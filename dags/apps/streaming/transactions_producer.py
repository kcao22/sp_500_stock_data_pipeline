import logging
import time

from apps.kafka_utils import YahooFinanceTransactionsAvroProducer

if __name__ == "__main__":
    transaction_producer = YahooFinanceTransactionsAvroProducer()
    try:
        while True:
            transaction_producer.produce_transaction()
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info(f"Transaction production terminated by user. Shutting down...")
