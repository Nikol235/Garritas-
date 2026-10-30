# Guía de estudio: Catálogo y Usuario con C4 Model

- [Descargar el PDF](Guia-estudio-C4-Catalogo-Usuario.pdf).
- [Descargar el HTML autónomo](Guia-estudio-C4-Catalogo-Usuario.html): guardar y abrir con un navegador. No necesita Angular ni Docker para leerlo.
- [Mapa de código copiable](Mapa-de-codigo.txt).

Incluye contexto C1, contenedores C2, componentes C3 de ambos servicios y código
C4 con clases y relaciones. También explica Eureka, Gateway, seguridad con
Keycloak, Feign, Kafka, Outbox/Inbox, Saga, compensación e idempotencia.

Las 71 referencias fijan el commit `cf3cede` para conservar las líneas verificadas.
Las credenciales indicadas son las de demostración DEV publicadas en el proyecto;
se distinguen de claves privadas, claves públicas JWKS e identificadores de
idempotencia. No se lee ningún archivo de secretos de la instalación.

Los ocho diagramas tienen fuentes `.dot` y versiones `.svg` y `.png` en
`diagramas/`, listas para reutilizar en una presentación. Las vistas C2/C3 son
acercamientos enfocados; no pretenden mostrar cada servicio o cada conexión del
sistema completo. Una tabla SQL se etiqueta como tabla, no como clase JPA.

## Regeneración y comprobación

Desde la raíz del proyecto, con Python, Graphviz y Playwright instalados y
Chromium disponible en `/usr/bin/chromium`:

```bash
python docs/guia-estudio-catalogo-usuario/generar_guia.py
python docs/guia-estudio-catalogo-usuario/verificar_guia.py
```

La generación valida que los archivos citados coincidan con la revisión indicada.
El HTML incluye los diagramas vectoriales y estilos dentro del propio documento;
no descarga recursos externos. Su botón de impresión permite guardar otro PDF.
Los fragmentos de código llevan números de línea para estudiar; para copiar una
clase completa, abrir su enlace al archivo original.
