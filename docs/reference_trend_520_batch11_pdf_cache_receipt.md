# Reference Trend 520 Batch11 PDF Cache Receipt

Generated: 2026-05-16

Scope: record locally cached official PDFs and table-extraction guardrails.

Outputs:
- `clean_data/engineering_guangxi_seed/reference_trend_520_batch11_pdf_cache_receipt_preview.csv`
- `reports/reference_trend_520_batch11_pdf_cache_receipt_rollup.csv`
- `reports/reference_trend_520_batch11_pdf_cache_receipt_qa.csv`
- `reports/reference_trend_520_batch11_pdf_cache_receipt_exclusion_log.csv`

Cached assets:
- 山东科技大学 (76): `raw_sources/reference_trend/batch11_official/sdust_2025_plan.pdf`, 204934 bytes, cached_text_pdf_hold_for_reliable_table_extraction.
- 惠州学院 (85): `raw_sources/reference_trend/batch11_official/hzu_2025_out_of_province_plan.pdf`, 482100 bytes, cached_text_pdf_hold_for_reliable_table_extraction.

Boundary:
- This is cache receipt/preflight only.
- The PDFs contain visible web text layers, but local table-aware extraction is not available.
- No flattened-text inference is used for Guangxi column counts.
- `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`.

Rollup:
- cached_pdf_rows: 2 山东科技大学, 惠州学院.
- cached_pdf_total_bytes: 687034
- web_text_layer_present_rows: 2
- local_parser_unavailable_rows: 2 pdftotext/qpdf/mutool/gs unavailable.
- reference_trend_pool_eligible_rows: 0 Receipt/preflight only.
- calibration_eligible_rows: 0 No group-year rows opened.
- canonical_ml_entry_open: false
- status::cached_text_pdf_hold_for_reliable_table_extraction: 2
