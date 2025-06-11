SELECT
    industry_id,
    industry_name
FROM {{ ref('dim_industries')}}
