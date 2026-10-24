import argparse
import json
import os
from kafka import KafkaConsumer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-messages', type=int, default=3)
    parser.add_argument('--timeout-ms', type=int, default=30000)
    args = parser.parse_args()
    consumer = KafkaConsumer(os.getenv('KAFKA_TOPIC', 'garritas.demo.v1'),
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:19092'),
        group_id=None, auto_offset_reset='earliest', enable_auto_commit=False,
        consumer_timeout_ms=args.timeout_ms)
    processed = 0
    try:
        for message in consumer:
            try:
                event = json.loads(message.value)
                status = 'consumed' if isinstance(event, dict) and event.get('eventId') else 'invalid'
            except (ValueError, UnicodeDecodeError):
                status = 'invalid'
            print(json.dumps({'status': status, 'topic': message.topic,
                              'partition': message.partition, 'offset': message.offset}), flush=True)
            processed += 1
            if processed >= args.max_messages:
                break
    finally:
        consumer.close()
    if processed < args.max_messages:
        raise SystemExit('No llegaron suficientes mensajes antes del tiempo límite')


if __name__ == '__main__':
    main()
