import json
import argparse

from confluent_kafka import Consumer

# Default consumer configuration uses all broker host ports for availability
default_consumer_config = {
    "bootstrap.servers": "localhost:9092,localhost:9094,localhost:9096",
    "group.id": "order-tracker",
    "auto.offset.reset": "earliest"
}


def run_consumer(bootstrap, topic, group_id, offset_reset):
    config = {
        "bootstrap.servers": bootstrap,
        "group.id": group_id,
        "auto.offset.reset": offset_reset
    }
    consumer = Consumer(config)
    consumer.subscribe([topic])

    print(f"🟢 Consumer running (bootstrap={bootstrap}) and subscribed to '{topic}'")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("❌ Error:", msg.error())
                continue

            value = msg.value().decode("utf-8")
            order = json.loads(value)
            print(f"📦 Received order: {order.get('quantity')} x {order.get('item')} from {order.get('user')}")
    except KeyboardInterrupt:
        print("\n🔴 Stopping consumer")

    finally:
        consumer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track orders from Kafka")
    parser.add_argument("--bootstrap", type=str, default=default_consumer_config["bootstrap.servers"],
                        help="comma-separated bootstrap.servers (hosts on the local machine)")
    parser.add_argument("--topic", type=str, default="orders", help="topic to subscribe to")
    parser.add_argument("--group", type=str, default=default_consumer_config["group.id"], help="consumer group.id")
    parser.add_argument("--offset-reset", type=str, default=default_consumer_config["auto.offset.reset"],
                        help="auto.offset.reset (earliest|latest)")
    args = parser.parse_args()

    run_consumer(args.bootstrap, args.topic, args.group, args.offset_reset)