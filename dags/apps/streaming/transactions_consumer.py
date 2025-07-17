import os
import pendulum
import requests
import pyspark.sql.functions as F
from pyspark.sql import SparkSession


def get_topic_schema(schema_registry_endpoint: str = os.environ.get("KAFKA_SCHEMA_REGISTRY_ENDPOINT"), topic: str = os.environ.get("KAFKA_TOPIC")) -> str:
    """
    Returns the Avro schema for the specified Kafka topic.
    :param topic: Kafka topic name.
    :return: Avro schema as a string.
    """
    schema_reponse = requests.get(
        url=f"{schema_registry_endpoint}/subjects/{topic}-value/versions/latest"
    )
    schema_reponse.raise_for_status()
    return schema_reponse.json().get("schema")


# Create Spark session and add Kafka + Avro Java dependencies
spark = SparkSession.builder \
    .appName("transactions_consumer_1") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.confluent:kafka-avro-serializer:7.4.0") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("schema.registry.url", os.environ.get("KAFKA_SCHEMA_REGISTRY_ENDPOINT")) \
    .getOrCreate()

timestamp_str = pendulum.now(tz="UTC").format("YYYYMMDD-HHmmss")

transactions_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get("KAFKA_ENDPOINT")) \
    .option("subscribe", os.environ.get("KAFKA_TOPIC")) \
    .option("startingOffsets", "earliest") \
    .load()

transactions_df = transactions_df.select(
    F.from_avro(transactions_df.value, os.environ.get("KAFKA_VALUE_SCHEMA")).alias("value"),
    F.from_avro(transactions_df.key, os.environ.get("KAFKA_KEY_SCHEMA")).alias("key")
).select(
    "value.transaction_id",
    "value.customer_id",
    "value.company_id",
    "value.volume_traded",
    "value.transaction_timestamp_utc",
    "key.company_id"
)

