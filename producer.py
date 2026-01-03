import json
import uuid
import random
import time
import argparse

from confluent_kafka import Producer

producer_config = {
    "bootstrap.servers": "localhost:9092"
}

producer = Producer(producer_config)

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


def create_order():
    return {
        "order_id": str(uuid.uuid4()),
        "user": random.choice(USERS),
        "item": random.choice(ITEMS),
        "quantity": random.randint(1, 10)
    }


def send_orders(topic="orders", count=10, delay=0.1):
    for _ in range(count):
        order = create_order()
        value = json.dumps(order).encode('utf-8')
        producer.produce(topic=topic, value=value, callback=delivery_report)
        # trigger delivery callbacks
        producer.poll(0)
        time.sleep(delay)
    producer.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send random orders to Kafka")
    parser.add_argument("-n", "--num", type=int, default=10, help="number of orders to send")
    parser.add_argument("--delay", type=float, default=0.1, help="seconds between messages")
    args = parser.parse_args()
    send_orders(count=args.num, delay=args.delay)
    print(f"Sent {args.num} orders")