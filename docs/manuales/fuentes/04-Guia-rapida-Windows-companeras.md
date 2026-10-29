Desde la clonación hasta abrir la tienda. Comandos seleccionables y copiables para PowerShell. **Edición: 28 de octubre de 2026, Perú.**

Copia únicamente el contenido de cada bloque, sin el prefijo PS C:\...&gt;. Ejecuta los pasos en orden y espera a que termine cada uno. No pegues todos los bloques juntos: algunos son alternativas o soluciones para errores.


## 1. Antes de clonar

Instala Git, **JDK 21 completo**, **Node.js 24** y Docker Desktop con contenedores Linux. Abre Docker Desktop y espera a que su motor arranque. En una PowerShell nueva comprueba:

```powershell
git --version
java -version
javac -version
node --version
npm.cmd --version
docker compose version
docker info
```

Java y javac deben indicar 21; Node debe indicar v24.x.x. Docker info debe mostrar la sección **Server** sin errores. Cero contenedores o imágenes es normal antes del primer arranque.

Si un comando no se reconoce, instala esa herramienta o corrige PATH; cierra y vuelve a abrir PowerShell después de instalar. En la página 7 están los enlaces oficiales y los problemas habituales.


## Qué modalidad usarás

Windows ejecuta los servicios Java y Angular. Docker ejecuta las bases, Kafka, Keycloak y monitorización. El lanzador automatiza el orden; **no necesitas iniciar los ocho microservicios por separado**. Cada compañera ejecuta su propia copia local.


## 2. Clonar la rama correcta

Abre PowerShell normal. Este bloque guarda la copia en C:\Users\TU_USUARIO\proyectos\Garritas-. La variable $HOME se adapta a cada computadora.

```powershell
cd $HOME
New-Item -ItemType Directory -Force proyectos
cd proyectos
git clone --branch feat/garritas-store https://github.com/Nikol235/Garritas-.git
cd Garritas-
git branch --show-current
```

La última salida debe ser **feat/garritas-store**. Si Garritas- ya existe, no borres nada ni vuelvas a clonar encima: entra en tu copia y revisa su estado. Para actualizar una copia ya clonada, consulta la página 6.


## 3. Permitir el script en esta ventana

