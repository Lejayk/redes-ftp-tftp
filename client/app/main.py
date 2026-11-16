"""panel en vivo de ftp y tftp: el navegador maneja al cliente y ve cada paquete del cable."""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .decoder import PacketDecoder
from .ftp_client import FtpClient, FtpError
from .hub import Hub
from .pacer import Pacer
from .samples import build_upload
from .sniffer import Sniffer
from .tftp_client import TftpClient, TftpError

logging.basicConfig(level=logging.INFO, format="[client] %(message)s")
# la imagen slim no trae /etc/mime.types: sin esto la fuente sale como text/plain
mimetypes.add_type("font/woff2", ".woff2")
logger = logging.getLogger("client")

STATIC_DIR = Path(__file__).parent / "static"
CLIENT_IP = os.environ.get("CLIENT_IP", "10.10.10.10")
FTP_HOST = os.environ.get("FTP_HOST", "10.10.10.21")
TFTP_HOST = os.environ.get("TFTP_HOST", "10.10.10.69")
CAPTURE_IFACE = os.environ.get("CAPTURE_IFACE", "eth0")
DEMO_USER, DEMO_PASSWORD, DEMO_FILE = "alumno", "redes2026", "config-router.txt"
# deja que el sniffer entregue los últimos paquetes antes de cerrar la operación
END_GRACE_SECONDS = 0.4
FILENAME_PATTERN = r"^[\w.\- ]+$"

hub = Hub()
pacer = Pacer(hub)
ftp = FtpClient(FTP_HOST, hub, pacer)
tftp = TftpClient(TFTP_HOST, hub, pacer)
capture = {"ok": False, "error": None}


class Operations:
    """corre una operación a la vez para que el diagrama no mezcle dos conversaciones."""

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None

    @property
    def busy(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self, proto: str, title: str, work: Callable[[], Awaitable[object]]) -> None:
        if self.busy:
            raise HTTPException(409, "Hay una operación en curso. Espera a que termine o cancélala.")
        self._task = asyncio.create_task(self._run(proto, title, work))

    def cancel(self) -> bool:
        if not self.busy or self._task.cancelling():
            return False
        self._task.cancel()
        return True

    async def _run(self, proto: str, title: str, work: Callable[[], Awaitable[object]]) -> None:
        hub.emit({"type": "op", "phase": "start", "proto": proto, "title": title})
        publish_state()
        ok = False
        try:
            ok = (await work()) is not False
        except (FtpError, TftpError) as error:
            hub.say(proto, str(error), "error")
        except asyncio.CancelledError:
            hub.say(proto, "Operación cancelada.", "warn")
            if proto == "ftp":
                await ftp.drop()
        except Exception as error:
            logger.exception("falló la operación «%s»", title)
            hub.say(proto, f"Error inesperado: {error or type(error).__name__}", "error")
        finally:
            await asyncio.sleep(END_GRACE_SECONDS)
            hub.emit({"type": "op", "phase": "end", "proto": proto, "title": title, "ok": ok})
            self._task = None
            publish_state()


operations = Operations()


def state_event() -> dict:
    return {
        "type": "state",
        "busy": operations.busy,
        "ftp": ftp.state(),
        "pacing": pacer.snapshot(),
        "hosts": {"client": CLIENT_IP, "ftp": FTP_HOST, "tftp": TFTP_HOST},
        "capture": capture,
    }


def publish_state() -> None:
    hub.emit(state_event(), record=False)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    hub.bind(asyncio.get_running_loop())
    broadcaster = asyncio.create_task(hub.run())
    try:
        Sniffer(CAPTURE_IFACE, PacketDecoder(CLIENT_IP, FTP_HOST, TFTP_HOST), hub).start()
        capture["ok"] = True
    except OSError as error:
        logger.error("la captura de paquetes no arrancó: %s", error)
        capture["error"] = str(error)
    yield
    broadcaster.cancel()


app = FastAPI(title="FTP y TFTP en vivo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------- modelos de entrada ----------


class LoginRequest(BaseModel):
    user: str = Field(min_length=1, max_length=64, pattern=r"^\S+$")
    password: str = Field(max_length=128, pattern=r"^[^\r\n]*$")


class FileRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=120, pattern=FILENAME_PATTERN)


class UploadRequest(FileRequest):
    size: Literal["small", "medium", "exact"] = "small"


class RawRequest(BaseModel):
    command: str = Field(min_length=1, max_length=200, pattern=r"^[^\r\n]+$")


class TftpDownloadRequest(FileRequest):
    lose_ack: bool = False


