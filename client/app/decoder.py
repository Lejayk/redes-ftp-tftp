"""convierte tramas ethernet crudas en capas legibles y marca qué bytes ocupa cada campo."""

from __future__ import annotations

import re
import socket
import struct

ETH_HEADER = 14
FTP_CONTROL_PORT = 21
TFTP_PORT = 69
TFTP_BLOCK = 512
LABEL_LIMIT = 60
SEQ_SPACE = 2**32

FLAG_FIN, FLAG_SYN, FLAG_RST, FLAG_PSH, FLAG_ACK, FLAG_URG = 0x01, 0x02, 0x04, 0x08, 0x10, 0x20
TCP_FLAG_NAMES = (
    (FLAG_SYN, "SYN"),
    (FLAG_FIN, "FIN"),
    (FLAG_RST, "RST"),
    (FLAG_PSH, "PSH"),
    (FLAG_ACK, "ACK"),
    (FLAG_URG, "URG"),
)

OP_RRQ, OP_WRQ, OP_DATA, OP_ACK, OP_ERROR, OP_OACK = 1, 2, 3, 4, 5, 6
TFTP_OPCODES = {OP_RRQ: "RRQ", OP_WRQ: "WRQ", OP_DATA: "DATA", OP_ACK: "ACK", OP_ERROR: "ERROR", OP_OACK: "OACK"}

PASV_PATTERN = re.compile(r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)")

FTP_COMMANDS = {
    "USER": "El cliente dice con qué usuario quiere entrar.",
    "PASS": "El cliente manda la contraseña en texto plano: cualquiera que capture el tráfico la puede leer.",
    "ACCT": "Envía información de la cuenta.",
    "SYST": "Pregunta qué sistema operativo tiene el servidor.",
    "PWD": "Pregunta en qué carpeta está parado.",
    "CWD": "Pide cambiar de carpeta.",
    "CDUP": "Pide subir a la carpeta superior.",
    "TYPE": "Elige el modo de transferencia: «A» es texto (ASCII) e «I» es binario, byte por byte sin tocar.",
    "PASV": "Pide modo pasivo: que el servidor abra un puerto para los datos y le diga cuál.",
    "EPSV": "Modo pasivo extendido: como PASV, pero el servidor responde solo con el puerto.",
    "PORT": "Modo activo: el cliente le dice al servidor a qué IP y puerto conectarse para los datos.",
    "LIST": "Pide el listado de archivos. La respuesta no vuelve por aquí: viaja por el canal de datos.",
    "NLST": "Pide solo los nombres de los archivos, por el canal de datos.",
    "RETR": "Pide descargar un archivo. El contenido viaja por el canal de datos.",
    "STOR": "Avisa que va a subir un archivo por el canal de datos.",
    "DELE": "Pide borrar un archivo.",
    "MKD": "Pide crear una carpeta.",
    "RMD": "Pide borrar una carpeta.",
    "SIZE": "Pregunta cuánto pesa un archivo.",
    "MDTM": "Pregunta la fecha de modificación de un archivo.",
    "FEAT": "Pregunta qué extensiones del protocolo soporta el servidor.",
    "HELP": "Pide la lista de comandos que entiende el servidor.",
    "NOOP": "No hace nada: sirve para mantener viva la sesión.",
    "STAT": "Pide el estado de la sesión.",
    "QUIT": "Cierra la sesión.",
}

FTP_REPLY_FAMILIES = {
    "1": "1xx · respuesta preliminar: todavía falta otra",
    "2": "2xx · listo: la orden se completó",
    "3": "3xx · va bien, pero falta información",
    "4": "4xx · error temporal: se puede reintentar",
    "5": "5xx · error permanente",
}

