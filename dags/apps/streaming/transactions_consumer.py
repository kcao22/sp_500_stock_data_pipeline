import logging
import time

from apps.kafka_utils import YahooFinanceTransactionsAvroConsumer


if __name__ == "__main__":
    # To avoid redundant requests to schema registry.
    message_schemas = {}
    

