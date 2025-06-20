DROP TABLE IF EXISTS ingress_yahoo_finance.transactions;
CREATE TABLE IF NOT EXISTS ingress_yahoo_finance.transactions (
    transaction_id VARCHAR(65535),
    customer_id VARCHAR(65535),
    company_id VARCHAR(65535),
    volume_traded VARCHAR(65535),
    transaction_timestamp_utc VARCHAR(65535)
);

DROP TABLE IF EXISTS ods_yahoo_finance.transactions;
CREATE TABLE IF NOT EXISTS ods_yahoo_finance.transactions (
    transaction_id VARCHAR(64) NOT NULL,
    customer_id INT NOT NULL,
    company_id INT NOT NULL,
    volume_traded INT NOT NULL,
    transaction_timestamp_utc TIMESTAMP,
    PRIMARY KEY (transaction_id)
);
