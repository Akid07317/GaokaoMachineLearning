# Reference Trend 520 Batch3 T1 Source Packet Parse

Run time: 2026-05-16T14:56:06

This is a non-baseline, non-canonical and non-ML parse layer for the locally cached T1 official sources from batch 3.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch3_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch3_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch3_t1_source_packet_parse_exclusion_log.csv`
- `raw_sources/reference_trend/batch3_t1/unnc_2025_plan_text.txt`

## Result

- Parsed preview rows: 272
- Source-packet rows ready for group-code mapping: 53
- Legacy science-label rows needing group-code and subject-label mapping: 19
- Hold / exclusion rows: 200
- Reference trend pool eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry open rows: 0

## Source Notes

- 哈尔滨医科大学: Guangxi ordinary column total 37 and adjacent national-special total 13; ordinary science rows are parsed, but the table uses legacy `理/文` labels and has no Guangxi院校专业组 code.
- 广西师范大学: parsed 249 Guangxi 2025 rows; ordinary physical regular-batch rows 53 with plan total 2002; no Guangxi院校专业组 code, so rows remain mapping workbench only.
- 宁波诺丁汉大学: official PDF text extracted to local text, but column alignment is not safe enough for row expansion; kept as whole-school Sino-foreign boundary hold.

## Next Step

The safe next automated step is to process the next P0/P1 official source candidates from `reference_trend_520_plan_discovery_query_pack.csv` / `reference_trend_520_plan_source_packet_queue.csv`, or, if the user approves browser/OCR/form work, unblock the three batch3 T2 candidates.
