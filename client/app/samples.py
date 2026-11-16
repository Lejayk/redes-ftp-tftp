"""contenido de prueba para las subidas, con tamaños elegidos para mostrar casos del protocolo."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# venezuela no usa horario de verano: utc-4 todo el año
LOCAL_TIME = timezone(timedelta(hours=-4))
SIZES = {"medium": 1300, "exact": 1024}
FILLER = "Linea de relleno para llegar al tamano exacto del ejemplo. 0123456789\n"


def build_upload(size: str) -> bytes:
    header = f"Archivo subido por el cliente del Grupo 1 a las {datetime.now(LOCAL_TIME):%H:%M:%S}.\n"
    if size == "small":
        return header.encode("ascii")
    target = SIZES[size]
    text = header + FILLER * (target // len(FILLER) + 1)
    return text.encode("ascii")[:target]
