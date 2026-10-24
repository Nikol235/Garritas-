# Manuales de Garritas Store en PDF

Edición revisada el **24 de octubre de 2026**, basada en el código `ceaf408` de la rama `feat/garritas-store`.

| PDF | Extensión | Contenido |
|---|---:|---|
| [1. Ejecución y puertos](01-Ejecucion-y-puertos.pdf) | 13 páginas | Requisitos, Windows/PowerShell y Linux/WSL2, arranque manual/automatizado, puertos, cuentas, recorridos por rol, consolas, pruebas, diagnóstico y conservación de datos. |
| [2. Construcción desde cero con código](02-Construccion-desde-cero-con-codigo.pdf) | 262 páginas | Etapas de construcción, estructura, qué crear y dónde pegar, explicación por módulo y contenido completo de 376 archivos de código/configuración. Los wrappers generados y el lockfile se suministran en el ZIP. |
| [3. Arquitectura, clases y conexiones](03-Arquitectura-clases-y-conexiones.pdf) | 108 páginas | Tecnologías, capas, anotaciones, cabeceras y fichas de las 145 fuentes Java y de TypeScript, datos, Saga, JWT/roles/propiedad, Angular, configuraciones y conexiones HTTP/Kafka. |

Los PDF tienen texto seleccionable, índice con páginas y marcadores de navegación. Los ocho diagramas se incluyen también como SVG/PNG y su fuente DOT en `diagramas/`.

## Código para practicar

[Descargar código base ZIP](Garritas-Store-codigo-base.zip). Contiene **436 archivos**, sin `.git`, `target`, `node_modules`, logs, bases ni `.env` personales. Incluye los wrappers y el `package-lock.json` completos. El [manifiesto SHA-256](MANIFIESTO-CODIGO.json) identifica cada archivo.

Se extrajo este ZIP en una carpeta nueva y se compilaron todos los módulos Maven y Angular después de `npm ci`, sin reutilizar los `target`/`node_modules` del checkout original. Las dependencias se resuelven con Maven/npm/Docker; el ZIP no es un instalador binario sin conexión.

Si copias código desde el PDF, revisa los saltos de línea visuales; usa el archivo del ZIP para conservar el texto exacto. Cada ficha del Manual 2 corresponde a un archivo completo en su ruta original.

## Revisión comprobada

- **15 pruebas Java y 11 Angular aprobadas**, además de compilación de todos los módulos y build de producción frontend.
- Recorridos con Chromium: sedes/roles, perfil/mascotas y propiedad, profesionales/especialidades M:N, citas y doble reserva, compra/pago/stock, envíos y entrega administrativa.
- Carrito persistente, PKCE, rechazo y compensación, idempotencia y CORS.
- Kafka UI, Keycloak, Eureka, Grafana, targets Prometheus y logs Loki.
- Replay/duplicados, caída y recuperación de Pago, broker detenido y recuperación mediante outbox.
- Ejemplo Python Kafka: tres mensajes publicados y consumidos.
- Corrección de carga del perfil con dos pruebas de regresión: una respuesta tardía ya no sobrescribe lo que comienza a escribir el usuario.

[Resultados estructurados y límites](revision.json), [verificación documental](verificacion-documental.json) y resúmenes en `evidencias/`.

**Alcance:** DEV Linux/nube. El lanzador PowerShell no se ejecutó en Windows y el arranque simultáneo del despliegue integral Docker continúa pendiente; se documenta el antecedente de falta de espacio con VFS. Los pagos son simulados. No se acredita un despliegue público ni una garantía absoluta para todas las plataformas.

## Regenerar y verificar los documentos

Herramientas documentales: Python 3, Graphviz (`dot`) y fuentes DejaVu Sans/Mono. No son dependencias de ejecución de la tienda. En Linux instala los paquetes de tu distribución para Graphviz y DejaVu; luego, desde la raíz:

```bash
python3 -m venv .runtime/manuales-venv
.runtime/manuales-venv/bin/pip install -r docs/manuales/fuentes/requirements.txt
.runtime/manuales-venv/bin/python docs/manuales/fuentes/generar.py
.runtime/manuales-venv/bin/python docs/manuales/fuentes/verificar.py
```

El generador toma los archivos versionados de la revisión local: guarda primero los nuevos archivos de código con Git para que entren en el inventario. Excluye `docs/manuales/` del ZIP para evitar archivos recursivos. La evidencia `revision.json` se actualiza después de ejecutar las pruebas; generar PDF no vuelve a probar la tienda. Las fuentes Markdown de los tres manuales quedan en `fuentes/`; conserva los PDF si necesitas reproducir esta edición exacta.
