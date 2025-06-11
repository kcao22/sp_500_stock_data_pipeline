WITH base_data AS (
    SELECT
        symbol,
        load_timestamp_utc,
        company_name,
        company_address,
        company_phone_number,
        company_website,
        company_sector,
        company_industry,
        company_full_time_employees,
        company_description,
        company_corporate_governance_score
    FROM {{ source('ods_yahoo', 'companies_weekly') }}
    {% if is_incremental() %}
    WHERE load_timestamp_utc > (SELECT MAX(load_timestamp_utc) FROM {{ this }})
    {% endif %}
),
parsed_addresses AS (
    SELECT 
        *,
        COALESCE(TRIM(SPLIT_PART(company_address, ',', 1)), NULL) AS company_street_address,
        COALESCE(SPLIT_PART(TRIM(SPLIT_PART(company_address, ',', 2)), ' ', 1), NULL) AS company_city,
        COALESCE(SPLIT_PART(TRIM(SPLIT_PART(company_address, ',', 2)), ' ', 2), NULL) AS company_state,
        COALESCE(SPLIT_PART(TRIM(SPLIT_PART(company_address, ',', 2)), ' ', 3), '') AS company_zip_code,
        COALESCE(SPLIT_PART(TRIM(SPLIT_PART(company_address, ',', 2)), ' ', 4), '') AS company_country
    FROM base_data
),
parsed_phone_numbers AS (
    SELECT
        *,
        REGEXP_REPLACE(company_phone_number, '[^0-9]', '') AS company_phone_number_cleaned
    FROM parsed_addresses
),
parsed_employees AS (
    SELECT
        *,
        REGEXP_REPLACE(company_full_time_employees, '[^0-9]', '') AS company_full_time_employees_cleaned
    FROM parsed_phone_numbers
),
parsed_description AS (
    SELECT
        *,
        REPLACE(company_description, 'Description   ', '') AS company_description_cleaned
    FROM parsed_employees
),
parsed_governance_scores AS (
    SELECT
        *,
        REPLACE(company_corporate_governance_score, 'Corporate Governance   ', '') AS company_corporate_governance_score_cleaned
    FROM parsed_description
),
weekly_data AS (
    SELECT
        symbol,
        load_timestamp_utc,
        company_name,
        company_street_address,
        company_city,
        company_state,
        company_zip_code,
        company_country,
        company_phone_number_cleaned AS company_phone_number,
        company_website,
        company_sector,
        company_industry,
        company_full_time_employees_cleaned AS company_full_time_employees,
        company_description_cleaned AS company_description,
        company_corporate_governance_score_cleaned AS company_corporate_governance_score
    FROM parsed_governance_scores
)
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
FROM weekly_data
