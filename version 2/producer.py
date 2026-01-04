# producer.py
# Script to send random order messages to a Kafka topic using confluent_kafka
# Requires confluent_kafka library
# Usage: python producer.py -n <number_of_orders> --delay <seconds_between_messages>

import json
import uuid
import random
import time
import argparse

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

producer_config = {
    # default to all three broker host ports for higher availability
    "bootstrap.servers": "localhost:9092,localhost:9094,localhost:9096"
}

# Producer is created after parsing CLI args so the bootstrap list can be overridden
producer = None

def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        try:
            val = msg.value().decode('utf-8')
        except Exception:
            val = msg.value()
        print(f"✅ Delivered {val}")
        print(f"✅ Delivered to {msg.topic()} : partition {msg.partition()} : at offset {msg.offset()}")


USERS = ["ulf", "lara", "max", "amira", "sam"]
ITEMS = [
    "frozen yogurt", "pizza", "sushi", "burger", "salad",
    "tacos", "ramen", "pasta", "curry", "ice cream"
]


def ensure_topic(topic, num_partitions=3, replication_factor=3, bootstrap_servers=None, timeout=10):
    """Ensure that a topic exists. If missing, attempt to create it using AdminClient.
    Returns True if the topic exists or was created successfully, False otherwise."""
    bs = bootstrap_servers or producer_config.get("bootstrap.servers")
    admin = AdminClient({"bootstrap.servers": bs})
    try:
        md = admin.list_topics(timeout=timeout)
    except Exception as e:
        print(f"⚠️ Could not list topics: {e}")
        return False

    if topic in md.topics and md.topics[topic].error is None:
        # Topic exists — check replication of first partition if available
        tmd = md.topics[topic]
        if tmd.partitions:
            first = next(iter(tmd.partitions.values()))
            existing_repl = len(first.replicas)
            if existing_repl != replication_factor:
                print(f"⚠️ Topic '{topic}' exists with replication {existing_repl}; requested {replication_factor}")
        print(f"ℹ️ Topic '{topic}' already exists")
        return True

    # Create topic
    new_topic = NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)
    futures = admin.create_topics([new_topic], request_timeout=timeout)
    f = futures.get(topic)
    try:
        f.result()
        print(f"✅ Created topic '{topic}' (partitions={num_partitions}, replication={replication_factor})")
        return True
    except Exception as e:
        print(f"❌ Failed to create topic '{topic}': {e}")
        return False


def create_order():
    return {
        "order_id": str(uuid.uuid4()),
        "user": random.choice(USERS),
        "item": random.choice(ITEMS),
        "quantity": random.randint(1, 10)
    }


def send_orders(topic="orders", count=10, delay=0.1):
    global producer
    # Safety: if producer wasn't created (e.g., function called directly), create it here
    if producer is None:
        producer = Producer(producer_config)

    for _ in range(count):
        order = create_order()
        value = json.dumps(order).encode('utf-8')
        try:
            producer.produce(topic=topic, value=value, callback=delivery_report)
            # trigger delivery callbacks
            producer.poll(0)
        except Exception as e:
            print(f"❌ Produce error: {e}")
            break
        time.sleep(delay)

    # flush only if producer exists
    if producer:
        producer.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send random orders to Kafka")
    parser.add_argument("-n", "--num", type=int, default=10, help="number of orders to send")
    parser.add_argument("--delay", type=float, default=0.1, help="seconds between messages")
    parser.add_argument("--bootstrap", type=str, default="localhost:9092,localhost:9094,localhost:9096",
                        help="comma-separated bootstrap.servers list (overrides default)")
    parser.add_argument("--topic", type=str, default="orders", help="topic name (default: 'orders')")
    parser.add_argument("--partitions", type=int, default=3, help="partitions when creating topic")
    parser.add_argument("--replication-factor", type=int, default=3, help="replication factor when creating topic")
    parser.add_argument("--no-create-topic", action="store_true", help="do not attempt to create topic if missing")
    args = parser.parse_args()

    # allow overriding bootstrap servers from the CLI
    if args.bootstrap:
        producer_config["bootstrap.servers"] = args.bootstrap

    # create the Producer with the chosen bootstrap list
    producer = Producer(producer_config)

    # Ensure topic exists (unless explicitly disabled)
    if not args.no_create_topic:
        ensure_topic(args.topic, num_partitions=args.partitions, replication_factor=args.replication_factor,
                     bootstrap_servers=producer_config["bootstrap.servers"])

    send_orders(topic=args.topic, count=args.num, delay=args.delay)
    print(f"Sent {args.num} orders (topic={args.topic}, bootstrap.servers={producer_config['bootstrap.servers']})")