# Reference trend 520 P1 batch16 static cache execution queue

Generated: 2026-05-17

## Scope

This queue isolates batch16 rows that could be attempted through an auditable static cache path in a later run. It is not itself a network/cache/parse run.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_execution_queue.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_execution_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_execution_queue_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_execution_queue_exclusion_log.csv`

## Route distribution

- detail_url_discovery_before_cache: 5
- static_html_page_cache_candidate: 2
- static_pdf_cache_candidate: 1
- static_query_probe_candidate: 2

## Execution boundary

- Readiness rows read: 17
- Static-cache execution candidates: 10
- Network/cache was not performed in this run.
- Future execution must use official URLs only, with no cookie/header/form/browser-state replay.
- If a query or site requires browser/form state, stop and ask for approval.
- Source packet parse, reference trend intake, canonical/ML, and 32-school decision pool remain closed.
