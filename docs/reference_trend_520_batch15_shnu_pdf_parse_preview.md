# Reference Trend 520 Batch15 Shanghai Normal University PDF Parse Preview

Generated: 2026-05-16

Purpose: cache and parse 上海师范大学 official 2025 out-province plan PDF into
a non-canonical source-packet preview for later Guangxi subject-route and
professional-group mapping.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_shnu_pdf_parse_preview.csv`
- `reports/reference_trend_520_batch15_shnu_pdf_parse_rollup.csv`
- `reports/reference_trend_520_batch15_shnu_pdf_parse_qa.csv`
- `reports/reference_trend_520_batch15_shnu_pdf_parse_exclusion_log.csv`

## Summary

- Official page: `https://ssdzsb.shnu.edu.cn/af/83/c26800a831363/page.htm`
- Official PDF: `https://ssdzsb.shnu.edu.cn/_upload/article/files/85/23/f796eb7c46f3884bb92c191a9052/3faafef1-d12a-4496-86cf-2b399dc5de72.pdf`
- Cached PDF: `raw_sources/reference_trend/batch15_official/shnu_2025_outprovince_plan.pdf`
- Parse status: `pdfplumber_tables_extracted`
- Guangxi rows extracted: 21
- Guangxi plan count sum: 154
- Special-boundary rows: 6

The PDF is useful plan-count evidence, but it is not a Guangxi professional-group
or subject-route split. All rows remain outside `reference_trend_pool`,
`canonical`, `ML`, and the 32-school decision_pool until mapping is resolved.
