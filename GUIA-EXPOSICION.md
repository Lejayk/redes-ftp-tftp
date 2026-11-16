# Guía de la exposición · Grupo 1 · FTP y TFTP

**Expo: lunes 16/11/2026.** Unos 22 minutos más preguntas.

> **La regla de esta guía:** el protagonista es el **protocolo**. La demo no se explica a sí misma: es la **prueba en vivo** de cada concepto. Primero se dice la idea y después se señala la flecha que la demuestra.

## Reparto

Los roles sirven de referencia para repartir; todos tienen que dominar el protocolo.

| # | Bloque | Quién | Min |
|---|---|---|---|
| 1 | Para qué existen: historia y lugar en la red | **Landaeta** | 2 |
| 2 | Lo que van a ver es real (el laboratorio en un minuto) | **Eliab** | 1 |
| 3.1 | FTP: la idea de las dos conexiones | **Eliab** | 2 |
| 3.2 | FTP: comandos y códigos de respuesta | **Landaeta** | 2 |
| 3.3 | FTP: modo activo y modo pasivo | **Leandro** | 2 |
| 3.4 | FTP: texto o binario | **Landaeta** | 1 |
| 3.5 | Demo FTP: cada uno narra las flechas de su tema | Todos | 3 |
| 4 | Anatomía de un paquete: capas y bytes | **Alsleben** | 2 |
| 5.1 | TFTP: los cinco paquetes | **Alsleben** | 2 |
| 5.2 | TFTP: el TID | **Leandro** | 1 |
| 5.3 | TFTP: stop-and-wait, retransmisión y límites | **Eliab** | 2 |
| 5.4 | TFTP: cómo termina, cómo se sube y para qué se usa | **Landaeta** | 1 |
| 6 | Seguridad de los dos protocolos | **Leandro** | 3 |
| 7 | Comparativa y cierre | **Landaeta** (números) y **Leandro** (conclusión) | 2 |

**Tiempo al frente:** Leandro unos 7 minutos, Landaeta unos 6, Eliab unos 5 y Alsleben unos 4 más todo el manejo del panel.

**Alsleben maneja el panel durante toda la expo**, en modo **Paso a paso**, y avanza cuando el que habla termina la idea.

---

## 1. Para qué existen (Landaeta)

Guion literal; se puede leer:

> "Somos el Grupo 1 y nos tocó FTP y TFTP. Los dos son protocolos de la **capa de aplicación** que sirven para lo mismo: **transferir archivos entre dos máquinas**.
>
> FTP es uno de los protocolos más viejos de internet. Su primera versión, la **RFC 114, es de abril de 1971**, de antes de que existiera TCP/IP. La versión que se usa hoy es la **RFC 959, de 1985**.
>
> TFTP, la versión *trivial*, nació en **1981** con la RFC 783, y su versión actual es la **RFC 1350, de 1992**. Se diseñó para ser tan pequeño que entrara en la memoria de arranque de una máquina sin disco.
>
> La gran diferencia: **FTP va sobre TCP, en el puerto 21**, y tiene usuario, contraseña y listado de carpetas. **TFTP va sobre UDP, en el puerto 69**, y solo sabe leer o escribir un archivo cuyo nombre ya conoces.
>
> Los navegadores ya no abren enlaces `ftp://`: Firefox y Chrome quitaron el soporte en 2021. Pero FTP sigue vivo en servidores y hosting, y TFTP en cada router y en el arranque de computadoras por red."

**Si te preguntan:**
- *¿En qué capa están?* En la de aplicación. FTP se apoya en TCP y TFTP en UDP, que son de la capa de transporte.
- *¿Qué puerto usa cada uno?* FTP el 21 para los comandos; TFTP el 69 para el primer pedido.
- *¿Diferencia entre TCP y UDP?* TCP abre una conexión, numera los bytes y confirma todo lo que recibe. UDP solo manda paquetes sueltos, sin confirmar nada.

---

## 2. Lo que van a ver es real (Eliab, 1 minuto)

