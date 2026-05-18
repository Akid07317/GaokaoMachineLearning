# Reference trend 520 P1 batch17 JXUTCM source packet parse preview

Generated: 2026-05-17

## Scope

This preview parses the official Jiangxi University of Chinese Medicine 2025 Guangxi plan page into auditable source-packet preview rows for本科普通批物理类 only.

Source: https://zsxxw.jxutcm.edu.cn/info/1049/2562.htm

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview_exclusion_log.csv`

## Result

- Physical ordinary-batch major rows: 26
- Physical ordinary-batch plan sum: 62
- Source professional groups captured: 01, 02, 04, 06, 08
- Group plan sums: 01=13, 02=8, 04=4, 06=30, 08=7

## Boundary

- This is a source-packet parse preview, not reference-trend intake.
- The source page is plan-only and does not provide minimum score or rank.
- Source group codes are printed as short professional group codes; the page also says group number should follow the exam filling system, so alignment to queue group code `101` remains a QA hold.
- History rows and sports rows visible on the source are excluded from this physical ordinary-batch preview.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