Desde la carpeta del proyecto ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
```

El cambio dura únicamente durante esta sesión de PowerShell. Si abres otra ventana para ejecutar el lanzador, repite este comando allí. No cambia permanentemente la política del equipo.


## 4. Compilar e instalar dependencias

```powershell
.\uso-rapido\garritas.ps1 -Accion build
```

Descarga las dependencias Maven, compila los módulos Java e instala y compila Angular. Puede tardar varios minutos la primera vez; conserva Internet y espera.

Si Angular pregunta **Would you like to share pseudonymous usage data… (y/N)**, escribe **N** y presiona Enter. Es una pregunta de estadísticas, no un error.

Al terminar Java debe indicar BUILD SUCCESS y Angular debe completar su build. El prompt PS C:\...&gt; vuelve cuando termina todo el comando. Si aparece BUILD FAILURE, Error o Falló un comando, guarda el mensaje y corrige antes de continuar.


## 5. Arrancar todo

Deja Docker Desktop abierto. En la misma PowerShell, dentro de Garritas-, ejecuta:

```powershell
.\uso-rapido\garritas.ps1 -Accion iniciar
```

**Importante: pueden abrirse varias ventanas de CMD/consola.** Es el lanzador iniciando procesos Java y Angular mediante Start-Process. No las cierres durante el uso: podrías detener aplicaciones.

Este paso descarga imágenes si faltan, levanta contenedores y espera los servicios. No ejecutes iniciar dos veces ni vuelvas a ejecutar build mientras este arranque sigue trabajando.

| Orden | Componentes |
| --- | --- |
| 1 | Kafka, Kafka UI y Keycloak con su base |
| 2 | Ocho bases PostgreSQL de negocio |
| 3 | Config Server y Eureka |
| 4 | Catálogo, Institución, Usuario, Bienestar, Venta, Pago, Citas y Envío |
| 5 | API Gateway y Angular |


## 6. Si la terminal no te deja escribir

Si todavía no aparece el prompt, el comando ocupa esa terminal. **No cierres las consolas ni repitas el arranque.** Presiona Windows + R, escribe powershell y pulsa Enter para abrir una ventana nueva.

En la nueva ventana pega:

```powershell
cd "$HOME\proyectos\Garritas-"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion estado
```

El estado debe ir mostrando OK. Si el arranque aún está en curso, algunos pueden aparecer FALLO: espera a que termine y vuelve a consultar estado. Si el arranque original terminó con error, revisa sus últimas líneas y los logs; no supongas que está todo listo por ver consolas abiertas.


## 7. Abrir la tienda y las consolas

Abre las direcciones en el navegador **de la computadora donde ejecutaste Garritas**. localhost no es una dirección para acceder a la computadora de otra compañera.

| Aplicación | Dirección local |
| --- | --- |
| Garritas Store | http://localhost:4200 |
| Kafka UI | http://localhost:18085 |
| Keycloak: administración | http://localhost:18180/admin/ |
| Eureka: servicios registrados | http://localhost:18761 |
| Gateway: API | http://localhost:18080/api/v1/productos |


## Cuentas de demostración

| Uso | Usuario | Contraseña |
| --- | --- | --- |
| Cliente de tienda | cliente | Cliente123! |
| Administrador de tienda | admin-store | Admin123! |
| Administrador Keycloak | admin | local-admin-change-me |
| Grafana, si lo arrancas | admin | local-grafana |

El administrador de Keycloak es distinto del administrador de la tienda. Estas cuentas son de laboratorio: no las uses para exponer el sistema en Internet.


## 8. Primer recorrido para comprobar funcionamiento

• Entra como cliente. Consulta Sedes y selecciona una sede activa.

• En Nueva orden añade productos; revisa cantidades y el carrito.

• Elige YAPE o PLIN para aprobación simulada. Confirma y espera a que Mis pedidos muestre Pagada. TRANSFERENCIA simula rechazo y compensación de stock.

• Completa Mi cuenta y registra una mascota antes de reservar una cita. Usa fecha futura en intervalos de 30 minutos.

• Solicita envío para un pedido pagado. Como ADMIN puedes confirmar/atender citas y marcar tránsito/entrega.

• Como cliente no debes poder editar sedes; como ADMIN sí. Los datos de cada cliente se controlan también en la API.

Los pagos son simulados: no se realiza un cobro bancario real.


## 9. Monitorización opcional

Cuando la tienda y los servicios estén listos, desde la raíz del proyecto ejecuta:

```powershell
docker compose -f obs/compose-dev.yml up -d
```

Espera un momento y abre:

| Herramienta | Dirección | Uso |
| --- | --- | --- |
| Grafana | http://localhost:13000 | Paneles y consultas; admin / local-grafana |
| Prometheus | http://localhost:19090 | Targets y métricas |
| Loki | http://localhost:13100/ready | Estado de su API; los logs se consultan en Grafana |

No uses obs/compose.yml para estos puertos: ese archivo es de otra modalidad. Kafka UI ya se inicia con el lanzador principal; no necesita este paso opcional.


## Puertos de los servicios de negocio

| Microservicio | HTTP | PostgreSQL host |
| --- | --- | --- |
| Venta | 8081 | 15441 |
| Institución / sedes | 8082 | 15442 |
| Envío | 8083 | 15443 |
| Citas | 8084 | 15444 |
| Catálogo | 8085 | 15445 |
| Usuario / mascotas | 8086 | 15446 |
| Pago | 8087 | 15447 |
| Bienestar / especialistas | 8088 | 15448 |

Infraestructura: Config Server 18888; Eureka 18761; Gateway 18080. Kafka usa 19092 desde el host (no es una página web). Las bases usan 5432 dentro de sus contenedores, publicados como 15441–15448 en Windows. Angular utiliza Gateway; no tienes que abrir manualmente cada puerto de negocio.


## 10. Detener y volver a iniciar

Para detener Java y Angular de forma gestionada, desde una PowerShell en el proyecto:

```powershell
.\uso-rapido\garritas.ps1 -Accion detener
```

Los contenedores y volúmenes se conservan. Para volver a usar la misma versión, abre Docker Desktop y ejecuta:

```powershell
cd "$HOME\proyectos\Garritas-"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion iniciar
```

Si el comando iniciar todavía está ejecutándose y deseas cancelarlo, usa Ctrl+C en la terminal original, espera el prompt y después ejecuta detener. No borres .runtime/windows-processes.json para forzar otro arranque: primero comprueba y detén los procesos registrados.


## 11. Actualizar una copia que ya existe

Solo cuando hayas detenido Java y Angular. Revisa git status: si muestra trabajo propio, consérvalo antes de actualizar; no uses reset --hard para saltarte esa revisión.

```powershell
cd "$HOME\proyectos\Garritas-"
git status
git branch --show-current
```

Si estás en feat/garritas-store y no tienes cambios locales pendientes:

```powershell
git pull --ff-only origin feat/garritas-store
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\uso-rapido\garritas.ps1 -Accion build
.\uso-rapido\garritas.ps1 -Accion iniciar
```

Ejecuta los comandos uno a uno. Si pull o build falla, detente antes de iniciar. Normalmente no necesitas compilar en cada sesión: vuelve a compilar cuando actualices o cambies código.


## Datos y limpieza

No ejecutes docker compose down -v como limpieza rutinaria: puede eliminar los volúmenes con datos. Para detener el laboratorio puedes usar detener y luego cerrar Docker Desktop; los volúmenes no son una copia de seguridad.


## 12. Problemas frecuentes y comandos de diagnóstico

**Docker Desktop is unable to start.** Primero prueba WSL:

```powershell
wsl --status
wsl --list --verbose
wsl -d Ubuntu -- uname -r
```

El último comando solo aplica si tienes una distribución llamada Ubuntu. Para reiniciar WSL guarda tu trabajo, cierra Docker Desktop completamente, ejecuta el siguiente comando, vuelve a abrir Docker Desktop y comprueba docker info:

```powershell
wsl --shutdown
# Ahora abre Docker Desktop desde Inicio; espera y ejecuta:
docker info
```

**No abre la tienda / FALLO en un servicio.** Usa estado y consulta el log concreto. Ejemplo de Catálogo (sustituye el nombre por el servicio que falló):

```powershell
Get-Content .runtime\garritas-catalogo-ms\error.log -Tail 60
Get-Content .runtime\garritas-catalogo-ms\console.log -Tail 60
```

Angular escribe .runtime/frontend.log y frontend-error.log. Para contenedores:

```powershell
docker ps -a
docker compose -f kafka/compose-dev.yml logs --tail 60
docker compose -f keycloak/compose-dev.yml logs --tail 60
```

**Ya existe un arranque registrado.** Ejecuta estado. Si necesitas reiniciar, termina/cancela el arranque original y utiliza detener antes de iniciar de nuevo. No lances procesos duplicados.

**Avisos npm o pregunta de Angular.** Responde N a estadísticas. npm fund y los avisos de actualización no son por sí mismos fallos del build. Si hay vulnerabilidades, registra y revisa npm audit antes de publicar; no ejecutes npm audit fix --force a ciegas.


## Instaladores oficiales si faltan herramientas

Git: https://git-scm.com/downloads/win<br/>JDK 21: https://adoptium.net/temurin/releases/?version=21<br/>Node.js: https://nodejs.org/en/download (elige versión 24)<br/>Docker Desktop: https://www.docker.com/products/docker-desktop/

Si necesitas ayuda, comparte el comando que ejecutaste y el error completo. El código se validó en DEV Linux; esta guía recoge el flujo PowerShell y los problemas observados durante el arranque en Windows. No acredita todas las configuraciones posibles de Windows.