> "Antes de entrar al protocolo: nada de lo que van a ver es una animación. Levantamos en Docker un servidor FTP y un servidor TFTP reales, escribimos los clientes a mano con sockets, y un programa captura cada paquete que cruza la tarjeta de red, igual que Wireshark. Cada flecha del pizarrón es uno de esos paquetes."

Para quien pregunte cómo está hecho, la arquitectura completa está en el [README](README.md).

---

## 3. FTP por dentro

### 3.1 La idea central: dos conexiones (Eliab)

FTP separa **qué hacer** de **los datos**. La RFC 959 lo define así:

- **Conexión de control** (puerto 21): por ahí viajan los comandos del cliente y las respuestas del servidor, en texto. Queda abierta toda la sesión. La RFC llama a quien la atiende *intérprete de protocolo* (PI).
- **Conexión de datos**: se abre **una nueva por cada transferencia** (cada listado, cada descarga, cada subida) y se cierra al terminar. La RFC llama a quien la atiende *proceso de transferencia de datos* (DTP).

Por qué importa:

- **El control va "fuera de banda":** mientras un archivo viaja por la conexión de datos, el cliente puede mandar un comando por la de control, por ejemplo `ABOR` para cancelar.
- **El fin del archivo es el cierre de la conexión:** en el modo normal (*stream*) no hay un "fin de archivo" dentro de los datos. Por eso cada transferencia necesita su propia conexión.
- **FTP tiene estado:** la sesión recuerda quién inició sesión, en qué carpeta está y el tipo de transferencia.

**En el pizarrón:** la columna del medio es la conexión de control (puerto 21) y la de la derecha es la de datos, con el puerto que cambia en cada transferencia.

### 3.2 Comandos y respuestas (Landaeta)

Guion para Landaeta, con la tabla de abajo proyectada o en la mano:

> "Por la conexión de control, cliente y servidor se hablan **en texto**. El cliente manda **comandos** de 3 o 4 letras, como `USER` para el usuario, `PASS` para la contraseña o `RETR` para descargar. El servidor contesta siempre con **un número de tres cifras** y una frase. La frase es para las personas; el programa solo mira el número.
>
> Y el número no es al azar: **la primera cifra dice cómo salió**. El 2 es éxito, el 3 significa que va bien pero falta algo, el 4 es un error temporal y el 5 un error definitivo. **La segunda cifra dice de qué se trata**: el 3, por ejemplo, es autenticación. Por eso, cuando mandamos el usuario, el servidor contesta **331**: 'va bien, pero falta algo de autenticación', o sea, falta la contraseña. Y si la clave está mal contesta **530**: error definitivo de autenticación."

- **Comandos:** palabras de 3 o 4 letras en texto, terminadas en `CR LF`. Por ejemplo `USER`, `PASS`, `PWD`, `LIST`, `RETR`, `STOR`, `TYPE`, `PASV`, `QUIT`.
- **Respuestas:** un **código de 3 dígitos** más un texto para humanos. El programa solo mira el código.

| Primer dígito | Significa | Ejemplo |
|---|---|---|
| **1**xx | Preliminar: falta otra respuesta | `150` abriendo conexión de datos |
| **2**xx | Éxito | `226` transferencia completa |
| **3**xx | Va bien, pero falta información | `331` falta la contraseña |
| **4**xx | Error temporal: reintentar | `425` no se pudo abrir la conexión de datos |
| **5**xx | Error permanente | `530` login incorrecto |

El **segundo dígito** dice de qué trata la respuesta: 0 sintaxis, 1 información, 2 conexiones, **3 autenticación**, 5 sistema de archivos. Por eso `331` se lee "3 (falta algo) de 3 (autenticación)": falta la contraseña.

### 3.3 Modo activo y modo pasivo (Leandro)

La pregunta clave es quién abre la conexión de datos. Mirado desde seguridad, es un problema de **firewalls y NAT**:

