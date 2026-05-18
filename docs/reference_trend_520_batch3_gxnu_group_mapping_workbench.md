# GXNU Group Mapping Workbench

Scope: 广西师范大学 2025 广西物理类本科普通批普通类计划解析行。

- Workbench rows: 53
- Parsed plan count sum: 2002
- Candidate exam authority groups: 151 / 152 / 155 / 156
- Manual fields: `selected_group_code`, `selected_decision`, `reviewer`, `decision_notes`

Boundary: this is a manual mapping workbench only. It does not open reference trend intake, canonical, ML, or the 32-school decision pool.

QA:
- input_parse_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_batch3_t1_source_packet_parse_preview.csv)
- candidate_groups_present: PASS (151|152|155|156)
- workbench_row_count: PASS (53 rows)
- plan_count_checksum: PASS (workbench=2002; source_ready_rows=2002)
- manual_decision_fields_blank: PASS (selected_group_code/selected_decision/reviewer/decision_notes remain blank.)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)
