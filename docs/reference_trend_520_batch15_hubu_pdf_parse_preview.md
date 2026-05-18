# Reference Trend 520 Batch15 Hubei University PDF Parse Preview

Generated: 2026-05-16

Purpose: cache and parse 湖北大学 official 2025 province/major plan PDF into a
non-canonical source-packet preview for later professional-group mapping.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_hubu_pdf_parse_preview.csv`
- `reports/reference_trend_520_batch15_hubu_pdf_parse_rollup.csv`
- `reports/reference_trend_520_batch15_hubu_pdf_parse_qa.csv`
- `reports/reference_trend_520_batch15_hubu_pdf_parse_exclusion_log.csv`

## Summary

- Official plan column: `https://zsxx.hubu.edu.cn/zsxx/zsjh.htm`
- Official PDF: `https://xxgk.hubu.edu.cn/__local/0/3E/A6/5144BF67BAF45FED441FDBA3834_1D8D2799_1E3A1.pdf`
- Cached PDF: `raw_sources/reference_trend/batch15_official/hubu_2025_plan_pdf.pdf`
- PDF pages: 4; parse status: `pypdf_text_extracted`
- Guangxi major rows extracted: 46
- Extracted Guangxi plan sum: 152
- PDF total-row Guangxi plan count: 152

The PDF is useful plan-count evidence, but it is not a professional-group split.
All rows remain outside `reference_trend_pool`, `canonical`, `ML`, and the
32-school decision_pool until official group mapping is resolved.

## Boundary

`eligible_for_intake_preview=true_source_packet_preview_only` means the row is
usable as a source-packet preview for human/GPT mapping work. It does not mean
it is calibration-ready. `reference_trend_pool_eligible=false_until_group_code_and_subject_mapping`
for every row.
