import json
import pendulum
import random
import time
from uuid import uuid4
from confluent_kafka import Producer


def create_producer(endpoint: str = "kafka:9092") -> Producer:
    """
    Creates Kafka producer.
    """
    return Producer({
        "bootstrap.servers": endpoint
    })

def produce_transaction():
    """
    Produces a mock stock transaction (buy or sell).
    """
    return {
        "transaction_id": uuid4().hex,
        "customer_id": random.randint(1, 1000),
        "company_id": random.randint(1, 502),
        "volume_traded": random.randint(-30, 30),
        "transaction_timestamp_utc": pendulum.now("UTC").to_iso8601_string()
    }


if __name__ == "__main__":
    producer = create_producer()
    while True:
        transaction = produce_transaction()
        producer.produce(
            topic="stock_transactions",
            value=json.dumps(produce_transaction()),
            key=str(transaction["transaction_id"]),
            callback=lambda err, msg: print(f"Produced message {transaction}") if not err else print(f"Error producing message: {err}"),
        )

        time.sleep(5)
