# Reference Trend 520 P0 PDF Text Extract Preview

Date: 2026-05-16

Scope: local text extraction for cached PDF rows from `reference_trend_520_p0_cached_parse_action_queue.csv`. This is only a readability and evidence preview. It does not infer Guangxi group-year records, does not create source_packet rows, and does not open reference_trend_pool/canonical/ML.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview_text/`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_rollup.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_qa.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_exclusion_log.csv`

## Coverage

- PDF preview rows: 1
- QA status: PASS

## Status Counts

- `text_extracted_layout_unverified`: 1

## Boundary

The extracted text can support a later manual table QA. Because the PDF text does not itself establish Guangxi subject/group mapping, no row is eligible for reference trend intake or calibration at this stage.
