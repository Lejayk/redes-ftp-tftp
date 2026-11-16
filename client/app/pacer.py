"""controla el ritmo del cliente: automático con pausas, o paso a paso esperando un clic."""

from __future__ import annotations

import asyncio

from .hub import Hub

DELAYS = {"fast": 0.15, "normal": 0.7, "slow": 1.5}


class Pacer:
    def __init__(self, hub: Hub) -> None:
        self._hub = hub
        self._go = asyncio.Event()
        self.mode = "auto"
        self.speed = "normal"

    def snapshot(self) -> dict:
        return {"mode": self.mode, "speed": self.speed}

    def configure(self, mode: str, speed: str) -> None:
        self.mode, self.speed = mode, speed
        if mode == "auto":
            # destraba a quien esté esperando un clic
            self._go.set()

    def release(self) -> None:
        self._go.set()

    async def gate(self, proto: str, label: str) -> None:
        """pausa antes de cada paso del protocolo para que se pueda seguir a ojo."""
        if self.mode != "step":
            await asyncio.sleep(DELAYS[self.speed])
            return
        self._go.clear()
        self._hub.emit({"type": "waiting", "proto": proto, "label": label})
        try:
            await self._go.wait()
        finally:
            self._hub.emit({"type": "resumed", "proto": proto})
