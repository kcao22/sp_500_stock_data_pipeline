-- Create ingress table for daily data
DROP SCHEMA IF EXISTS ingress;
CREATE SCHEMA IF NOT EXISTS ingress;

DROP TABLE IF EXISTS ingress.companies_daily;
CREATE TABLE IF NOT EXISTS ingress.companies_daily (
    symbol VARCHAR(65535) NOT NULL,
    load_timestamp_utc VARCHAR(65535) NOT NULL,
    previous_close VARCHAR(65535),
    "open" VARCHAR(65535),
    bid VARCHAR(65535),
    ask VARCHAR(65535),
    day_range VARCHAR(65535),
    volume VARCHAR(65535),
    avg_volume VARCHAR(65535),
    intraday_market_cap VARCHAR(65535),
    beta VARCHAR(65535),
    pe_ratio VARCHAR(65535),
    eps VARCHAR(65535),
    earnings_date VARCHAR(65535),
    forward_dividend_and_yield VARCHAR(65535),
    ex_dividend_date VARCHAR(65535),
    one_year_target_estimate VARCHAR(65535)
);

DROP TABLE IF EXISTS ingress.companies_weekly;
CREATE TABLE IF NOT EXISTS ingress.companies_weekly (
    symbol VARCHAR(65535) NOT NULL,
    load_timestamp_utc VARCHAR(65535) NOT NULL,
    company_name VARCHAR(65535),
    company_address VARCHAR(65535),
    company_phone_number VARCHAR(65535),
    company_website VARCHAR(65535),
    company_sector VARCHAR(65535),
    company_industry VARCHAR(65535),
    company_full_time_employees VARCHAR(65535),
    company_description VARCHAR(65535),
    company_corporate_governance_score VARCHAR(65535)
);

-- Create ods table for daily data
DROP SCHEMA IF EXISTS ods;
CREATE SCHEMA IF NOT EXISTS ods;

DROP TABLE IF EXISTS ods.companies_daily;
CREATE TABLE IF NOT EXISTS ods.companies_daily (
    symbol VARCHAR(16) NOT NULL,
    load_timestamp_utc TIMESTAMP NOT NULL,
    previous_close NUMERIC(9,2),
    "open" NUMERIC(9,2),
    bid VARCHAR(64),
    ask VARCHAR(64),
    day_range VARCHAR(64),
    volume VARCHAR(64),
    avg_volume VARCHAR(64),
    intraday_market_cap VARCHAR(32),
    beta NUMERIC(5,2),
    pe_ratio NUMERIC(7,2),
    eps NUMERIC(7,2),
    earnings_date VARCHAR(128),
    forward_dividend_and_yield VARCHAR(64),
    ex_dividend_date VARCHAR(128),
    one_year_target_estimate NUMERIC(9,2),
    PRIMARY KEY (symbol, load_timestamp_utc)
);

DROP TABLE IF EXISTS ods.companies_weekly;
CREATE TABLE IF NOT EXISTS ods.companies_weekly (
    symbol VARCHAR(16) NOT NULL,
    load_timestamp_utc TIMESTAMP NOT NULL,
    company_name VARCHAR(256),
    company_address VARCHAR(512),
    company_phone_number VARCHAR(64),
    company_website VARCHAR(512),
    company_sector VARCHAR(128),
    company_industry VARCHAR(128),
    company_full_time_employees INTEGER,
    company_description VARCHAR(65535),
    company_corporate_governance_score VARCHAR(1024),
    PRIMARY KEY (symbol, load_timestamp_utc)
);
