"""captura cruda con un socket AF_PACKET: lo mismo que hace wireshark, sin wireshark."""

from __future__ import annotations

import logging
import socket
import threading

from .decoder import PacketDecoder
from .hub import Hub

ETH_P_ALL = 0x0003
MAX_FRAME = 65535

logger = logging.getLogger("client.sniffer")


class Sniffer:
    """lee cada trama que entra o sale de la tarjeta de red del cliente."""

    def __init__(self, interface: str, decoder: PacketDecoder, hub: Hub) -> None:
        self._interface = interface
        self._decoder = decoder
        self._hub = hub
        self._socket: socket.socket | None = None

    def start(self) -> None:
        # ETH_P_ALL pide todas las tramas, en las dos direcciones
        self._socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        self._socket.bind((self._interface, 0))
        threading.Thread(target=self._loop, name="sniffer", daemon=True).start()
        logger.info("capturando tramas en %s", self._interface)

    def _loop(self) -> None:
        while True:
            frame, _address = self._socket.recvfrom(MAX_FRAME)
            try:
                event = self._decoder.decode(frame)
            except Exception:
                logger.exception("no se pudo decodificar una trama de %d bytes", len(frame))
                continue
            if event is not None:
                self._hub.emit(event)
