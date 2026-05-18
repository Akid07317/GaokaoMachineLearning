# Reference Trend 520 Batch15 XBMU AJAX Reachability Backoff

Generated: 2026-05-16

Purpose: preserve 西北民族大学 official 2025 plan-search UI evidence without
performing browser/cookie/header/form replay or creating structured plan rows.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_preview.csv`
- `reports/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_rollup.csv`
- `reports/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_qa.csv`
- `reports/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_exclusion_log.csv`

## Summary

- Official plan UI: `https://zs.xbmu.edu.cn/static/front/xbmu/basic/html_web/zsjh.html`
- Cached HTML: `raw_sources/reference_trend/batch15_official/xbmu_2025_plan_page.html`
- AJAX parameter endpoint: `https://zs.xbmu.edu.cn/f/ajax_zsjh_param` -> `http_403`
- Static page has Guangxi filter: True
- Static page has plan templates/endpoints: True

The static page contains the plan-search UI and AJAX endpoint shapes, but the
terminal probe for the parameter endpoint returned `http_403` with body marker
`页面不存在`. The site certificate also failed normal TLS validation, so the
HTML cache is treated as reachability evidence only.

## Boundary

No browser, cookie/header replay, or form replay was attempted. No source-packet
intake rows, `reference_trend_pool`, `canonical`, `ML`, or 32-school
decision_pool data were written. Continue only with explicit approval or with a
separate official static export/PDF/table source.
