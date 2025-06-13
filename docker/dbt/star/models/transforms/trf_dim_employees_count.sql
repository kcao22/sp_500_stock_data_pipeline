WITH company_employees AS (
    SELECT
        symbol,
        load_timestamp_utc,
        company_full_time_employees
    FROM {{ ref('stg_companies_weekly') }}
    {% if is_incremental() %}
    WHERE load_timestamp_utc > (SELECT MAX(load_timestamp_utc) FROM {{ this }})
    {% endif %}
), dim_companies AS 
    SELECT
        company_id,
        company_symbol,
        company_name
    FROM {{ ref('dim_companies') }}
), dim_employees_count AS (
    SELECT
        dc.company_id AS company_id,
        company_full_time_employees,
        load_timestamp_utc AS load_timestamp_utc_from
        LEAD(load_timestamp_utc, 1) OVER (PARTITION BY symbol ORDER BY load_timestamp_utc) AS load_timestamp_utc_to
    FROM 
        company_employees ce
        LEFT JOIN dim_companies dc ON ce.symbol = dc.company_symbol
)
SELECT
    company_id,
    company_full_time_employees,
    load_timestamp_utc_from,
    load_timestamp_utc_to
FROM dim_employees_count

