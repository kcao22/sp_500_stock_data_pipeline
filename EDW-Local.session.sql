-- SELECT *
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_SCHEMA = 'ingress'
--   AND TABLE_NAME = 'companies_daily';

-- SELECT
--     column_name
-- FROM 
--     INFORMATION_SCHEMA.COLUMNS
-- WHERE
--     table_schema = 'ingress'
--     AND table_name = 'companies_daily'
-- ORDER BY 
--     ordinal_position ASC

SELECT *
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'ods'
  AND TABLE_NAME = 'companies_daily';
