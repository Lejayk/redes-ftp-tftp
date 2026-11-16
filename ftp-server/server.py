"""servidor ftp del grupo 1, montado con pyftpdlib."""

import logging

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

ROOT = "/srv/ftp"
PASSIVE_PORTS = range(30000, 30010)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[ftp-server] %(message)s")

    authorizer = DummyAuthorizer()
    # usuario de la demo: puede listar, descargar y subir
    authorizer.add_user("alumno", "redes2026", ROOT, perm="elradfmw")
    # anonymous solo puede leer
    authorizer.add_anonymous(ROOT, perm="elr")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Servidor FTP del Grupo 1 listo."
    handler.passive_ports = PASSIVE_PORTS
    # el default de 3 s tras una clave mala se siente eterno en una exposición
    handler.auth_failed_timeout = 1
    # una hora sin actividad antes de cortar la sesión de control
    handler.timeout = 3600

    server = FTPServer(("0.0.0.0", 21), handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
