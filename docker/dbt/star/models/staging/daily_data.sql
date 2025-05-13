SELECT
    symbol,
    load_timestamp_utc,
    previous_close,
    "open",
    TRIM(SPLIT_PART(bid, 'x', 1)) AS bid_price,
    TRIM(SPLIT_PART(bid, 'x', 2)) AS bid_size,
    TRIM(SPLIT_PART(ask, 'x', 1)) AS ask_price,
    TRIM(SPLIT_PART(ask, 'x', 2)) AS ask_size,
    TRIM(SPLIT_PART(day_range, '-', 1)) AS day_range_low,
    TRIM(SPLIT_PART(day_range, '-', 2)) AS day_range_high,
    volume,
    avg_volume,
    LEFT(intraday_market_cap, LENGTH(intraday_market_cap) - 1) AS intraday_market_cap_trillions,
    beta,
    pe_ratio,
    eps,
    CASE
        WHEN TRIM(SPLIT_PART(earnings_date, '-', 1)) IS NOT NULL THEN TO_DATE(TRIM(SPLIT_PART(earnings_date, '-', 1)), 'Mon DD, YYYY')
        ELSE NULL
    END AS earnings_date_min,
    CASE
        WHEN TRIM(SPLIT_PART(earnings_date, '-', 2)) IS NOT NULL THEN TO_DATE(TRIM(SPLIT_PART(earnings_date, '-', 2)), 'Mon DD, YYYY')
        ELSE NULL
    END AS earnings_date_max,
    forward_dividend_and_yield,
    ex_dividend_date,
    one_year_target_estimate
FROM {{ source('ods', 'companies_daily') }}


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
