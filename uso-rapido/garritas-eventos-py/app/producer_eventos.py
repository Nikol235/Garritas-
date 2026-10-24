"""Isolated Kafka exercise: never publishes fabricated purchases into the real Saga."""
import argparse
import json
import os
import time
import uuid
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=3)
    args = parser.parse_args()
    broker = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:19092')
    topic = os.getenv('KAFKA_TOPIC', 'garritas.demo.v1')
    if topic != 'garritas.demo.v1':
        parser.error('Este productor usa solo garritas.demo.v1; no altera eventos de negocio')
    admin = KafkaAdminClient(bootstrap_servers=broker, client_id='garritas-demo-admin')
    try:
        admin.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()
    producer = KafkaProducer(bootstrap_servers=broker, acks='all',
                             key_serializer=lambda k: k.encode(),
                             value_serializer=lambda v: json.dumps(v).encode())
    try:
        for number in range(args.count):
            event = {'eventId': str(uuid.uuid4()), 'type': 'demo.mascota',
                     'nombre': 'Luna', 'numero': number + 1, 'timestamp': time.time()}
            metadata = producer.send(topic, key='luna', value=event).get(timeout=15)
            print(json.dumps({'status': 'published', 'topic': metadata.topic,
                              'partition': metadata.partition, 'offset': metadata.offset}), flush=True)
    finally:
        producer.close(timeout=10)


if __name__ == '__main__':
    main()
