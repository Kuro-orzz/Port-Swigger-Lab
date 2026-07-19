SELECT
  NET.REG_DOMAIN(page) AS domain,
  STRING_AGG(DISTINCT version, ', ') AS versions
FROM `httparchive.crawl.pages`,
  UNNEST(technologies) AS t,
  UNNEST(t.info) AS version
WHERE date = '2026-06-01'
  AND client = 'desktop'
  AND is_root_page = TRUE
  AND t.technology = 'WordPress'
  AND version != ''
GROUP BY domain;