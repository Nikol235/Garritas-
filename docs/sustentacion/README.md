# Guía para explicar y sustentar Garritas Store

Documentación de estudio basada en el código `ed74c90` de `feat/garritas-store`. No cambia la lógica de la aplicación ni atribuye nuevas pruebas de ejecución a esta entrega documental.

- **[Guía completa en PDF — 28 páginas](Guia-de-sustentacion-Garritas.pdf):** funcionamiento, conexiones, CRUD y reglas de los ocho servicios, relaciones N:M, sesiones S6–S11 y respuestas explicadas a las siete preguntas.
- **[Resumen para exponer — PDF de 2 páginas](Resumen-para-exponer.pdf):** discurso inicial, reparto, flujo principal y siete respuestas cortas.
- **[Mapa exacto de código — TXT](Mapa-de-codigo.txt):** 119 referencias con ruta, línea, símbolo y enlace a GitHub; se pueden copiar para abrir con Ctrl+P y Ctrl+G en VS Code.
- [Guía completa en Markdown](Guia-de-sustentacion-Garritas.md) y [resumen en Markdown](Resumen-para-exponer.md).

Las referencias están fijadas al commit revisado para que las líneas de código no cambien al navegar por una rama que siga evolucionando. Son 119 referencias, no 119 archivos distintos. Los once diagramas incluyen fuente DOT y versiones PNG/SVG en `diagramas/`.

## Orden recomendado para estudiar

1. Lee el resumen de dos páginas.
2. Revisa la compra y la compensación; identifica productor, consumidor y estado pendiente.
3. Abre la ficha de tus microservicios y su asociación N:M.
4. Ensaya las preguntas S6–S11 con los archivos abiertos, no solo memorizando conceptos.
5. Prepara el recorrido individual de tres minutos y comprueba los datos/cuentas antes de presentar.

## Precisión de la explicación

La guía distingue Feign de las demás llamadas HTTP, timeout de Circuit Breaker, roles de propiedad, ACID local de Saga, at-least-once de efectos idempotentes, y scrape UP de éxito de negocio. Describe los paneles aprovisionados y las consultas adicionales en Explore sin inventar paneles existentes.

En esta versión Envío es maestro logístico y el despacho pertenece a Venta. Las N:M de las tres parejas usan entidades de asociación con atributos y dos `@ManyToOne`; Bienestar conserva un ejemplo explícito de `@ManyToMany`. No se afirma que todos los servicios tengan CRUD libre ni que Garritas haya tenido un auth-ms propio temporal. Los pagos son simulados; una API externa real del brief global continúa siendo una integración distinta.

## Regenerar y verificar

Requiere Python 3, ReportLab, Pillow, pypdf, Graphviz y fuentes DejaVu. Las dependencias Python están fijadas en `docs/manuales/fuentes/requirements.txt`. Desde la raíz, con esas herramientas instaladas:

```bash
python3 docs/sustentacion/generar_guia.py
python3 docs/sustentacion/verificar_guia.py
```

El generador comprueba que cada ruta/símbolo exista y crea los dos PDF, el Markdown y el mapa. El verificador compara las fuentes con el commit enlazado, revisa cobertura de referencias en PDF, texto seleccionable, enlaces, marcadores y diagramas. Guarda primero tus cambios de código en Git si vas a regenerar: no enlaces como si estuvieran publicados archivos que aún no pertenecen a ese commit.

[Resultado de la verificación documental](verificacion.json). La evidencia funcional previa está en [resultados de la actualización](../evidencias-actualizacion/resultado.json).