| | Modo activo (`PORT`) | Modo pasivo (`PASV`) |
|---|---|---|
| El cliente dice | "Conéctate a mi IP, a este puerto" | "Ábreme un puerto" |
| Abre la conexión de datos | **El servidor**, desde su puerto 20 | **El cliente** |
| Problema | El firewall o el NAT del cliente bloquean conexiones entrantes | Ninguno para el cliente: abre las dos conexiones |

Hoy casi todo usa **modo pasivo**, y así funciona nuestro cliente. (Para IPv6 existen `EPSV` y `EPRT`, de la RFC 2428.)

Puntos para Leandro:
- En el **activo**, el cliente tiene que aceptar una conexión que viene de afuera. Cualquier firewall o router doméstico con NAT la bloquea por defecto, y por eso el pasivo se volvió el estándar.
- En el **pasivo**, el lado incómodo pasa al servidor: tiene que abrir un **rango de puertos** para los datos. El nuestro usa del 30000 al 30009, y el firewall del servidor tiene que permitirlos.
- **Puente a la seguridad:** el comando `PORT` le dice al servidor "conéctate a esta IP". ¿Y si la IP no es la del cliente? Eso es el **ataque de rebote**, que se ve en el bloque 6.

**En el pizarrón:** el servidor responde algo como `227 Entering passive mode (10,10,10,21,117,50)`. Los cuatro primeros números son la IP; el puerto es **117 × 256 + 50 = 30002**, y la bitácora muestra esa cuenta. Los dos últimos números cambian en cada transferencia, porque el servidor elige un puerto libre entre 30000 y 30009. Enseguida aparece un `SYN` hacia la columna de la derecha: la segunda conexión.

### 3.4 Texto o binario (Landaeta)

Guion para Landaeta:

> "Antes de pasar un archivo, el cliente le dice al servidor **de qué tipo es**. Con `TYPE A` es texto: FTP adapta los saltos de línea, porque Windows y Linux los escriben distinto. Con `TYPE I` es binario: los bytes viajan exactamente como están. Si alguien descarga una imagen o un programa en modo texto, FTP 'corrige' bytes que parecían saltos de línea y **el archivo queda roto**. Por eso nuestro cliente pide texto para el listado y binario para los archivos."

- `TYPE A` (ASCII): convierte los saltos de línea al formato de la red (`CR LF`). Sirve para texto.
- `TYPE I` (*image*, binario): manda los bytes sin tocarlos.

Descargar una imagen o un `.exe` en modo ASCII **lo corrompe**, porque cambia bytes que parecen saltos de línea. Por eso nuestro cliente usa `TYPE A` para el listado y `TYPE I` para los archivos.

### 3.5 La sesión completa, flecha por flecha (demo FTP en Paso a paso)

| Lo que aparece en el pizarrón | Narra | Qué explica |
|---|---|---|
| `SYN`, `SYN, ACK`, `ACK` | Eliab | Saludo de tres vías de TCP: recién después se pueden mandar datos |
| `220 Servidor FTP del Grupo 1 listo.` | Eliab | En FTP **el servidor habla primero** |
| `USER alumno` y `331` | Landaeta | "3 de autenticación": el usuario se acepta, falta la contraseña |
| `PASS` con clave mala y `530` | Landaeta | "5 de autenticación": error definitivo, la clave está mal |
| `PASS redes2026` y `230` | **Leandro** | La contraseña en texto plano (ver 6.1) y el `230` de login correcto |
| `TYPE A` y `200` | Landaeta | Modo texto para el listado |
| `PASV` y `227 (…)` | **Leandro** | La cuenta del puerto pasivo, que ahora el servidor tiene que tener abierto |
| `SYN` hacia la derecha | Eliab | Segunda conexión TCP: el canal de datos |
| `LIST` y `125` | Eliab | `125` = "la conexión de datos ya estaba abierta". Si no lo estuviera, el servidor diría `150` |
| `Datos · 216 B` | Eliab | El listado viaja por el canal de datos, **no** por el de control |
| `FIN` del canal de datos y `226` | Eliab | Cerrar el canal **es** la señal de fin de archivo |
| `TYPE I`, `PASV`, `RETR config-router.txt` | Landaeta | Lo mismo para descargar, ahora en binario |
| `QUIT`, `221` y `FIN` | Landaeta | Se cierra la sesión: `221` es la despedida y los `FIN` cierran la conexión de control |

