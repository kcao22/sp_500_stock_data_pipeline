SELECT
    sector_id,
    secotr_name
FROM {{ ref('dim_sectors')}}
