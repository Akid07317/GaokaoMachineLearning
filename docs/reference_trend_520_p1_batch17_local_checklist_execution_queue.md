# P1 batch17 local checklist execution queue

## Summary

本轮读取 marker 140 action board，仅抽取不需要用户批准的本地 checklist/backoff 路由项。未联网、未抓取新页面、未 OCR、未打开浏览器/form/header/cookie/微信状态，也未选择最低位次。

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_local_checklist_execution_queue.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_execution_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_execution_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_execution_queue_exclusion_log.csv`

## Findings

- Input action board rows: 25
- Local checklist queue rows: 8
- Excluded approval/raw-artifact/non-local rows: 17
- Queue lanes: group_boundary_checklist=1, local_placeholder_cache_needed=1, official_only_discovery_backoff=5, static_table_alignment_checklist=1

## Boundary

This is a no-fetch routing/checklist layer. Every row keeps `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
