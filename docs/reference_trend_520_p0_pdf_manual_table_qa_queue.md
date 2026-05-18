# Reference Trend 520 P0 PDF Manual Table QA Queue

Date: 2026-05-16

Scope: candidate table lines extracted from the local PDF text preview. This queue is designed for human QA of the original PDF/table layout. It deliberately does not map numeric sequences to the Guangxi column because extracted PDF text can collapse blank cells.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_manual_table_qa_queue.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_rollup.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_qa.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_exclusion_log.csv`

## Coverage

- Manual QA rows: 31
- QA status: PASS

## Row Types

- `major_candidate_line`: 29
- `summary_or_total_line`: 2

## Boundary

The next safe step is visual/table-layout QA against the PDF, not automatic intake. All rows remain outside source_packet, reference_trend_pool, canonical, ML, and the 32-school decision_pool.