**Si te preguntan:**
- *¿Por qué FTP usa dos conexiones?* Para separar el control de los datos: se puede mandar un comando mientras un archivo viaja, y el fin del archivo se marca cerrando la conexión de datos.
- *¿Qué diferencia hay entre modo activo y pasivo?* Quién abre la conexión de datos. En el activo la abre el servidor, y eso choca con firewalls y NAT. En el pasivo la abre el cliente.
- *¿Qué significa el `227`?* "Entrando en modo pasivo": trae la IP y el puerto donde el servidor espera la conexión de datos.

---

## 4. Anatomía de un paquete (Alsleben)

Un paquete es **capas dentro de capas**: cada protocolo envuelve al de arriba con su propia cabecera. Se ve abriendo la flecha `PASS redes2026` en el inspector (82 bytes en total):

| Capa | Bytes | Qué lleva |
|---|---|---|
| Ethernet | 14 | MAC de destino, MAC de origen y el tipo (`0x0800`: lo que sigue es IPv4) |
| IPv4 | 20 | IP de origen y de destino, TTL y protocolo (6 = TCP) |
| TCP | 32 | Puertos, **número de secuencia**, **número de acuse**, flags y opciones |
| FTP | 16 | El texto `PASS redes2026` y el fin de línea `CR LF` |

Al pasar el mouse por un campo se iluminan sus bytes en el volcado de abajo.

**Para contrastar, al empezar el bloque 5.1** (cuando ya hay paquetes de TFTP), se abre un `ACK` de TFTP (46 bytes). Después de IP no viene TCP sino **UDP: solo 8 bytes** (puertos, largo y checksum). UDP no trae números de secuencia ni de acuse, porque no garantiza nada. Por eso TFTP tiene que encargarse él mismo de la confiabilidad, que es justamente lo que se ve en el bloque siguiente.

---

## 5. TFTP por dentro

### 5.1 Los cinco paquetes (Alsleben)

TFTP tiene **solo cinco tipos de paquete**. Los dos primeros bytes (el *opcode*) dicen cuál es:

| Opcode | Paquete | Formato | En nuestra captura |
|---|---|---|---|
| 1 | **RRQ** (pedido de lectura) | `opcode` · nombre · `0` · modo · `0` | `RRQ config-router.txt octet`: 26 bytes |
| 2 | **WRQ** (pedido de escritura) | igual que RRQ | |
| 3 | **DATA** | `opcode` · nº de bloque (2 bytes) · hasta 512 bytes de datos | 516 bytes con un bloque lleno |
| 4 | **ACK** | `opcode` · nº de bloque | 4 bytes |
| 5 | **ERROR** | `opcode` · código · mensaje · `0` | `ERROR 1: File not found`: 19 bytes |

- **Modos:** `octet` (binario, byte por byte), `netascii` (texto, con `CR LF`) y `mail` (obsoleto).
- **Códigos de error:** 0 no definido, **1 archivo no encontrado**, 2 acceso denegado, 3 disco lleno, 4 operación ilegal, **5 TID desconocido**, 6 el archivo ya existe y 7 usuario desconocido.

**En el pizarrón:** al abrir cada flecha en el inspector se ven esos campos separados, con sus bytes.

### 5.2 El TID (Leandro)

El cliente manda el pedido al puerto 69, pero **el servidor contesta desde un puerto nuevo, al azar**. Ese par de puertos, el del cliente y el nuevo del servidor, es el *Transfer ID* (TID) e identifica la transferencia; el 69 queda libre para pedidos nuevos.
*En el pizarrón:* la columna de la derecha muestra ese puerto nuevo.

