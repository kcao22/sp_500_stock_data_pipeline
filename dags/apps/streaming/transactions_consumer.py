from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType

# 1. Spark Session
spark = SparkSession.builder \
    .appName("KafkaToS3") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.apache.hadoop:hadoop-aws:3.3.2") \
    .getOrCreate()

# 2. S3 credentials (if running locally without IAM roles)
hadoop_conf = spark._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.access.key", "YOUR_AWS_ACCESS_KEY")
hadoop_conf.set("fs.s3a.secret.key", "YOUR_AWS_SECRET_KEY")
hadoop_conf.set("fs.s3a.endpoint", "s3.us-west-2.amazonaws.com")
hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# 3. Define Schema
schema = StructType() \
    .add("transaction_id", StringType()) \
    .add("symbol", StringType()) \
    .add("price", DoubleType()) \
    .add("volume", DoubleType()) \
    .add("timestamp", TimestampType())

# 4. Read from Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "stock_transactions") \
    .option("startingOffsets", "latest") \
    .load()

# 5. Decode Kafka value (assume JSON string)
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
