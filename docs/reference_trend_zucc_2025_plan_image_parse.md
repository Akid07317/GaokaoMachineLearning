# ZUCC 2025 Guangxi Plan Image Parse Preview

Generated: 2026-05-16

This preview parses the official ZUCC 2025 Guangxi plan image into major-level plan rows. It remains a source-packet parse preview only because the official image does not print the Guangxi institution-professional-group code.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_zucc_2025_plan_image_parse_preview.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_rollup.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_qa.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_exclusion_log.csv`

## Parsed Result

- Major rows: 17
- 广西物 plan sum: 80
- 广西史 plan sum: 10
- Official image total row: 广西物 80, 广西史 10

## Hold Reason

The source is useful for field thickness, but not yet a calibration row. The image has no group code, so the queue's `13021-102` candidate must be verified against Guangxi exam-authority group lines before conversion to group-year trend evidence.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. This preview does not write canonical/ML data and does not touch the 32-school decision pool.
