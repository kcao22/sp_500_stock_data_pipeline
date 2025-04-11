-- Create raw table for daily data
DROP SCHEMA IF EXISTS raw;
CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.companies_daily;
CREATE TABLE IF NOT EXISTS raw.companies_daily (
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

DROP TABLE IF EXISTS raw.companies_weekly;
CREATE TABLE IF NOT EXISTS raw.companies_weekly (
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

