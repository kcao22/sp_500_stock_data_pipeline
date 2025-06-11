SELECT
    company_id,
    company_symbol,
    company_name
FROM {{ ref('dim_companies')}}
