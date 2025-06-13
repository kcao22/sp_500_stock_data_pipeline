WITH trf_dim_employees AS (
    SELECT
        company_id,
        company_full_time_employees,
        load_timestamp_utc_from,
        load_timestamp_utc_to
    FROM {{ ref('trf_dim_employees') }}
)
SELECT
    company_id,
    company_full_time_employees,
    load_timestamp_utc_from,
    load_timestamp_utc_to
FROM trf_dim_employees
