#!/bin/bash
# arranca tftpd-hpa y le manda un pedido descartable.
# esta versión pierde siempre el primer pedido que atiende (el proceso hijo falla con
# "socket: Address family not supported by protocol"); los siguientes funcionan bien,
# así que se "gasta" ese primer pedido antes de la demo.
set -euo pipefail

# -L  primer plano (docker necesita un proceso que no se vaya a segundo plano)
# -c  permite crear archivos nuevos, o sea, subidas con WRQ
# -p  sin chequeos extra de permisos
# -s  encierra al servidor dentro de /srv/tftp
# -T  espera 3 s sin ACK antes de retransmitir un bloque
in.tftpd -L -c -p -s -u root -T 3000000 /srv/tftp &
server=$!

sleep 1
# rrq de un archivo inexistente, enviado con el /dev/udp de bash
printf '\x00\x01calentamiento\x00octet\x00' > /dev/udp/127.0.0.1/69
echo "[tftp-server] escuchando en el puerto 69"

wait "$server"
