WITH trf_dim_employees_count AS (
    SELECT
        company_id,
        company_full_time_employees,
        load_timestamp_utc_from,
        load_timestamp_utc_to
    FROM {{ ref('trf_dim_employees_count') }}
)
SELECT
    company_id,
    company_full_time_employees,
    load_timestamp_utc_from,
    load_timestamp_utc_to
FROM trf_dim_employees_count