class PacingRequest(BaseModel):
    mode: Literal["auto", "step"]
    speed: Literal["fast", "normal", "slow"]


def require_ftp_session(logged_in: bool = False) -> None:
    if not ftp.connected:
        raise HTTPException(400, "Primero hay que conectarse: botón «Conectar».")
    if logged_in and not ftp.user:
        raise HTTPException(400, "Falta iniciar sesión: botón «Iniciar sesión».")


# ---------- página y eventos ----------


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-store"})


@app.websocket("/ws")
async def live(websocket: WebSocket) -> None:
    await hub.attach(websocket, state_event())
    try:
        while True:
            # el navegador no manda nada: esto solo detecta cuándo se va
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        hub.detach(websocket)


@app.get("/api/state")
async def current_state() -> dict:
    return state_event()


# ---------- ftp ----------


@app.post("/api/ftp/connect")
async def ftp_connect() -> dict:
    if ftp.connected:
        raise HTTPException(400, "Ya hay una sesión abierta. Ciérrala con QUIT antes de reconectar.")
    operations.start("ftp", "Conectar al servidor FTP", ftp.connect)
    return {"ok": True}


@app.post("/api/ftp/login")
async def ftp_login(body: LoginRequest) -> dict:
    require_ftp_session()
    operations.start("ftp", f"Iniciar sesión como «{body.user}»", lambda: ftp.login(body.user, body.password))
    return {"ok": True}


@app.post("/api/ftp/list")
async def ftp_list() -> dict:
    require_ftp_session(logged_in=True)
    operations.start("ftp", "Listar archivos (LIST)", ftp.list_files)
    return {"ok": True}


@app.post("/api/ftp/download")
async def ftp_download(body: FileRequest) -> dict:
    require_ftp_session(logged_in=True)
    operations.start("ftp", f"Descargar «{body.filename}» (RETR)", lambda: ftp.download(body.filename))
    return {"ok": True}


@app.post("/api/ftp/upload")
async def ftp_upload(body: UploadRequest) -> dict:
    require_ftp_session(logged_in=True)
    content = build_upload(body.size)
    operations.start("ftp", f"Subir «{body.filename}» (STOR)", lambda: ftp.upload(body.filename, content))
    return {"ok": True}


@app.post("/api/ftp/raw")
async def ftp_raw(body: RawRequest) -> dict:
    require_ftp_session()
    operations.start("ftp", f"Comando manual «{body.command.strip()}»", lambda: ftp.raw(body.command))
    return {"ok": True}


@app.post("/api/ftp/quit")
async def ftp_quit() -> dict:
    require_ftp_session()
    operations.start("ftp", "Cerrar sesión (QUIT)", ftp.quit)
    return {"ok": True}


@app.post("/api/ftp/demo")
async def ftp_demo() -> dict:
    async def run_demo() -> bool:
        if ftp.connected:
            await ftp.quit()
        await ftp.connect()
        if not await ftp.login(DEMO_USER, DEMO_PASSWORD):
            return False
        await ftp.list_files()
        downloaded = await ftp.download(DEMO_FILE)
        await ftp.quit()
        return downloaded

    operations.start("ftp", "Demo completa: conectar, login, listar, descargar y salir", run_demo)
    return {"ok": True}


# ---------- tftp ----------


@app.post("/api/tftp/download")
async def tftp_download(body: TftpDownloadRequest) -> dict:
    title = f"Descargar «{body.filename}» (RRQ)" + (" con un ACK perdido" if body.lose_ack else "")
    lose = 2 if body.lose_ack else None
    operations.start("tftp", title, lambda: tftp.download(body.filename, lose_ack_of_block=lose))
    return {"ok": True}


@app.post("/api/tftp/upload")
async def tftp_upload(body: UploadRequest) -> dict:
    content = build_upload(body.size)
    operations.start("tftp", f"Subir «{body.filename}» (WRQ)", lambda: tftp.upload(body.filename, content))
    return {"ok": True}


# ---------- ritmo y control ----------


@app.post("/api/pacing")
async def set_pacing(body: PacingRequest) -> dict:
    pacer.configure(body.mode, body.speed)
    publish_state()
    return {"ok": True}


@app.post("/api/next")
async def next_step() -> dict:
    pacer.release()
    return {"ok": True}


@app.post("/api/cancel")
async def cancel() -> dict:
    return {"ok": operations.cancel()}


@app.post("/api/clear")
async def clear() -> dict:
    hub.clear()
    hub.emit({"type": "clear"}, record=False)
    return {"ok": True}
