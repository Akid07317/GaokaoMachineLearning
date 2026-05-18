# Reference Trend 520 Batch3 UNNC PDF Column Alignment Preview

Run date: 2026-05-16

This package parses the cached official Ningbo Nottingham PDF text only far enough to align the Guangxi physical plan column. It is a source-packet preview and QA artifact, not a trend-pool intake.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_pdf_column_alignment_preview.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_qa.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_exclusion_log.csv`

## Result

- Physical rows detected: 17
- Provisional Guangxi physical plan sum: 20
- PDF summary Guangxi physical checksum: 20
- Same-line labels: 10; labels needing manual review: 7
- QA: 6 pass / 0 review / 0 fail

## Boundary

The checksum now matches the PDF's Guangxi physical summary, but several major labels still need manual alignment and the PDF does not contain Guangxi institution-major-group codes. All rows remain `eligible_for_intake_preview=false`, `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.

## Next Action

Use this preview as a manual label/group mapping workbench seed for 宁波诺丁汉大学 group 303. Do not promote rows until the major labels and exam-authority group mapping are accepted.
