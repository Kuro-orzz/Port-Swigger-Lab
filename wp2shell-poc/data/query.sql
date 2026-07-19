-- SELECT DISTINCT
--   NET.REG_DOMAIN(page) AS domain,
--   version
-- FROM `httparchive.crawl.pages`,
--   UNNEST(technologies) AS t,
--   UNNEST(t.info) AS version
-- WHERE date = '2026-06-01'
--   AND client = 'desktop'
--   AND is_root_page = TRUE
--   AND NET.REG_DOMAIN(page) LIKE '%.vn'
--   AND t.technology = 'WordPress'
--   AND version IN ('6.9.0', '6.9.1', '6.9.2', '6.9.3', '6.9.4', '7.0.0', '7.0.1')
-- ORDER BY domain;



-- SELECT
--   NET.REG_DOMAIN(page) AS domain,
--   STRING_AGG(DISTINCT version, ', ') AS versions
-- FROM `httparchive.crawl.pages`,
--   UNNEST(technologies) AS t,
--   UNNEST(t.info) AS version
-- WHERE date = '2026-06-01'
--   AND client = 'desktop'
--   AND is_root_page = TRUE
--   AND t.technology = 'WordPress'
--   AND version != ''
-- GROUP BY domain;