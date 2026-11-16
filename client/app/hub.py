"""reparte los eventos en vivo a todos los navegadores conectados."""

from __future__ import annotations

import asyncio
import json
import time
from collections import deque

from fastapi import WebSocket

HISTORY_LIMIT = 3000


class Hub:
    """cola única de eventos: el sniffer y los clientes escriben, los websockets leen."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._history: deque[dict] = deque(maxlen=HISTORY_LIMIT)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._queue: asyncio.Queue[dict] | None = None

    def bind(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._queue = asyncio.Queue()

    def emit(self, event: dict, record: bool = True) -> None:
        """se puede llamar desde cualquier hilo: el sniffer vive fuera del event loop."""
        if self._loop is None:
            return
        event.setdefault("t", time.time())
        self._loop.call_soon_threadsafe(self._accept, event, record)

    def say(self, proto: str, text: str, tone: str = "info") -> None:
        self.emit({"type": "say", "proto": proto, "text": text, "tone": tone})

    def clear(self) -> None:
        self._history.clear()

    def _accept(self, event: dict, record: bool) -> None:
        if record:
            self._history.append(event)
        self._queue.put_nowait(event)

    async def run(self) -> None:
        while True:
            event = await self._queue.get()
            message = json.dumps(event, ensure_ascii=False)
            for client in list(self._clients):
                try:
                    await client.send_text(message)
                except Exception:
                    self._clients.discard(client)

    async def attach(self, websocket: WebSocket, state: dict) -> None:
        await websocket.accept()
        snapshot = list(self._history)
        self._clients.add(websocket)
        # quien recarga la página recupera todo lo que ya pasó
        await websocket.send_text(json.dumps({"type": "history", "events": snapshot}, ensure_ascii=False))
        await websocket.send_text(json.dumps(state, ensure_ascii=False))

    def detach(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)
