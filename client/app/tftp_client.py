"""cliente tftp escrito a mano sobre udp: rrq, wrq, data, ack y error, uno por uno."""

from __future__ import annotations

import asyncio
import socket
import struct

from .hub import Hub
from .pacer import Pacer

TFTP_PORT = 69
BLOCK_SIZE = 512
OP_RRQ, OP_WRQ, OP_DATA, OP_ACK, OP_ERROR = 1, 2, 3, 4, 5
# más largo que la espera del servidor (3 s), para que se vea primero su retransmisión
RECEIVE_TIMEOUT_SECONDS = 5.0
MAX_RETRIES = 4
MAX_PACKET = 4 + BLOCK_SIZE + 64


class TftpError(Exception):
    """problema que se le muestra tal cual a quien presenta."""


class TftpClient:
    def __init__(self, host: str, hub: Hub, pacer: Pacer) -> None:
        self.host = host
        self._hub = hub
        self._pacer = pacer

    def _say(self, text: str, tone: str = "info") -> None:
        self._hub.say("tftp", text, tone)

    # ---------- descarga ----------

    async def download(self, filename: str, lose_ack_of_block: int | None = None) -> bool:
        sock = self._open_socket()
        try:
            self._say(
                f"El cliente abre un socket UDP en el puerto {sock.getsockname()[1]}. "
                "No hay saludo previo: UDP no establece conexión, manda y listo."
            )
            request = self._request(OP_RRQ, filename)
            await self._pacer.gate("tftp", f"Enviar RRQ «{filename}» al puerto {TFTP_PORT}")
            await self._send(sock, request, (self.host, TFTP_PORT))
            last_packet, last_address = request, (self.host, TFTP_PORT)

            server: tuple[str, int] | None = None
            expected, content, ack_dropped = 1, bytearray(), False
            while True:
                packet, address = await self._receive(sock, last_packet, last_address)
                if server is None:
                    server = address
                elif address != server:
                    # un paquete de otro puerto no es de esta transferencia
                    await self._send(sock, self._error(5, "Unknown transfer ID"), address)
                    continue
                opcode = struct.unpack_from("!H", packet)[0]
                if opcode == OP_ERROR:
                    self._report_error(packet)
                    return False
                if opcode != OP_DATA:
                    continue

                block = struct.unpack_from("!H", packet, 2)[0]
                data = packet[4:]
                is_new = block == expected
                if is_new:
                    content += data
                    expected = (expected + 1) % 65536
                    if block == lose_ack_of_block and not ack_dropped and len(data) == BLOCK_SIZE:
                        ack_dropped = True
                        self._say(
                            f"Simulación: el ACK del bloque {block} «se pierde» (el cliente no lo manda). "
                            "El servidor se queda esperando y en 3 segundos va a reenviar el bloque.",
                            "warn",
                        )
                        continue
                else:
                    self._say(f"Llegó otra vez el bloque {block}: es la retransmisión. Se descarta y se vuelve a confirmar.", "warn")

                ack = struct.pack("!HH", OP_ACK, block)
                await self._pacer.gate("tftp", f"Enviar ACK del bloque {block}")
                await self._send(sock, ack, server)
                last_packet, last_address = ack, server
                if is_new and len(data) < BLOCK_SIZE:
                    self._say(
                        f"El bloque {block} trajo {len(data)} bytes, menos de 512: era el último. "
                        f"Archivo completo: {len(content)} bytes.",
                        "ok",
                    )
                    return True
        finally:
            sock.close()

    # ---------- subida ----------

    async def upload(self, filename: str, content: bytes) -> bool:
        sock = self._open_socket()
        try:
            self._say(f"El cliente abre un socket UDP en el puerto {sock.getsockname()[1]} para subir «{filename}».")
            request = self._request(OP_WRQ, filename)
            await self._pacer.gate("tftp", f"Enviar WRQ «{filename}» al puerto {TFTP_PORT}")
            await self._send(sock, request, (self.host, TFTP_PORT))

            server = await self._await_ack(sock, 0, request, (self.host, TFTP_PORT), None)
            if server is None:
                return False

            blocks = [content[offset : offset + BLOCK_SIZE] for offset in range(0, len(content), BLOCK_SIZE)]
            if len(content) % BLOCK_SIZE == 0:
                # un archivo múltiplo de 512 necesita un bloque vacío para marcar el final
                blocks.append(b"")
            for number, chunk in enumerate(blocks, start=1):
                block = number % 65536
                packet = struct.pack("!HH", OP_DATA, block) + chunk
                await self._pacer.gate("tftp", f"Enviar DATA bloque {block} ({len(chunk)} bytes)")
                await self._send(sock, packet, server)
                if await self._await_ack(sock, block, packet, server, server) is None:
                    return False
            self._say(f"Subida completa: {len(content)} bytes en {len(blocks)} bloque(s). Ya está en tftp-server/files.", "ok")
            return True
        finally:
            sock.close()

    async def _await_ack(
        self,
        sock: socket.socket,
        block: int,
        last_packet: bytes,
        last_address: tuple[str, int],
        server: tuple[str, int] | None,
    ) -> tuple[str, int] | None:
        """espera el ack de un bloque; devuelve la dirección (tid) del servidor o none si hubo error."""
        while True:
            packet, address = await self._receive(sock, last_packet, last_address)
            if server is not None and address != server:
                await self._send(sock, self._error(5, "Unknown transfer ID"), address)
                continue
            opcode = struct.unpack_from("!H", packet)[0]
            if opcode == OP_ERROR:
                self._report_error(packet)
                return None
            # un ack viejo repetido se ignora: reenviar por eso duplicaría todo el tráfico
            if opcode == OP_ACK and struct.unpack_from("!H", packet, 2)[0] == block:
                return address

    # ---------- utilidades ----------

    @staticmethod
    def _open_socket() -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.bind(("0.0.0.0", 0))
        return sock

    @staticmethod
    def _request(opcode: int, filename: str, mode: str = "octet") -> bytes:
        # opcode (2 bytes) + nombre + 0x00 + modo + 0x00
        return struct.pack("!H", opcode) + filename.encode("utf-8") + b"\0" + mode.encode("ascii") + b"\0"

    @staticmethod
    def _error(code: int, message: str) -> bytes:
        return struct.pack("!HH", OP_ERROR, code) + message.encode("ascii") + b"\0"

    @staticmethod
    async def _send(sock: socket.socket, packet: bytes, address: tuple[str, int]) -> None:
        await asyncio.get_running_loop().sock_sendto(sock, packet, address)

    async def _receive(
        self, sock: socket.socket, last_packet: bytes, last_address: tuple[str, int]
    ) -> tuple[bytes, tuple[str, int]]:
        """espera un paquete; si no llega a tiempo, retransmite el último que mandó el cliente."""
        loop = asyncio.get_running_loop()
        for _attempt in range(MAX_RETRIES + 1):
            try:
                return await asyncio.wait_for(loop.sock_recvfrom(sock, MAX_PACKET), RECEIVE_TIMEOUT_SECONDS)
            except TimeoutError:
                self._say(
                    f"Pasaron {RECEIVE_TIMEOUT_SECONDS:g} s sin respuesta: el cliente retransmite su último paquete.",
                    "warn",
                )
                await self._send(sock, last_packet, last_address)
        raise TftpError("El servidor dejó de responder. Transferencia abortada.")

    def _report_error(self, packet: bytes) -> None:
        code = struct.unpack_from("!H", packet, 2)[0]
        message = packet[4:].split(b"\0")[0].decode("utf-8", errors="replace")
        self._say(f"El servidor respondió ERROR {code}: «{message}». En TFTP un error corta la transferencia ahí mismo.", "error")
