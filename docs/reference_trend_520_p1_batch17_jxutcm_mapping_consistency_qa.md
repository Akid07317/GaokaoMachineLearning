# P1 batch17 JXUTCM mapping consistency QA

## Summary

本轮只使用本地已有 marker 122/123/124/138 产物，对江西中医药大学 `10412-101` 做 source short group 到广西考试院专业组的保守 mapping consistency QA。未联网、未抓取一分一档细页、未使用浏览器态、未选择最低位次。

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa_exclusion_log.csv`

## Findings

- Source plan major rows: 26
- Source group rows: 5
- Plan count sum: 62
- Only suffix candidate: source group `01` -> target `101`
- Official min_score linked to suffix candidate: `527`
- Selected min_rank rows: 0
- Accepted mapping rows: 0

## Boundary

`01 -> 101` remains a candidate-only suffix match, not an accepted mapping. The candidate group contains one `5+3` row, so special-type/boundary review is flagged before any calibration. Source groups `02/04/06/08` are kept only as adjacent source-packet context. `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