FTP_REPLIES = {
    "125": "El canal de datos ya estaba abierto: empieza la transferencia.",
    "150": "El servidor abre el canal de datos y empieza a transferir.",
    "200": "Orden aceptada.",
    "211": "Estado del sistema o lista de extensiones.",
    "213": "Respuesta con el dato pedido (tamaño o fecha).",
    "214": "Mensaje de ayuda.",
    "215": "Tipo de sistema del servidor.",
    "220": "Bienvenida: en FTP el servidor habla primero y avisa que está listo.",
    "221": "Despedida: el servidor va a cerrar la conexión de control.",
    "226": "Transferencia completa: el servidor cierra el canal de datos.",
    "227": "Modo pasivo. Los seis números son la IP (los cuatro primeros) y el puerto, que se calcula p1 × 256 + p2.",
    "230": "Login correcto: la sesión está abierta.",
    "250": "Acción sobre el archivo completada.",
    "257": "Ruta de la carpeta actual.",
    "331": "Usuario aceptado: ahora falta la contraseña.",
    "421": "El servicio se cierra: se acabó el tiempo o el servidor se apaga.",
    "425": "No se pudo abrir el canal de datos.",
    "426": "Se cortó la transferencia.",
    "500": "Comando desconocido.",
    "501": "Error en los argumentos del comando.",
    "502": "Comando no implementado.",
    "503": "Comandos en mal orden (por ejemplo, PASS sin USER).",
    "530": "Login incorrecto, o hace falta iniciar sesión primero.",
    "550": "No se pudo: el archivo no existe o no hay permiso.",
}

TFTP_ERRORS = {
    0: "Error sin código específico; el texto lo explica.",
    1: "Archivo no encontrado.",
    2: "Acceso denegado.",
    3: "Disco lleno.",
    4: "Operación TFTP ilegal.",
    5: "TID desconocido: el paquete llegó a un puerto que no es de esta transferencia.",
    6: "El archivo ya existe.",
    7: "Usuario desconocido.",
}


def _field(label: str, value: object, start: int, end: int) -> dict:
    return {"label": label, "value": str(value), "start": start, "end": end}


def _layer(key: str, name: str, start: int, end: int, fields: list[dict]) -> dict:
    return {"key": key, "name": name, "start": start, "end": end, "fields": fields}


def _mac(raw: bytes) -> str:
    return ":".join(f"{byte:02x}" for byte in raw)


def _clip(text: str, limit: int = LABEL_LIMIT) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _preview(data: bytes, limit: int = 64) -> str:
    text = data[:limit].decode("utf-8", errors="replace")
    clean = "".join(char if char.isprintable() else " " for char in text)
    # colapsa saltos de línea y espacios repetidos
    return " ".join(clean.split())


def _ports(direction: str, client_port: int, server_port: int) -> str:
    return f"{client_port} → {server_port}" if direction == "out" else f"{server_port} → {client_port}"


