import logging
import os
import pendulum
import random
from apps import kafka_config
from apps.print_utils import print_logging_info_decorator
from typing import Dict
from uuid import uuid4
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


logging.basicConfig(level=logging.INFO)


class YahooFinanceTransactionsAvroProducer:
    def __init__(
        self,
        schema_registry_endpoint: str = os.environ.get("KAFKA_SCHEMA_REGISTRY_ENDPOINT"),
        kafka_endpoint: str = os.environ.get("KAFKA_ENDPOINT"),
        topic: str = os.environ.get("KAFKA_TOPIC"),
        key_schema: str = kafka_config.schemas["transactions"]["key_schema"],
        value_schema: str = kafka_config.schemas["transactions"]["value_schema"]
    ):
        """
        Creates Kafka producer object for creating mock stock transactions.
        :param schema_registry_endpoint: URL of the schema registry.
        :param kafka_endpoint: URL of the Kafka broker.
        :param topic: Kafka topic to produce messages to.
        :param key_schema: Avro schema for the message key for partitioning logic.
        :param value_schema: Avro schema for the message value containing transaction details.
        """
        self.schema_registry_endpoint = schema_registry_endpoint
        self.kafka_endpoint = kafka_endpoint
        self.topic = topic
        self.key_schema = avro.loads(key_schema)
        self.value_schema = avro.loads(value_schema)
        self.producer = self._create_producer()

    @print_logging_info_decorator
    def _create_producer(self) -> AvroProducer:
        """
        Creates Kafka producer.
        """
        return AvroProducer({
            "bootstrap.servers": self.kafka_endpoint,
            "schema.registry.url": self.schema_registry_endpoint
        }, default_key_schema=self.key_schema, default_value_schema=self.value_schema)

    @print_logging_info_decorator
    def _get_mock_transaction(self) -> Dict:
        """
        Produces a mock stock transaction dictionary to send to Kafka broker (buy or sell).
        """
        return {
            "transaction_id": uuid4().hex,
            "customer_id": random.randint(1, 1000),
            "company_id": random.randint(1, 502),
            "volume_traded": random.randint(-30, 30),
            "transaction_timestamp_utc": pendulum.now("UTC").to_iso8601_string()
        }

    @print_logging_info_decorator
    def produce_transaction(self):
        """
        Produces a mock stock transaction to the Kafka topic.
        """
        transaction = self._get_mock_transaction()
        try:
            self.producer.produce(
                topic=self.topic,
                value=transaction,
                key={"company_id": transaction["company_id"]},
                callback=lambda err, msg: logging.info(f"Produced message {transaction}") if not err else logging.error(f"Error producing message: {err}")
            )
            self.producer.flush()
        except Exception as e:
            raise Exception(f"Failed to produce message with exception: {e}") from e
