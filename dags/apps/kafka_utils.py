import json
import logging
import os
import pendulum
import random
import requests
import struct
import spark.sql.functions as F
from apps import kafka_config
from apps.print_utils import print_logging_info_decorator
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from io import BytesIO
from fastavro import schemaless_reader
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, BinaryType
from typing import Dict
from uuid import uuid4


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


class YahooFinanceTransactionsAvroConsumer:
    def __init__(
        self,
        schema_registry_endpoint: str = os.environ.get("KAFKA_SCHEMA_REGISTRY_ENDPOINT"),
        kafka_endpoint: str = os.environ.get("KAFKA_ENDPOINT"),
        topic: str = os.environ.get("KAFKA_TOPIC")
    ):
        self.schema_registry_endpoint = schema_registry_endpoint
        self.kafka_endpoint = kafka_endpoint
        self.topic = topic
        self.spark_session = SparkSession.builder \
            .appName("YahooFinanceTransactionsAvroConsumer") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0") \
            .getOrCreate()

    def fetch_message_schema(self, schema_id: str, schema_hashmap: Dict):
        """
        Fetches the Avro schema for a given schema ID from the schema registry.
        :param schema_id: The ID of the schema to fetch.
        :return: The Avro schema as a string.
        """
        try:
            if schema_id in schema_hashmap:
                return schema_hashmap[schema_id]
            else:
                response = requests.get(
                    f"{self.schema_registry_endpoint}/schemas/ids/{schema_id}"
                )
                response.raise_for_status()
                schema_dict = json.loads(response.json()["schema"])
                schema_hashmap[schema_id] = schema_dict
                return schema_dict
        except Exception as e:
            raise Exception(f"Failed to fetch schema with ID {schema_id}: {e}") from e

    def strip_confluent_avro_message(self, message_bytes: bytes) -> str:
        if not message_bytes:
            raise ValueError("Message bytes empty.")
        try:
            buffer = BytesIO(message_bytes)
            # Check if confluent avro serialized message
            if buffer.read(1) != b'\x00':
                raise ValueError("Improperly formatted message. Expecting Confluent Avro message.")
            # Get schema ID from message
            schema_id = struct.unpack('>I', buffer.read(4))[0]
            # Fetch schema registry schema
            schema = self.fetch_message_schema(schema_id)
            # Get payload
            payload = schemaless_reader(buffer, schema)
            return json.dumps(payload)
        except Exception as e:
            raise Exception(f"Failed to strip Confluent Avro message: {e}") from e

    def consume_transactions(self):
        df = self.spark_session \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_endpoint) \
            .option("subscribe", self.topic) \
            .option("startingOffsets", "earliest") \
            .load()
        decoded = df.withColumn("decoded_value_json", self.strip_confluent_avro_message(col("value")))
