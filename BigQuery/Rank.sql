SELECT
  NET.REG_DOMAIN(page) AS domain,
  rank,
  -- Tech stack theo nhóm
  STRING_AGG(DISTINCT IF('CMS' IN UNNEST(t.categories), t.technology, NULL), ', ')                    AS cms,
  STRING_AGG(DISTINCT IF('Programming languages' IN UNNEST(t.categories), t.technology, NULL), ', ')  AS languages,
  STRING_AGG(DISTINCT IF('JavaScript frameworks' IN UNNEST(t.categories), t.technology, NULL), ', ')  AS js_frameworks,
  STRING_AGG(DISTINCT IF('Web frameworks' IN UNNEST(t.categories), t.technology, NULL), ', ')         AS web_frameworks,
  STRING_AGG(DISTINCT IF('Web servers' IN UNNEST(t.categories), t.technology, NULL), ', ')            AS web_server,
  STRING_AGG(DISTINCT IF('CDN' IN UNNEST(t.categories), t.technology, NULL), ', ')                    AS cdn,
  STRING_AGG(DISTINCT IF('Ecommerce' IN UNNEST(t.categories), t.technology, NULL), ', ')              AS ecommerce,
  -- Hạ tầng từ summary
  ANY_VALUE(JSON_VALUE(summary, '$._protocol'))                       AS http_protocol,
  ANY_VALUE(JSON_VALUE(summary, '$.https'))                           AS https,
  ANY_VALUE(CAST(JSON_VALUE(summary, '$.bytesTotal') AS INT64))       AS total_bytes,
  ANY_VALUE(CAST(JSON_VALUE(summary, '$.reqTotal')   AS INT64))       AS requests,
  -- Hiệu năng (Core Web Vitals)
  ANY_VALUE(CAST(JSON_VALUE(custom_metrics.performance,
            '$.lcp_elem_stats.renderTime') AS FLOAT64))               AS lcp_render_ms
FROM `httparchive.crawl.pages`,
  UNNEST(technologies) AS t
WHERE date='2026-06-01' AND client='desktop' AND is_root_page=TRUE
  AND rank <= 100000000000
GROUP BY domain, rank
ORDER BY rank, domain;