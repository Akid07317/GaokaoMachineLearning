# P1 batch17 safe static QA subqueue

## Summary

从 marker 133 的 15 条 source-packet preview action queue 中，拆出 8 条可以在无新增批准条件下继续推进的 strict local/static QA rows，并将 7 条涉及浏览器/JS、条件 fetch、图片/OCR 或 WeChat 的 rows 写入 exclusion log。

本轮不联网、不缓存、不解析新网页、不 OCR、不打开微信或浏览器态；只为后续本地表格对齐、既有 preview QA、group mapping readiness、coverage/exclusion rollup 提供安全子队列。

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_safe_static_qa_subqueue.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_subqueue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_subqueue_qa.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_subqueue_exclusion_log.csv`

## Coverage

- Source action queue rows: 15
- Strict safe/static subqueue rows: 8
- Excluded rows: 7
- Subqueue rows with official min_score: 6
- Subqueue rows with selected min_rank: 0

## Boundaries

- `min_rank` 继续为空；等待 marker 136 的官方一分一档 raw cache/浏览器态批准后才能选择位次。
- `reference_trend_pool_eligible=false`，`calibration_eligible=false`，`canonical_ml_entry_open=false`。
- 不合并 32 所 decision_pool，不写 canonical/ML，不做 intake。

## QA

QA PASS: row balance、strict membership、browser/approval exclusion、OCR/WeChat/login exclusion、rank blank gate、intake/canonical/ML closure all pass.