Puntos para Leandro:
- **Es la única "identidad" que tiene TFTP:** no hay usuario ni sesión, solo el par de puertos.
- **La defensa que trae:** si llega un paquete desde un puerto que no es el de la transferencia, se descarta y se contesta `ERROR 5: Unknown transfer ID`. Así un paquete perdido de otra transferencia, o uno inyectado, no se mezcla con el archivo.
- **Su límite:** un puerto al azar no es autenticación. Quien pueda ver el tráfico conoce los dos puertos y puede inyectar paquetes. Por eso TFTP no se expone fuera de una red controlada.

### 5.3 Stop-and-wait, retransmisión y límites (Eliab)

**Stop-and-wait.** Se manda **un bloque y se espera su `ACK`** antes del siguiente. No hay ventana ni reordenamiento, y por eso es tan simple que entra en una memoria de arranque.

**Confiabilidad sobre UDP: retransmisión por tiempo.** Si no llega la confirmación, el que mandó el último paquete lo **reenvía al vencer un temporizador**. El nuestro espera 3 segundos.
*En el pizarrón:* con "Simular que se pierde el ACK del bloque 2" aparece **"3,0 s de silencio"** y después `DATA bloque 2 (otra vez)` en naranja.

**El "síndrome del aprendiz de brujo".** Es un error famoso del diseño original. Si un `ACK` se **demora** (sin perderse), el emisor reenvía el bloque y le llegan dos `ACK`; si responde a cada uno, todos los bloques siguientes viajan duplicados. La corrección, documentada en la RFC 1123: **nunca reenviar por un `ACK` repetido, solo por tiempo vencido.** Nuestro cliente lo respeta.

**Límites y extensiones.** El número de bloque mide 16 bits, así que el TFTP original llega a **65 535 bloques × 512 bytes ≈ 32 MB**. Las extensiones lo amplían:
- RFC 2347: negociación de opciones, con un nuevo paquete `OACK` (opcode 6).
- RFC 2348: bloques más grandes, hasta 65 464 bytes.
- RFC 2349: el tiempo de espera y el tamaño del archivo.
- RFC 7440: varios bloques por cada `ACK`.

### 5.4 Cómo termina, cómo se sube y para qué se usa (Landaeta)

Guion para Landaeta, señalando la descarga de `config-router.txt` del bloque 5.1 mientras Alsleben descarga `justo-1024.txt`:

> "¿Cómo sabe el cliente que el archivo terminó, si TFTP no tiene un paquete de 'fin'? Con una regla muy simple: **el bloque que trae menos de 512 bytes es el último.**
>
> Este archivo mide 1300 bytes, y llegan bloques de 512, 512 y **276**. El de 276 es el final.
>
> Pero este otro mide exactamente 1024, o sea dos bloques llenos. Como el segundo también tiene 512, el cliente no puede saber que terminó. Por eso el servidor manda **un tercer bloque vacío, de 0 bytes**: es la única forma de avisar el final.
>
> Para **subir** un archivo, el cliente manda un pedido de escritura y el servidor acepta con un **`ACK 0`**, un 'ok, mándalo'. Recién ahí el cliente envía el bloque 1.
>
> ¿Y para qué se usa algo tan simple hoy? Para **arrancar computadoras por red**: el DHCP le dice a la máquina qué servidor TFTP y qué archivo cargar para arrancar, y eso se llama PXE. Y en **equipos de red**: los routers, switches y teléfonos IP guardan y cargan su configuración y su firmware por TFTP."

**Si te preguntan:**
- *¿Por qué TFTP usa UDP?* Por simplicidad: sin conexión ni estado de TCP el programa es diminuto. La confiabilidad la pone él mismo, con `ACK` y retransmisión.
- *¿Qué pasa si se pierde un DATA?* No llega su `ACK`, se vence el temporizador del servidor y lo reenvía.
- *¿Cómo sabe el cliente que terminó?* Porque le llega un bloque de menos de 512 bytes.
- *¿Por qué no hay listado de archivos?* Porque TFTP solo define leer y escribir. Hay que conocer el nombre exacto.

