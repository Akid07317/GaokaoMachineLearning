# Reference Trend 520 Batch15 Yangtze University Aggregate PDF Backoff

Generated: 2026-05-16

Purpose: cache and audit the official 长江大学 2025 plan PDF discovered in
batch15 while preventing it from being mistaken for a Guangxi source-packet.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_preview.csv`
- `reports/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_rollup.csv`
- `reports/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_qa.csv`
- `reports/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_exclusion_log.csv`

## Summary

- Official plan column: `https://zszc.yangtzeu.edu.cn/bkzn/zsjh.htm`
- Official PDF: `https://xxgk.yangtzeu.edu.cn/__local/3/55/84/AED89C4A8BF7FC02EED72A7D670_3AD1D955_3EF0F.pdf`
- Cached PDF: `raw_sources/reference_trend/batch15_official/yangtzeu_2025_plan_pdf.pdf`
- PDF pages: 1; parse status: `pypdf_text_extracted`
- Aggregate rows extracted: 17
- 普本物理组 aggregate plan: 6113
- Total aggregate plan: 9781

The PDF is useful official context but does not contain Guangxi province rows,
major rows, professional-group codes, minimum scores, or ranks. It is therefore
excluded from source-packet intake and kept as a backoff/context artifact.
