# Reference Trend 520 Batch3 UNNC Label/Group Mapping Workbench

Run date: 2026-05-16

This workbench turns the Ningbo Nottingham PDF column-alignment preview into human-review rows. It protects manual decision fields and does not write reference_trend, canonical, or ML inputs.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_qa.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_exclusion_log.csv`

## Result

- Workbench rows: 17
- Rows with positive Guangxi physical plan count: 8
- Provisional Guangxi physical plan sum: 20
- Positive rows: 国际事务与国际关系=1, 英语=3, 国际经济与贸易=3, 国际商务=3, 计算机科学与技术=3, 数学与应用数学=1, 电气类(2+2)=1, 电气类=5
- QA: 6 pass / 0 review / 0 fail

## Manual Fields

Fill `selected_decision`, `reviewer`, and `decision_notes` only after checking the PDF visual layout and confirming that these rows map to exam-authority group 303. Valid decisions are `accept_label_group303_mapping`, `edit_label_then_accept`, `reject_row`, or `hold_for_pdf_visual_review`.

## Boundary

All rows remain `eligible_for_intake_preview=false`, `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false` until human acceptance.
