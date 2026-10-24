# Uso rápido

Esta carpeta cumple el mismo propósito que `uso-rapido/` en Pagatu: ejemplos ejecutables y herramientas auxiliares, separados de los microservicios.

- `garritas-eventos-py/`: productor y consumidor Kafka independientes de Spring.
- `scripts/`: arranque DEV, comprobación de estado, pruebas funcionales y de recuperación.
- `garritas.ps1`: lanzador Windows PowerShell.
- `pom.xml`: agregador Maven para compilar todos los módulos.
- `docker/`: despliegue integrado local opcional, manteniendo la raíz limpia.

Desde la raíz del proyecto:

```bash
bash uso-rapido/scripts/dev.sh build
bash uso-rapido/scripts/dev.sh all
bash uso-rapido/scripts/dev.sh status
```

Windows:

```powershell
.\uso-rapido\garritas.ps1 -Accion build
.\uso-rapido\garritas.ps1 -Accion iniciar
```
