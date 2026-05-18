# Reference trend 520 P1 batch16 action queue

Generated: 2026-05-17

## Scope

This queue turns batch16 official source-discovery preview rows into safe next actions. It does not cache, parse, OCR, replay forms, or create source-packet/intake/canonical rows.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_action_queue.csv`
- `reports/reference_trend_520_p1_batch16_action_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch16_action_queue_qa.csv`
- `reports/reference_trend_520_p1_batch16_action_queue_exclusion_log.csv`

## Route distribution

- context_only_hold_search_refinement: 6
- exact_official_page_cache_parse_preview: 2
- official_pdf_cache_then_text_extract_preview: 1
- official_plan_portal_or_page_drilldown: 5
- official_query_cache_parameter_review: 2
- special_type_boundary_manual_review_hold: 1

## Boundary

- Expected output layer is `p1_batch16_action_queue_only_not_source_packet_not_intake`.
- Browser/form replay still requires explicit approval if a static cache route is blocked.
- PDF/table routes require later local preview and QA before source packet rows.
- Canonical/ML and the 32-school decision pool remain closed.
