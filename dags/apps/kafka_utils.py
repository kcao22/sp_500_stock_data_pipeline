import json
import pendulum
import random
import time
from uuid import uuid4
from confluent_kafka import Producer, Consumer


def create_producer(endpoint: str = "kafka:9092") -> Producer:
    """
    Creates Kafka producer.
    """
    return Producer({
        "bootstrap.servers": endpoint
    })

def create_consumer(
        endpoint: str = "kafka:9092",
        consumer_group: str = "stock_transactions_consumer_group", offset_handling: str = "earliest",
        topic: str = "stock_transactions"
    ) -> Consumer:
    """
    Creates a Kafka consumer, connecting to a specified endpoint as a part of a specified consumer group and subscribes to a given topic.
    :param endpoint: The Kafka broker endpoint to connect to.
    :param consumer_group: The consumer group to which the consumer belongs.
    :param offset_handling: How to handle offsets, e.g., "earliest" or "latest".
    :param topic: The topic to subscribe to.
    :return: Kafka consumer instance.
    """
    stock_transaction_consumer = Consumer(
        {
            "bootstrap.servers": endpoint,
            "group.id": consumer_group,
            "auto.offset.reset": offset_handling
        }
    )
    stock_transaction_consumer.subscribe([topic])
    return stock_transaction_consumer


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
