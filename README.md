# FTP y TFTP a corazón abierto

**Grupo 1 · Redes** — Eliab Parra, Sebastian Alsleben, Santiago Landaeta y Leandro Jay.

Un laboratorio en Docker con tres máquinas: un servidor FTP, un servidor TFTP y un cliente escrito a mano. Una página web muestra en vivo cada paquete que cruza el cable, separado en capas (Ethernet, IP, TCP o UDP, y el protocolo) hasta el último byte.

## Qué hay adentro

Son tres contenedores en una red privada `10.10.10.0/24`. Las IP están elegidas para recordarlas: el servidor FTP termina en 21 y el TFTP en 69, igual que sus puertos.

| Contenedor | IP | Qué hace |
|---|---|---|
| `client` | 10.10.10.10 | El panel web, los dos clientes escritos a mano y la captura de paquetes |
| `ftp-server` | 10.10.10.21 | Servidor FTP real ([pyftpdlib](https://github.com/giampaolo/pyftpdlib)), puerto 21 y pasivos 30000-30009 |
| `tftp-server` | 10.10.10.69 | Servidor TFTP real (`tftpd-hpa`, el servidor TFTP clásico de Linux, el que se usa para respaldar routers y arrancar equipos por red), puerto 69 |

```
  navegador ──► http://localhost:8080
                       │
             ┌─────────┴──────────┐
             │ client 10.10.10.10 │  ← captura cada trama de su tarjeta de red
             └───┬────────────┬───┘
         TCP 21  │            │  UDP 69
       + datos   │            │
   ┌─────────────┴──┐   ┌─────┴───────────┐
   │ ftp-server .21 │   │ tftp-server .69 │
   └────────────────┘   └─────────────────┘
```

Los servidores son programas reales y conocidos. Los **clientes los escribimos nosotros** sobre sockets, sin librerías de FTP ni de TFTP, para que se vea cada paso del protocolo:

- [`client/app/ftp_client.py`](client/app/ftp_client.py): conexión de control, `USER`/`PASS`, `PASV` con el cálculo del puerto, canal de datos, `LIST`, `RETR`, `STOR` y `QUIT`.
- [`client/app/tftp_client.py`](client/app/tftp_client.py): `RRQ`, `WRQ`, `DATA`, `ACK` y `ERROR`, con bloques de 512 bytes, retransmisiones y el TID.
- [`client/app/decoder.py`](client/app/decoder.py): toma cada trama cruda del cable y la separa en capas, marcando qué bytes ocupa cada campo.
- [`client/app/sniffer.py`](client/app/sniffer.py): lee las tramas con un socket `AF_PACKET`, lo mismo que hace Wireshark.

## Cómo reconstruirlo

Solo hace falta **Docker con Docker Compose**: Docker Desktop en Windows o Mac, o Docker Engine en Linux.

```bash
git clone https://github.com/Lejayk/redes-ftp-tftp.git
cd redes-ftp-tftp
docker compose up --build
```

Después se abre http://localhost:8080. La primera vez tarda un par de minutos, porque construye las tres imágenes y para eso necesita internet. Después arranca en segundos y **funciona sin internet**.

Para apagar todo: `Ctrl+C` y después `docker compose down`.

La guía de la exposición, con el reparto, los guiones y las preguntas probables, está en [GUIA-EXPOSICION.md](GUIA-EXPOSICION.md).

### En la laptop de la exposición (Windows con Docker dentro de WSL2)

Ahí Docker no está en Windows sino dentro de la distro Debian de WSL2. Para eso están los dos `.bat`:

1. Doble clic en **`iniciar.bat`**: arranca Docker dentro de Debian, levanta los contenedores y abre http://localhost:8080.
2. Dejar abierta esa ventana negra durante la exposición: si se cierra, WSL se apaga y los contenedores también.
3. Para apagar todo: **`detener.bat`**.

Si la distro de WSL tiene otro nombre, se cambia la línea `set "DISTRO=Debian"` al principio de los dos archivos.

## Cómo se usa el panel

- **Pestañas FTP y TFTP**: cada protocolo tiene sus controles y su propio diagrama.
- **El pizarrón**: cada flecha es un paquete real capturado del cable, y se escribe con tiza de quien lo manda a quien lo recibe. La columna del medio es el puerto conocido (21 o 69); la de la derecha es el puerto que se abre para los datos (el pasivo de FTP o el TID de TFTP). Los colores de tiza siempre significan lo mismo: celeste para comandos y pedidos, amarillo para datos, blanco para el saludo y el cierre de TCP, rosa para errores y naranja para retransmisiones.
- **El silencio también se dibuja**: antes de una retransmisión aparece el hueco con su duración real (por ejemplo, "3,0 s de silencio: el ACK nunca llegó").
- **Limpiar** pasa el borrador por el pizarrón.
- **Inspector**: al hacer clic en una flecha se abre el paquete capa por capa. Al pasar el mouse por un campo se iluminan sus bytes en el volcado hexadecimal, y al revés.
- **Modo paso a paso**: el cliente se detiene antes de cada paso hasta que se pulsa **Siguiente**. También avanzan la flecha derecha, AvPág o la barra espaciadora, así que sirve un presentador de diapositivas.
- **Velocidad**: rápida, normal o lenta, para el modo automático.
- **Pizarrón o pizarra blanca** (botón del círculo a medias): si el proyector lava el verde, la pizarra blanca con marcadores se lee mejor. Conviene probar las dos en el aula antes de empezar.
- **Bitácora**: lo que el cliente va razonando, por ejemplo el cálculo del puerto pasivo.
- **Estadísticas**: paquetes, bytes en el cable y cuántos son del archivo. Cuando hay una descarga terminada de cada protocolo aparece la comparativa FTP contra TFTP.

## Guion sugerido para la exposición

Conviene usar el **modo paso a paso** y la velocidad **normal**.

### FTP (dos personas)

1. **Conectar.** Se ven los tres pasos del saludo TCP (`SYN`, `SYN, ACK`, `ACK`) y después el servidor habla primero con un `220`.
2. **Iniciar sesión.** `USER` recibe un `331` (falta la contraseña) y `PASS` un `230`. Abrir `PASS` en el inspector: **la contraseña viaja en texto plano** y se lee en los bytes. Es el gran problema de seguridad de FTP.
3. **Contraseña incorrecta** (opcional): cambiar la clave y volver a iniciar sesión para mostrar el `530`.
4. **Listar.** `PASV` recibe un `227` con seis números; la bitácora muestra el cálculo `p1 × 256 + p2`. Aparece una **segunda conexión TCP** (columna de la derecha): FTP separa comandos y datos.
5. **Descargar** `config-router.txt`: el contenido viaja por el canal de datos y el `226` avisa que terminó.
6. **Cerrar sesión**: `QUIT`, `221` y el cierre con `FIN`.

### TFTP (dos personas)

1. **Descargar `config-router.txt`.** Un solo `RRQ` al puerto 69, sin usuario ni contraseña y sin saludo previo, porque UDP no establece conexión. El servidor contesta **desde otro puerto** (el TID). Llegan tres bloques: 512, 512 y 276 bytes. El último es más chico, y así se sabe que terminó.
2. **Descargar `justo-1024.txt`.** Son dos bloques llenos, así que hace falta un **tercer bloque vacío** para avisar el final.
3. **Descargar `no-existe.txt`.** El servidor responde `ERROR 1` y la transferencia se corta.
4. **Marcar "Simular que se pierde el ACK del bloque 2"** y descargar de nuevo. El cliente no confirma el bloque 2, el servidor espera 3 segundos y lo **retransmite**. Así consigue TFTP la confiabilidad sobre UDP: *stop-and-wait*.
5. **Subir** un archivo con `WRQ`: el servidor acepta con `ACK 0` y el cliente manda los bloques.

### Cierre

Con la **Demo completa** de FTP y la descarga de `config-router.txt` por TFTP, la comparativa del pie muestra el mismo archivo de 1300 bytes por los dos protocolos. En las pruebas, FTP necesitó **56 paquetes y 5,7 KB** en el cable, y TFTP **7 paquetes y 1,6 KB**. FTP gasta más porque tiene saludo TCP, login, dos conexiones y acuses de recibo. TFTP es mínimo, pero no tiene seguridad ni listado de archivos. Por eso TFTP se usa en redes locales para cosas simples, como respaldar la configuración de un router o arrancar equipos por red.

## Cómo cumple el enunciado

- *"Si el protocolo posee un cliente y un servidor utilizar máquinas virtuales o Docker"*: cliente y servidores corren en contenedores Docker separados, cada uno con su IP.
- *"También pueden realizar código que permita implementar o ejemplificar el procedimiento paso a paso del protocolo"*: los clientes están escritos a mano sobre sockets, el modo paso a paso detiene cada etapa y el decodificador explica cada paquete.

## Si algo falla

- **La página no abre**: revisar que la ventana de `iniciar.bat` siga abierta y que no muestre errores. Probar de nuevo con `detener.bat` y después `iniciar.bat`.
- **El puerto 8080 está ocupado**: cambiar `"8080:8080"` por, por ejemplo, `"8090:8080"` en `docker-compose.yml` y abrir http://localhost:8090.
- **Una operación quedó trabada**: botón **Cancelar**.
- **El build falla al descargar paquetes**: las imágenes se construyen con `network: host` porque en WSL2 la red puente de Docker colgaba las descargas grandes. Si en otra máquina eso da error, se borran las tres líneas `network: host` de `docker-compose.yml`.
- **Los archivos subidos** aparecen en `ftp-server/files` y `tftp-server/files`.
- **Fuente del pizarrón**: [Klee One](https://fonts.google.com/specimen/Klee+One) de Fontworks, licencia SIL Open Font License (copia en [`client/app/static/fonts/OFL.txt`](client/app/static/fonts/OFL.txt)). Está guardada en `client/app/static/fonts`, recortada a los caracteres del panel, para que funcione sin internet.
- **Detalle técnico**: la versión de `tftpd-hpa` de Debian pierde siempre el primer pedido que atiende. Por eso [`tftp-server/start.sh`](tftp-server/start.sh) le manda un pedido descartable al arrancar, y el primer pedido de la demo ya responde bien.
