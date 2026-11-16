"""cliente ftp escrito a mano sobre sockets: cada comando del protocolo viaja tal cual."""

from __future__ import annotations

import asyncio
import re

from .hub import Hub
from .pacer import Pacer

FTP_PORT = 21
TIMEOUT_SECONDS = 10
PASV_PATTERN = re.compile(r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)")
# estos comandos necesitan canal de datos: tienen su propio botón
DATA_COMMANDS = {"LIST", "NLST", "MLSD", "RETR", "STOR", "STOU", "APPE"}
ACTIVE_MODE_COMMANDS = {"PORT", "EPRT"}


class FtpError(Exception):
    """problema que se le muestra tal cual a quien presenta."""


class FtpClient:
    def __init__(self, host: str, hub: Hub, pacer: Pacer) -> None:
        self.host = host
        self._hub = hub
        self._pacer = pacer
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._pending_user: str | None = None
        self.user: str | None = None

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    def state(self) -> dict:
        return {"connected": self.connected, "user": self.user}

    def _say(self, text: str, tone: str = "info") -> None:
        self._hub.say("ftp", text, tone)

    # ---------- sesión ----------

    async def connect(self) -> None:
        if self.connected:
            raise FtpError("Ya hay una sesión abierta. Ciérrala con QUIT antes de reconectar.")
        await self._pacer.gate("ftp", f"Abrir conexión TCP con {self.host}:{FTP_PORT}")
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, FTP_PORT), TIMEOUT_SECONDS
            )
        except OSError as error:
            raise FtpError(f"No se pudo conectar con el servidor FTP: {error}") from error
        await self._read_reply()
        self._say("Conexión de control abierta. Fíjate que el servidor habla primero: saluda con un 220.", "ok")

    async def login(self, user: str, password: str) -> bool:
        code, _ = await self.send(f"USER {user}")
        if code == 331:
            code, _ = await self.send(f"PASS {password}")
        if code == 230:
            self.user = user
            self._say(
                f"Sesión iniciada como «{user}». La contraseña viajó en texto plano: ábrela en el inspector y se lee entera.",
                "warn",
            )
            return True
        self._say("El servidor rechazó el login. La conexión TCP sigue abierta: se puede reintentar con otra clave.", "error")
        return False

    async def quit(self) -> None:
        if not self.connected:
            raise FtpError("No hay ninguna sesión abierta.")
        await self.send("QUIT")
        await self.drop()
        self._say("Sesión cerrada: el servidor se despidió con 221 y se cerró la conexión TCP.", "ok")

    async def drop(self) -> None:
        """cierra la conexión de control sin despedirse, para limpiar tras un error."""
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
        self._reader = self._writer = None
        self.user = self._pending_user = None

    # ---------- transferencias ----------

    async def list_files(self) -> None:
        await self.send("TYPE A")
        reader, writer = await self._open_data_channel()
        code, _ = await self.send("LIST")
        if code >= 400:
            writer.close()
            return
        listing = await self._read_all(reader)
        writer.close()
        await self._read_reply()
        entries = [line for line in listing.decode("utf-8", errors="replace").splitlines() if line.strip()]
        self._say(f"El listado llegó por el canal de datos, no por el de control: {len(entries)} archivo(s).", "ok")

    async def download(self, filename: str) -> bool:
        await self.send("TYPE I")
        reader, writer = await self._open_data_channel()
        code, _ = await self.send(f"RETR {filename}")
        if code >= 400:
            writer.close()
            self._say(f"El servidor no encontró «{filename}» o no deja leerlo.", "error")
            return False
        content = await self._read_all(reader)
        writer.close()
        await self._read_reply()
        self._say(f"Descarga completa: {len(content)} bytes de «{filename}».", "ok")
        return True

    async def upload(self, filename: str, content: bytes) -> bool:
        await self.send("TYPE I")
        reader, writer = await self._open_data_channel()
        code, _ = await self.send(f"STOR {filename}")
        if code >= 400:
            writer.close()
            self._say(f"El servidor no aceptó la subida de «{filename}».", "error")
            return False
        writer.write(content)
        await writer.drain()
        # cerrar el canal de datos es la forma de decir «terminé de subir»
        writer.close()
        await writer.wait_closed()
        await self._read_reply()
        self._say(f"Subida completa: {len(content)} bytes. Ya está en la carpeta ftp-server/files.", "ok")
        return True

    async def raw(self, line: str) -> None:
        verb, _, argument = line.strip().partition(" ")
        verb = verb.upper()
        if verb in DATA_COMMANDS:
            raise FtpError(f"{verb} necesita un canal de datos: usa los botones de listar, descargar o subir.")
        if verb in ACTIVE_MODE_COMMANDS:
            raise FtpError("El modo activo no está en esta demo: el cliente usa modo pasivo (PASV).")
        if verb == "QUIT":
            await self.quit()
            return
        code, _ = await self.send(line.strip())
        # mantiene el estado si alguien hace el login a mano
        if verb == "USER":
            self._pending_user = argument.strip()
        elif verb == "PASS" and code == 230:
            self.user = self._pending_user or "manual"

    # ---------- protocolo ----------

    async def send(self, command: str) -> tuple[int, str]:
        if not self.connected:
            raise FtpError("Primero hay que conectarse: botón «Conectar».")
        await self._pacer.gate("ftp", f"Enviar «{command}»")
        self._writer.write(f"{command}\r\n".encode("utf-8"))
        await self._writer.drain()
        return await self._read_reply()

    async def _read_reply(self) -> tuple[int, str]:
        """lee una respuesta completa; las de varias líneas terminan con «código + espacio»."""
        first = await self._readline()
        lines = [first]
        code = first[:3]
        if len(first) > 3 and first[3] == "-":
            while True:
                line = await self._readline()
                lines.append(line)
                if line.startswith(f"{code} "):
                    break
        if not code.isdigit():
            raise FtpError(f"Respuesta inesperada del servidor: {first}")
        return int(code), "\n".join(lines)

    async def _readline(self) -> str:
        raw = await asyncio.wait_for(self._reader.readline(), TIMEOUT_SECONDS)
        if not raw:
            await self.drop()
            raise FtpError("El servidor cerró la conexión de control.")
        return raw.decode("utf-8", errors="replace").rstrip("\r\n")

    async def _open_data_channel(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        code, text = await self.send("PASV")
        match = PASV_PATTERN.search(text)
        if code != 227 or not match:
            raise FtpError(f"El servidor no aceptó el modo pasivo: {text}")
        h1, h2, h3, h4, p1, p2 = (int(number) for number in match.groups())
        address, port = f"{h1}.{h2}.{h3}.{h4}", p1 * 256 + p2
        self._say(f"Del 227 sale adónde conectarse para los datos: IP {address}, puerto {p1} × 256 + {p2} = {port}.")
        await self._pacer.gate("ftp", f"Abrir la conexión de datos con {address}:{port}")
        try:
            return await asyncio.wait_for(asyncio.open_connection(address, port), TIMEOUT_SECONDS)
        except OSError as error:
            raise FtpError(f"No se pudo abrir el canal de datos: {error}") from error

    @staticmethod
    async def _read_all(reader: asyncio.StreamReader) -> bytes:
        # el servidor cierra el canal de datos cuando termina: se lee hasta el EOF
        return await asyncio.wait_for(reader.read(), TIMEOUT_SECONDS)