---

## 6. Seguridad (Leandro)

### 6.1 En la demo FTP, al llegar a `PASS`

> "Miren el círculo rosa: **la contraseña viajó en texto plano**."

- Alsleben abre `PASS` en el inspector: **"redes2026" aparece marcada en los bytes**, legible en la columna de texto.
- Este panel hace lo mismo que haría un atacante con Wireshark: **leer el cable**. Le alcanza con estar en el camino del tráfico, por ejemplo en el mismo Wi-Fi, con un ataque de ARP spoofing o desde un switch comprometido.
- **El canal de datos tampoco va cifrado:** los archivos se pueden leer, y también **modificar en el camino**, porque FTP no protege la integridad.

### 6.2 Más problemas de FTP

- **Fuerza bruta:** con una clave mala el servidor responde `530`. Los servidores frenan los intentos; el nuestro espera 1 segundo después de cada fallo.
- **FTP anónimo:** el usuario `anonymous` (RFC 1635) entra sin clave real. El nuestro lo permite solo para leer, que es lo habitual en servidores públicos.
- **Ataque de rebote (*bounce*, RFC 2577):** con `PORT` el cliente le puede decir al servidor que se conecte a **otra máquina**, y usarlo para escanear puertos o saltarse un firewall. Los servidores modernos lo rechazan; `pyftpdlib`, el nuestro, lo bloquea por defecto.

### 6.3 TFTP

- **No tiene autenticación ni cifrado.** Quien sepa o adivine el nombre de un archivo lo descarga. Es un caso real conocido: servidores TFTP expuestos que filtran configuraciones de routers, con sus contraseñas adentro.
- **Si permite escribir (WRQ), cualquiera puede subir o pisar archivos.** El nuestro lo permite solo para la demo; en producción no se habilita.
- **Ataques de reflexión:** como es UDP y no hay saludo previo, un atacante puede falsificar la IP de origen. Un pedido pequeño hace que el servidor dispare bloques de 512 bytes contra la víctima.
- **Lo que sí hicimos:** el servidor está encerrado en su carpeta (`-s`), así que nadie puede pedir, por ejemplo, `/etc/passwd`.

### 6.4 Cómo se usan bien

| | FTP | TFTP |
|---|---|---|
| Autenticación | Usuario y clave **en texto plano** | Ninguna |
| Cifrado e integridad | Ninguno | Ninguno |
| Alternativa segura | **FTPS** (el mismo FTP con TLS, RFC 4217) o **SFTP** (otro protocolo, sobre SSH, puerto 22) | Solo en una LAN aislada, con VLAN, ACL en el puerto 69 y solo lectura |
| Exponerlo a internet | No | Jamás |

**Si te preguntan:**
- *¿FTPS y SFTP son lo mismo?* No. FTPS es FTP con cifrado TLS. SFTP es otro protocolo, que viaja dentro de SSH.
- *¿Se puede seguir usando FTP?* Sí, pero solo cifrado con FTPS, o directamente cambiarlo por SFTP.
- *¿Por qué TFTP sigue existiendo si es tan inseguro?* Porque es mínimo y cabe en el arranque de una máquina. Se usa dentro de redes controladas, nunca expuesto a internet.

---

## 7. Comparativa y cierre

**Landaeta**, con la comparativa del pie a la vista:

> "Para bajar el mismo archivo de 1300 bytes, FTP necesitó **[número de FTP]** paquetes y TFTP **[número de TFTP]**. Y eso sin contar la conexión ni el login de FTP: con todo, FTP usa 56."

Con el orden de esta guía la comparativa muestra **19** paquetes para FTP y **7** para TFTP (medido en el ensayo). Si muestra otra cosa, se lee lo que diga la pantalla.

**Leandro** concluye:

> "FTP es completo: tiene usuarios, carpetas, dos conexiones y modos de transferencia, pero manda todo en texto plano. TFTP es mínimo, apenas cinco tipos de paquete y stop-and-wait, y por eso cabe en el arranque de una máquina, pero no tiene ninguna seguridad. Hoy los archivos se mueven con SFTP o FTPS, y TFTP queda para redes cerradas. Gracias."

