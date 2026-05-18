# Reference Trend 520 Batch15 Qinghai University Plan Readiness

Generated: 2026-05-16

Purpose: preserve the 青海大学 batch15 2025 plan source chain without promoting
it into source-packet intake, reference_trend_pool, canonical, ML, or the
32-school decision_pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_qhu_plan_readiness_preview.csv`
- `reports/reference_trend_520_batch15_qhu_plan_readiness_rollup.csv`
- `reports/reference_trend_520_batch15_qhu_plan_readiness_qa.csv`
- `reports/reference_trend_520_batch15_qhu_plan_readiness_exclusion_log.csv`

## Evidence Summary

- First-party official page cached: `raw_sources/reference_trend/batch15_qhu_2025_plan_official_page.html`
- Official URL: `https://zsw.qhu.edu.cn/zsxx/zszc/92a9bb561a4e4253a01988aec41e7333.htm`
- The cached official page title is 青海大学2025年招生计划 and it references an
  external Eqxiu poster: `https://s.eqxiu.com/s/yHplm9Zh?bt=yxy&eip=true`.
- The static first-party HTML does not expose structured 广西/物理/院校专业组
  plan rows, minimum score, minimum rank, or group code.

## Boundary

All rows remain `eligible_for_intake_preview=false`,
`reference_trend_pool_eligible=false`, `calibration_eligible=false`, and
`canonical_ml_entry_open=false`.

Next safe step: wait for approval before using browser render, OCR, or manual
transcription on the external poster. If approved, extract only auditable
广西物理类本科普通批 rows into a new preview/QA layer.
