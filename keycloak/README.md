# Keycloak

Desde la raíz: `docker compose -f keycloak/compose-dev.yml up -d --wait`.

Consola en el puerto **18180**; realm `garritas`. El administrador de Keycloak es `admin` / `local-admin-change-me`, configurable por `KEYCLOAK_ADMIN_PASSWORD`.

Cuentas de tienda: `cliente` / `Cliente123!`, `admin-store` / `Admin123!`. Son fixtures locales, no credenciales de producción.

`garritas-realm.json` se importa solo si el realm aún no existe; cambiar el JSON no sobrescribe usuarios en un volumen existente. El consumidor de JWT comprueba firma, emisor y audiencia `garritas-api`. El cliente Angular es público y utiliza Authorization Code con PKCE; no tiene secreto ni guarda tokens en localStorage.

La red es `garritas-keycloak-dev-net`. Prometheus se conecta al puerto interno 9000 para las métricas, sin publicar el servicio fuera de localhost. El volumen conserva su nombre anterior.
