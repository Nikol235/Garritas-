# Compose integrado opcional

Las herramientas de integración se agrupan aquí para mantener una estructura de raíz como Pagatu. El flujo DEV recomendado y probado se documenta en la raíz.

Desde la raíz del repositorio:

```bash
docker compose -f uso-rapido/docker/compose.yml up -d --build --wait --wait-timeout 300
```

Si el builder no puede descargar dependencias, compila en el host y utiliza los artefactos:

```bash
bash uso-rapido/scripts/dev.sh build
(cd clients/garritas-frontend && npm ci && npm run build)
docker compose -f uso-rapido/docker/compose.yml -f uso-rapido/docker/compose.prebuilt.yml up -d --build --wait --wait-timeout 300
```

El contexto de construcción es la raíz; el agregador Maven está en `uso-rapido/pom.xml`. El frontend se sirve en 4200, Gateway en 28080, Config en 28888 y Eureka en 28761. Keycloak usa 18180. No ejecutar al mismo tiempo que DEV, porque comparten puertos.

La monitorización se añade con `-f uso-rapido/docker/compose.observability.yml`. Las imágenes/volúmenes son locales de demostración; no conforman un despliegue público de producción. En la nube usada en la revisión, VFS agotó el disco al intentar todo el stack: el funcionamiento conjunto en contenedores sigue pendiente de recursos suficientes; no se afirma que esa prueba haya pasado.