| | FTP | TFTP |
|---|---|---|
| Transporte | TCP | UDP |
| Puertos | 21 (control) + uno por cada transferencia | 69 (pedido) + TID |
| Conexiones | Dos | Ninguna (datagramas) |
| Autenticación | Usuario y clave | Ninguna |
| Operaciones | Listar, navegar, subir, bajar, borrar, renombrar… | Leer y escribir |
| Confiabilidad | La da TCP | Propia: `ACK`, stop-and-wait y retransmisión |
| Fin del archivo | Se cierra la conexión de datos | Un bloque de menos de 512 bytes |
| Norma | RFC 959 (1985) | RFC 1350 (1992) |

---

## Chuleta de referencia

**Comandos FTP de la demo:** `USER`, `PASS`, `TYPE A` / `TYPE I`, `PASV`, `LIST`, `RETR`, `STOR`, `SYST`, `QUIT`.

**Respuestas FTP que aparecen:**

| Código | Significa |
|---|---|
| `125` | La conexión de datos ya estaba abierta: empieza la transferencia |
| `200` | Comando aceptado |
| `215` | Tipo de sistema (respuesta a `SYST`) |
| `220` | Servidor listo |
| `221` | Despedida: se cierra la conexión de control |
| `226` | Transferencia completa: se cierra la conexión de datos |
| `227` | Modo pasivo, con la IP y el puerto |
| `230` | Login correcto |
| `331` | Usuario aceptado: falta la contraseña |
| `530` | Login incorrecto |
| `550` | Archivo no disponible |

**Paquetes TFTP:** 1 `RRQ`, 2 `WRQ`, 3 `DATA`, 4 `ACK`, 5 `ERROR`, 6 `OACK` (extensión).

---

## La demo: clics de Alsleben (siempre en Paso a paso)

| Momento | Clic |
|---|---|
| FTP | **Conectar** → **Iniciar sesión** con una clave mala (para el `530`) → **Iniciar sesión** con `redes2026` → **Listar** → **Descargar** → **Cerrar sesión** |
| Contraseña | Clic en la flecha `PASS redes2026` para abrirla en el inspector |
| Anatomía (4) | Clic en `PASS` para abrir sus capas |
| Los cinco paquetes (5.1) | Pestaña **TFTP** → **Descargar** `config-router.txt` → **Descargar** `no-existe.txt` → abrir `RRQ`, un `DATA`, un `ACK` (para comparar con TCP) y el `ERROR` |
| TID (5.2) | Señalar la columna derecha: el puerto nuevo del servidor |
| Retransmisión (5.3) | Marcar **Simular que se pierde el ACK** → **Descargar** `config-router.txt` |
| Cómo termina (5.4) | **Desmarcar** la pérdida → **Descargar** `justo-1024.txt` (el bloque vacío) |
| Antes del cierre | **Descargar** `config-router.txt` una vez más, en Automático: la comparativa usa la última descarga de cada protocolo |

## Antes de empezar (llegar 15 minutos antes)

- [ ] `iniciar.bat` y dejar abierta la ventana negra.
- [ ] Abrir http://localhost:8080 y pulsar **F11**.
- [ ] Probar en el proyector el pizarrón verde y la pizarra blanca; quedarse con la que mejor se lea desde el fondo.
- [ ] **Paso a paso**, velocidad **Normal**, y **Limpiar**.

## Plan B

| Pasa esto | Hacer esto |
|---|---|
| Una operación se trabó | **Cancelar** |
| La página no carga | Revisar la ventana negra; si se cerró, `detener.bat` y luego `iniciar.bat` |
| El proyector lava el verde | Cambiar a la pizarra blanca |
| Se acaba el tiempo | **Demo completa** en Automático |
| Pregunta que nadie sabe | "Lo verificamos y le respondemos", mejor que inventar |
