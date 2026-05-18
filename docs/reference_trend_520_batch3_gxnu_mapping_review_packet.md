# GXNU Mapping Review Packet

Scope: derived reviewer packet for 广西师范大学 2025 广西物理类本科普通批普通类计划 rows.

- Row-level packet rows: 53
- Plan count checksum: 2002
- Candidate groups: 151 / 152 / 155 / 156

Discipline rollup:
- 07 理学: 13 rows, plan 822
- 08 工学: 15 rows, plan 682
- 12 管理学: 9 rows, plan 126
- 05 文学: 4 rows, plan 108
- 04 教育学: 6 rows, plan 106
- 03 法学: 4 rows, plan 88
- 02 经济学: 2 rows, plan 70

QA:
- input_workbench_exists: PASS (clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_group_mapping_workbench.csv)
- packet_rows_match_workbench: PASS (packet=53; workbench=53)
- plan_count_checksum: PASS (packet=2002; workbench=2002)
- candidate_group_context_present: PASS (151|152|155|156)
- discipline_rollup_present: PASS (7 discipline families)
- no_auto_group_assignment: PASS (proposed_group_code is intentionally blank.)
- no_reference_trend_pool_or_canonical_ml: PASS (No trend/canonical/ML writes.)

Boundary: this packet helps manual mapping only. It does not assign groups or write reference trend/canonical/ML.
