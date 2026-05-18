# P1 batch17 safe static QA local artifact inventory

## Summary

本轮读取 marker 137 的 8 条 strict safe/static QA rows，并仅用本地已有 batch17 文件建立 artifact inventory。未联网、未打开浏览器、未 OCR、未抓取微信/JS/form/header/cookie 来源。

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory_rollup.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory_qa.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory_exclusion_log.csv`

## Findings

- Inventory rows: 8
- Rows with official min_score retained for QA: 6
- Rows with selected min_rank: 0
- Rows with local parsed/readiness artifacts available now: 1
- Rows still excluded from intake because local parse/mapping/rank artifact is incomplete: 7

## Boundary

`min_rank` remains blank. `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row. The 32-school decision_pool remains untouched.
