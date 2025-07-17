import os
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType, IntegerType


# Get message schema
value_schema = None
try:
    response = requests.get(f"{os.environ.get('KAFKA_SCHEMA_REGISTRY_ENDPOINT')}/subjects/{os.environ.get('KAFKA_TOPIC')}/versions/latest")
    value_schema = response.json()["schema"]
except Exception as e:
    raise Exception(f"Failed to fetch schema from schema registry: {e}")

# Create spark session
spark = SparkSession.builder \
    .appName("transactions_consumer") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
            "org.apache.spark:spark-avro_2.12:3.4.1,"
            "org.apache.hadoop:hadoop-aws:3.3.2") \
    .getOrCreate()

# Set Hadoop AWS configurations for S3 access
hadoop_conf = spark._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.access.key", os.environ.get("AWS_ACCESS_KEY_ID"))
hadoop_conf.set("fs.s3a.secret.key", os.environ.get("AWS_SECRET_ACCESS_KEY"))
hadoop_conf.set("fs.s3a.endpoint", f"s3.{os.environ.get("AWS_REGION")}.amazonaws.com")
hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# Consume messages
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", os.environ.get("KAFKA_TOPIC")) \
    .option("startingOffsets", "latest") \
    .load()

# Set schema
schema = StructType() \
    .add("transaction_id", StringType()) \
    .add("customer_id", IntegerType()) \
    .add("company_id", IntegerType()) \
    .add("volume_traded", IntegerType()) \
    .add("transaction_timestamp_utc", TimestampType())


df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# 6. Write to S3 in append mode (partitioned per batch)
query = df_parsed.writeStream \
    .format("parquet") \
    .option("path", "s3a://your-bucket/path/to/stock_transactions/") \
    .option("checkpointLocation", "/tmp/spark-checkpoint-stock-transactions/") \
    .outputMode("append") \
    .start()

query.awaitTermination()
