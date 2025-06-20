import json
import pendulum
import random
import time
from uuid import uuid4
from confluent_kafka.avro import AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient


class YahooFinanceTransactionsProducer:
    def __init__(
            self,
            schema_registry_endpoint: str = "schema-registry:8091",
            kafka_endpoint: str = "kafka:9092",
            topic: str = "stock_transactions"
            schema: dict = {
                "type": "record",
                "name": "stock_transaction",
                "fields": [
                    {"name": "transaction_id", "type": "string"},
                    {"name": "customer_id", "type": "int"},
                    {"name": "company_id", "type": "int"},
                    {"name": "volume_traded", "type": "int"},
                    {"name": "transaction_timestamp_utc", "type": "string"}
                ]
            }

        )
    self.schema_registry_endpoint = 

def create_producer(endpoint: str = "kafka:9092", schema_registry_endpoint: str = "schema-registry:8091" ) -> AvroProducer:
    """
    Creates Kafka producer.
    """
    return AvroProducer({
        "bootstrap.servers": endpoint,
        "schema.registry.url": schema_registry_endpoint
    }, default_key_schema=load("schemas/transaction_key.avsc"),

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
