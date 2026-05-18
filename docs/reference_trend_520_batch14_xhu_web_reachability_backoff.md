# Reference Trend 520 Batch14 XHU Web Reachability Backoff

Generated: 2026-05-16

Purpose: preserve the 西华大学 batch14 official-source evidence discovered this
run without promoting it into source-packet intake, reference_trend_pool,
canonical, ML, or the 32-school decision_pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_xhu_web_reachability_backoff_preview.csv`
- `reports/reference_trend_520_batch14_xhu_web_reachability_backoff_rollup.csv`
- `reports/reference_trend_520_batch14_xhu_web_reachability_backoff_qa.csv`
- `reports/reference_trend_520_batch14_xhu_web_reachability_backoff_exclusion_log.csv`

## Evidence Summary

- Official 2025 charter found: `https://zb.xhu.edu.cn/72/65/c7906a225893/page.htm`.
  It confirms the 2025 admissions document and says province/major plans follow
  provincial admissions authorities, but it does not publish Guangxi
  院校专业组 plan rows.
- Official 2024 plan announcement found:
  `https://zb.xhu.edu.cn/33/fd/c7892a209917/page.htm`. It is useful historical
  context but only exposes aggregate/e-guide context in web text, not static
  Guangxi physical ordinary group rows.
- Official portal `https://zb.xhu.edu.cn/` exists and exposes admissions-plan
  navigation via web index, but terminal cache attempts for the portal/article
  returned 412/SSL/empty-reply outcomes. This is now a backoff state.

## Boundary

All rows remain `reference_trend_pool_eligible=false`,
`calibration_eligible=false`, and `canonical_ml_entry_open=false`.

Next safe step: do not repeat the same terminal curl URLs. Continue only if an
exact 2025 Guangxi plan detail URL is discovered, or if the user approves a
browser/header/cookie route for auditable caching.
