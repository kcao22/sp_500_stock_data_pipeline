WITH duplicates AS (
    SELECT
        symbol,
        load_timestamp_utc,
        COUNT(*) AS count
    FROM {{ source('ods_yahoo', 'companies_weekly') }}
    GROUP BY symbol, load_timestamp_utc
    HAVING COUNT(*) > 1
)
SELECT *
FROM duplicates;