class PacketDecoder:
    """guarda el estado mínimo para contar la historia: saludos tcp, números relativos y tids de tftp."""

    def __init__(self, client_ip: str, ftp_ip: str, tftp_ip: str) -> None:
        self.client_ip = client_ip
        self.ftp_ip = ftp_ip
        self.tftp_ip = tftp_ip
        self._initial_seq: dict[tuple, int] = {}
        self._handshake: dict[frozenset, int] = {}
        self._tftp_seen: set[tuple] = set()
        self._tftp_transfers: set[tuple] = set()
        self._count = 0

    def decode(self, frame: bytes) -> dict | None:
        if len(frame) < ETH_HEADER + 20 or frame[12:14] != b"\x08\x00":
            return None
        ip = ETH_HEADER
        header_len = (frame[ip] & 0x0F) * 4
        total_len = struct.unpack_from("!H", frame, ip + 2)[0]
        protocol = frame[ip + 9]
        src = socket.inet_ntoa(frame[ip + 12 : ip + 16])
        dst = socket.inet_ntoa(frame[ip + 16 : ip + 20])
        if self.client_ip not in (src, dst):
            return None
        peer = dst if src == self.client_ip else src
        if total_len:
            # quita el relleno que ethernet agrega a las tramas muy pequeñas
            frame = frame[: ip + total_len]
        direction = "out" if src == self.client_ip else "in"
        transport = ip + header_len

        if protocol == 6 and peer == self.ftp_ip:
            story = self._tcp(frame, transport, src, dst, direction)
        elif protocol == 17 and peer == self.tftp_ip:
            story = self._udp(frame, transport, direction)
        else:
            return None
        if story is None:
            return None

        self._count += 1
        layers = [self._ethernet(frame), self._ipv4(frame, header_len, total_len, protocol, src, dst)]
        layers.extend(story.pop("layers"))
        return {
            "type": "packet",
            "id": self._count,
            "dir": direction,
            "client": f"{self.client_ip}:{story['client_port']}",
            "server": f"{peer}:{story['server_port']}",
            "frame_len": len(frame),
            "layers": layers,
            "hex": frame.hex(),
            **story,
        }

    # ---------- capas de abajo ----------

    @staticmethod
    def _ethernet(frame: bytes) -> dict:
        return _layer(
            "eth",
            "Ethernet II",
            0,
            ETH_HEADER,
            [
                _field("MAC destino", _mac(frame[0:6]), 0, 6),
                _field("MAC origen", _mac(frame[6:12]), 6, 12),
                _field("Tipo", "0x0800 · lo que sigue es IPv4", 12, 14),
            ],
        )

    @staticmethod
    def _ipv4(frame: bytes, header_len: int, total_len: int, protocol: int, src: str, dst: str) -> dict:
        start = ETH_HEADER
        name = {6: "TCP", 17: "UDP"}.get(protocol, str(protocol))
        ident, _, ttl, _, checksum = struct.unpack_from("!HHBBH", frame, start + 4)
        return _layer(
            "ip",
            "IPv4",
            start,
            start + header_len,
            [
                _field("Versión y largo de cabecera", f"versión 4 · {header_len} bytes", start, start + 1),
                _field("Largo total", f"{total_len} bytes", start + 2, start + 4),
                _field("Identificación", f"0x{ident:04x}", start + 4, start + 6),
                _field("TTL", f"{ttl} saltos como máximo", start + 8, start + 9),
                _field("Protocolo", f"{protocol} · {name}", start + 9, start + 10),
                _field("Checksum", f"0x{checksum:04x}", start + 10, start + 12),
                _field("IP origen", src, start + 12, start + 16),
                _field("IP destino", dst, start + 16, start + 20),
            ],
        )

    # ---------- tcp y ftp ----------

    def _tcp(self, frame: bytes, start: int, src: str, dst: str, direction: str) -> dict:
        sport, dport, seq, ack, offset_flags, window, checksum, urgent = struct.unpack_from("!HHIIHHHH", frame, start)
        header_len = (offset_flags >> 12) * 4
        flags = offset_flags & 0x3F
        payload_start = start + header_len
        payload = frame[payload_start:]
        client_port, server_port = (sport, dport) if direction == "out" else (dport, sport)
        channel = "ctrl" if server_port == FTP_CONTROL_PORT else "data"

        key, reverse = (src, sport, dst, dport), (dst, dport, src, sport)
        if flags & FLAG_SYN:
            self._initial_seq[key] = seq
        relative_seq = (seq - self._initial_seq[key]) % SEQ_SPACE if key in self._initial_seq else seq
        has_ack = bool(flags & FLAG_ACK)
        relative_ack = (ack - self._initial_seq[reverse]) % SEQ_SPACE if has_ack and reverse in self._initial_seq else ack
        flags_text = ", ".join(name for bit, name in TCP_FLAG_NAMES if flags & bit) or "ninguna"

        fields = [
            _field("Puerto origen", sport, start, start + 2),
            _field("Puerto destino", dport, start + 2, start + 4),
            _field("Nº de secuencia", f"{relative_seq} relativo · {seq} real", start + 4, start + 8),
            _field("Nº de acuse", f"{relative_ack} relativo" if has_ack else "sin uso (no hay ACK)", start + 8, start + 12),
            _field("Largo de cabecera y flags", f"{header_len} bytes · {flags_text}", start + 12, start + 14),
            _field("Ventana", f"{window} bytes", start + 14, start + 16),
            _field("Checksum", f"0x{checksum:04x}", start + 16, start + 18),
            _field("Puntero urgente", urgent, start + 18, start + 20),
        ]
        if header_len > 20:
            fields.append(_field("Opciones", f"{header_len - 20} bytes (MSS, escala de ventana, marcas de tiempo)", start + 20, payload_start))

        connection = frozenset({(src, sport), (dst, dport)})
        story = self._tcp_story(flags, payload, payload_start, direction, channel, server_port, relative_ack, connection)
        story.setdefault("file_bytes", 0)
        story["layers"] = [_layer("tcp", "TCP", start, payload_start, fields), *story.get("layers", [])]
        story["meta"] = f"TCP · {flags_text} · {len(payload)} B · {_ports(direction, client_port, server_port)}"
        return {
            "proto": "ftp",
            "channel": channel,
            "transport": "TCP",
            "client_port": client_port,
            "server_port": server_port,
            "payload_len": len(payload),
            **story,
        }

    def _tcp_story(
        self,
        flags: int,
        payload: bytes,
        payload_start: int,
        direction: str,
        channel: str,
        server_port: int,
        relative_ack: int,
        connection: frozenset,
    ) -> dict:
        stage = self._handshake.get(connection, 0)
        where = "de control (puerto 21)" if channel == "ctrl" else f"de datos (puerto {server_port})"
        who = "El cliente" if direction == "out" else "El servidor"

        if flags & FLAG_SYN and not flags & FLAG_ACK:
            self._handshake[connection] = 1
            return {"kind": "handshake", "label": "SYN", "explain": f"Saludo de tres vías, paso 1 de 3: el cliente pide abrir la conexión {where}."}
        if flags & FLAG_SYN:
            self._handshake[connection] = 2
            return {"kind": "handshake", "label": "SYN, ACK", "explain": "Paso 2 de 3: el servidor acepta la conexión y devuelve el saludo."}
        if flags & FLAG_RST:
            return {"kind": "rst", "label": "RST", "explain": f"{who} corta la conexión {where} de golpe, sin despedida."}
        if payload:
            story = (
                self._ftp_control(payload, payload_start, direction)
                if channel == "ctrl"
                else self._ftp_data(payload, payload_start, server_port)
            )
            if flags & FLAG_FIN:
                story["label"] += " + FIN"
                story["explain"] += " En el mismo paquete avisa que cierra la conexión."
            return story
        if flags & FLAG_FIN:
            label = "FIN, ACK" if flags & FLAG_ACK else "FIN"
            return {"kind": "fin", "label": label, "explain": f"{who} avisa que terminó: cierra su lado de la conexión {where}."}
        if stage == 2 and direction == "out":
            self._handshake[connection] = 3
            return {"kind": "handshake", "label": "ACK", "explain": "Paso 3 de 3: conexión establecida. Recién ahora pueden viajar datos."}
        return {
            "kind": "ack",
            "label": "ACK",
            "explain": f"Acuse de recibo de TCP: «recibí todo hasta el byte {relative_ack}». Es trabajo extra que UDP no hace.",
        }

    def _ftp_control(self, payload: bytes, start: int, direction: str) -> dict:
        first, _, rest = payload.partition(b"\r\n")
        text = first.decode("utf-8", errors="replace")
        fields: list[dict] = []

        secret = False
        if direction == "out":
            verb_raw, _, argument_raw = first.partition(b" ")
            verb = verb_raw.decode("utf-8", errors="replace").upper()
            secret = verb == "PASS"
            fields.append(_field("Comando", verb, start, start + len(verb_raw)))
            if argument_raw:
                argument_start = start + len(verb_raw) + 1
                argument = _field(
                    "Contraseña en texto plano" if secret else "Argumento",
                    argument_raw.decode("utf-8", errors="replace"),
                    argument_start,
                    argument_start + len(argument_raw),
                )
                # la contraseña se marca en el pizarrón y en el volcado de bytes
                argument["emphasis"] = secret
                fields.append(argument)
            explain = FTP_COMMANDS.get(verb, "Comando del protocolo FTP.")
        else:
            code = text[:3]
            fields.append(_field("Familia del código", FTP_REPLY_FAMILIES.get(code[:1], "desconocida"), start, start + 1))
            fields.append(_field("Código", code, start, start + 3))
            if len(first) > 4:
                fields.append(_field("Texto", text[4:], start + 4, start + len(first)))
            explain = FTP_REPLIES.get(code) or FTP_REPLY_FAMILIES.get(code[:1], "Respuesta del servidor FTP.")
            if code == "227":
                explain += self._passive_math(text)

        line_end = start + len(first)
        if payload[len(first) : len(first) + 2] == b"\r\n":
            fields.append(_field("Fin de línea", "CR LF · 0x0d 0x0a", line_end, line_end + 2))
        extra_lines = rest.count(b"\r\n")
        if extra_lines:
            fields.append(_field("Líneas siguientes", f"{extra_lines} más", line_end + 2, start + len(payload)))

        layer = _layer("app", "FTP · canal de control", start, start + len(payload), fields)
        return {"kind": "app", "label": _clip(text), "explain": explain, "layers": [layer], "secret": secret}

    @staticmethod
    def _passive_math(text: str) -> str:
        match = PASV_PATTERN.search(text)
        if not match:
            return ""
        h1, h2, h3, h4, p1, p2 = (int(number) for number in match.groups())
        return f" Aquí: IP {h1}.{h2}.{h3}.{h4} y puerto {p1} × 256 + {p2} = {p1 * 256 + p2}."

    @staticmethod
    def _ftp_data(payload: bytes, start: int, server_port: int) -> dict:
        preview = _preview(payload)
        fields = [_field("Contenido", f"{len(payload)} bytes · «{_clip(preview, 40)}»", start, start + len(payload))]
        layer = _layer("app", "FTP · canal de datos", start, start + len(payload), fields)
        return {
            "kind": "data",
            "label": f"Datos · {len(payload)} B",
            "explain": f"Contenido real viajando por el canal de datos (puerto {server_port}), separado de los comandos: «{_clip(preview, 50)}».",
            "file_bytes": len(payload),
            "layers": [layer],
        }

    # ---------- udp y tftp ----------

    def _udp(self, frame: bytes, start: int, direction: str) -> dict | None:
        sport, dport, length, checksum = struct.unpack_from("!HHHH", frame, start)
        payload_start = start + 8
        payload = frame[payload_start : start + length]
        if len(payload) < 2:
            return None
        client_port, server_port = (sport, dport) if direction == "out" else (dport, sport)
        udp_layer = _layer(
            "udp",
            "UDP",
            start,
            payload_start,
            [
                _field("Puerto origen", sport, start, start + 2),
                _field("Puerto destino", dport, start + 2, start + 4),
                _field("Largo", f"{length} bytes (cabecera + datos)", start + 4, start + 6),
                _field("Checksum", f"0x{checksum:04x}", start + 6, start + 8),
            ],
        )
        story = self._tftp(payload, payload_start, direction, client_port, server_port)
        tftp_layer = story.pop("layer")
        return {
            "proto": "tftp",
            "channel": "tftp",
            "transport": "UDP",
            "client_port": client_port,
            "server_port": server_port,
            "payload_len": len(payload),
            "meta": f"UDP · {len(payload)} B · {_ports(direction, client_port, server_port)}",
            "layers": [udp_layer, tftp_layer],
            **story,
        }

    def _tftp(self, payload: bytes, start: int, direction: str, client_port: int, server_port: int) -> dict:
        opcode = struct.unpack_from("!H", payload)[0]
        name = TFTP_OPCODES.get(opcode, f"opcode {opcode}")
        end = start + len(payload)
        fields = [_field("Opcode", f"{opcode} · {name}", start, start + 2)]
        file_bytes = 0
        block: int | None = None

        if opcode in (OP_RRQ, OP_WRQ):
            parts = payload[2:].split(b"\0")
            filename_raw = parts[0]
            mode_raw = parts[1] if len(parts) > 1 else b""
            name_end = start + 2 + len(filename_raw)
            mode_end = name_end + 1 + len(mode_raw)
            filename = filename_raw.decode("utf-8", errors="replace")
            mode = mode_raw.decode("utf-8", errors="replace")
            fields += [
                _field("Nombre de archivo", filename, start + 2, name_end),
                _field("Separador", "0x00", name_end, name_end + 1),
                _field("Modo", f"{mode} · binario, sin conversiones" if mode == "octet" else mode, name_end + 1, mode_end),
                _field("Separador", "0x00", mode_end, mode_end + 1),
            ]
            kind = "request"
            label = _clip(f"{name} «{filename}» · {mode}")
            if opcode == OP_RRQ:
                explain = "Read Request: el cliente pide leer (descargar) un archivo."
            else:
                explain = "Write Request: el cliente pide escribir (subir) un archivo."
            explain += " Va al puerto 69, el único que el servidor escucha. No hay usuario ni contraseña: todo cabe en un paquete."
        elif opcode == OP_DATA:
            block = struct.unpack_from("!H", payload, 2)[0]
            data = payload[4:]
            file_bytes = len(data)
            content = f"{len(data)} bytes · «{_clip(_preview(data), 36)}»" if data else "0 bytes (vacío)"
            fields += [_field("Nº de bloque", block, start + 2, start + 4), _field("Datos", content, start + 4, end)]
            kind = "tdata"
            label = f"DATA bloque {block} · {len(data)} B"
            if len(data) == TFTP_BLOCK:
                explain = f"Bloque {block} lleno: 512 bytes. Quien envía no manda el siguiente hasta recibir su ACK (stop-and-wait)."
            elif not data:
                explain = "Bloque vacío. El archivo medía un múltiplo exacto de 512, así que hace falta un bloque de 0 bytes para avisar que terminó."
            else:
                explain = f"Bloque {block} con {len(data)} bytes, menos de 512: así se sabe que es el último. TFTP no tiene otro aviso de fin."
        elif opcode == OP_ACK:
            block = struct.unpack_from("!H", payload, 2)[0]
            fields.append(_field("Nº de bloque", block, start + 2, start + 4))
            kind = "tack"
            label = f"ACK bloque {block}"
            if block == 0:
                explain = "ACK 0: el servidor acepta la escritura y el cliente ya puede mandar el bloque 1."
            else:
                explain = f"Confirma que llegó el bloque {block}. Recién ahora se manda el siguiente."
        elif opcode == OP_ERROR:
            code = struct.unpack_from("!H", payload, 2)[0]
            message_raw = payload[4:].split(b"\0")[0]
            message = message_raw.decode("utf-8", errors="replace")
            message_end = start + 4 + len(message_raw)
            fields += [
                _field("Código de error", f"{code} · {TFTP_ERRORS.get(code, 'desconocido')}", start + 2, start + 4),
                _field("Mensaje", message, start + 4, message_end),
            ]
            if end > message_end:
                fields.append(_field("Separador", "0x00", message_end, message_end + 1))
            kind = "terror"
            label = _clip(f"ERROR {code}: {message}")
            explain = f"{TFTP_ERRORS.get(code, 'Error.')} En TFTP un error termina la transferencia en el acto."
        else:
            kind = "request"
            label = name
            explain = "Paquete TFTP."

        if block is not None:
            seen_key = (direction, client_port, server_port, opcode, block)
            if seen_key in self._tftp_seen:
                kind = "retrans"
                label += " (otra vez)"
                file_bytes = 0
                if opcode == OP_ACK:
                    explain = f"ACK repetido: confirma de nuevo el bloque {block}, porque ese bloque llegó dos veces."
                else:
                    explain = (
                        f"Retransmisión: el bloque {block} ya se había enviado, pero su ACK no llegó a tiempo. "
                        "UDP no garantiza nada, así que TFTP se encarga: espera y reenvía."
                    )
            self._tftp_seen.add(seen_key)

        transfer = (client_port, server_port)
        if direction == "in" and server_port != TFTP_PORT and transfer not in self._tftp_transfers:
            self._tftp_transfers.add(transfer)
            explain += (
                f" Ojo: responde desde el puerto {server_port}, no desde el 69. "
                "El servidor abrió un puerto nuevo (TID) solo para esta transferencia."
            )

        layer = _layer("app", f"TFTP · {name}", start, end, fields)
        return {"kind": kind, "label": label, "explain": explain, "file_bytes": file_bytes, "layer": layer}
