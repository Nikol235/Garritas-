# Productor y consumidor Kafka

Como en `uso-rapido/pagatu-eventos-py`, este ejemplo prueba publicación y consumo sin depender de Spring Boot. Utiliza el topic aislado `garritas.demo.v1`: no inventa ventas ni modifica el stock real.

Primero inicia `kafka/compose-dev.yml`. Desde esta carpeta:

```powershell
docker compose build
docker compose run --rm eventos python producer_eventos.py --count 3
docker compose run --rm eventos python consumer_eventos.py --max-messages 3
```

El consumidor lee desde el comienzo e imprime topic, partición y offset. También se puede ejecutar en el host, con Python 3:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r app/requirements.txt
.venv\Scripts\python app/producer_eventos.py --count 3
.venv\Scripts\python app/consumer_eventos.py --max-messages 3
```

En Linux/macOS se usa `.venv/bin/python`. El broker por defecto es `localhost:19092`; `KAFKA_BOOTSTRAP_SERVERS` permite cambiarlo. Los comandos terminan y devuelven error si no se reciben los mensajes esperados.
