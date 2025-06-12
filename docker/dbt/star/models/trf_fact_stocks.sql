WITH companies_daily AS (
    SELECT
        symbol,
        load_timestamp_utc,
        previous_close,
        open_price,
        bid_price,
        bid_size,
        ask_price,
        ask_size,
        day_range_low,
        day_range_high,
        volume,
        avg_volume,
        intraday_market_cap_trillions,
        beta,
        pe_ratio,
        eps,
        earnings_date_min,
        earnings_date_max,
        forward_dividend_and_yield,
        ex_dividend_date,
        one_year_target_estimate
    FROM {{ ref('stg_companies_daily') }}
    {% if is_incremental() %}
    WHERE load_timestamp_utc > (SELECT MAX(load_timestamp_utc) FROM {{ this }})
    {% endif %}
), latest_weekly_timestamp AS (
    SELECT MAX(load_timestamp_utc) AS max_load_timestamp_utc
    FROM {{ ref('stg_companies_weekly') }} 
), companies_weekly AS (
    SELECT
        symbol,
        load_timestamp_utc,
        company_name,
        company_street_address,
        company_city,
        company_state,
        company_zip_code,
        company_country,
        company_phone_number,
        company_website,
        company_sector,
        company_industry,
        company_full_time_employees,
        company_description,
        company_corporate_governance_score
    FROM {{ ref('stg_companies_weekly') }}
    WHERE load_timestamp_utc = (SELECT max_load_timestamp_utc FROM latest_weekly_timestamp)

), companies AS (
    SELECT
        company_id,
        company_symbol,
        company_name
    FROM {{ ref('dim_companies')}}
), industries AS (
    SELECT
        industry_id,
        industry_name
    FROM {{ ref('dim_industries') }}
), sectors AS (
    SELECT
        sector_id,
        sector_name
    FROM {{ ref('dim_sectors') }}
), states AS (
    SELECT
        state_id,
        state_name
    FROM {{ ref('dim_states') }}
), dimensional_companies_daily AS (
    SELECT
        c.company_id,
        i.industry_id,
        s.sector_id,
        st.state_id,
        load_timestamp_utc,
        previous_close,
        open_price,
        bid_price,
        bid_size,
        ask_price,
        ask_size,
        day_range_low,
        day_range_high,
        volume,
        avg_volume,
        intraday_market_cap_trillions,
        beta,
        pe_ratio,
        eps,
        earnings_date_min,
        earnings_date_max,
        forward_dividend_and_yield,
        ex_dividend_date,
        one_year_target_estimate

    FROM 
        companies_daily cd
        LEFT JOIN companies_weekly cw ON cd.symbol = cw.symbol
        LEFT JOIN companies c ON cd.symbol = c.company_symbol
        LEFT JOIN industries i ON cw.company_industry = i.industry_name
        LEFT JOIN sectors s ON cw.company_sector = s.sector_name
        LEFT JOIN states st ON cw.company_state = st.state_name
)