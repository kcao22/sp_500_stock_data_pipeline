WITH base_data AS (
    SELECT
        symbol,
        load_timestamp_utc,
        previous_close,
        "open",
        bid,
        ask,
        day_range,
        volume,
        avg_volume,
        intraday_market_cap,
        beta,
        pe_ratio,
        eps,
        earnings_date,
        forward_dividend_and_yield,
        ex_dividend_date,
        one_year_target_estimate
    FROM {{ source('ods_yahoo', 'companies_daily') }}
),
parsed_bid_ask AS (
    SELECT
        *,
        TRIM(SPLIT_PART(bid, 'x', 1)) AS bid_price,
        TRIM(SPLIT_PART(bid, 'x', 2)) AS bid_size,
        TRIM(SPLIT_PART(ask, 'x', 1)) AS ask_price,
        TRIM(SPLIT_PART(ask, 'x', 2)) AS ask_size
    FROM base_data
),
parsed_day_range AS (
    SELECT
        *,
        TRIM(SPLIT_PART(day_range, '-', 1)) AS day_range_low,
        TRIM(SPLIT_PART(day_range, '-', 2)) AS day_range_high
    FROM parsed_bid_ask
),
parsed_earnings_date AS (
    SELECT
        *,
        CASE
            WHEN TRIM(SPLIT_PART(earnings_date, '-', 1)) IS NOT NULL THEN TO_DATE(TRIM(SPLIT_PART(earnings_date, '-', 1)), 'Mon DD, YYYY')
            ELSE NULL
        END AS earnings_date_min,
        CASE
            WHEN TRIM(SPLIT_PART(earnings_date, '-', 2)) IS NOT NULL THEN TO_DATE(TRIM(SPLIT_PART(earnings_date, '-', 2)), 'Mon DD, YYYY')
            ELSE NULL
        END AS earnings_date_max
    FROM parsed_day_range
),
daily_data AS (
    SELECT
        symbol,
        load_timestamp_utc,
        previous_close,
        "open",
        bid_price,
        bid_size,
        ask_price,
        ask_size,
        day_range_low,
        day_range_high,
        volume,
        avg_volume,
        LEFT(intraday_market_cap, LENGTH(intraday_market_cap) - 1) AS intraday_market_cap_trillions,
        beta,
        pe_ratio,
        eps,
        earnings_date_min,
        earnings_date_max,
        forward_dividend_and_yield,
        ex_dividend_date,
        one_year_target_estimate
    FROM parsed_earnings_date
)
SELECT *
FROM daily_data;
