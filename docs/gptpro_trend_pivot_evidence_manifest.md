# GPT Pro trend pivot evidence pack manifest

## Purpose

This pack is for asking web GPT Pro whether the Guangxi gaokao project should pivot from a 32-school-only decision pool toward a separate reference trend pool, and whether two parallel threads should be used:

- one thread for source/data collection;
- one thread for data structuring, schema, QA, and integration.

## Core conclusion to test

The current 32-school pool is useful as a high-confidence decision pool, but is too small and too selective to represent admissions trends. Trend work should use an isolated reference trend pool built at the college-major-group-year level.

## Files and what they prove

### Prompt

- `docs/gptpro_trend_pivot_prompt.md`
  - The exact prompt to paste into web GPT Pro.

### Pivot judgment

- `docs/trend_reference_pool_pivot.md`
  - Records the revised architecture: 32-school decision pool vs reference trend pool.
  - States why trend learning should use group-year samples and why broad uncontrolled expansion is different from a trend pool.

### Full project summary

- `docs/project_bottleneck_summary_pack.md`
  - Full narrative handoff of project bottleneck, pre-ML status, post-human decisions, data sufficiency audit, and P0/P1 outputs.

### Data sufficiency

- `docs/pre_ml_data_sufficiency_audit.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_sufficiency_audit_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv`
- `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`
- `reports/engineering_pre_ml_data_thickening_priority_queue_coverage_rollup.csv`

Key metrics:

- audited schools = 32
- broad data collection needed = 0 for the 32-school decision pool
- targeted collection/thickening needed = 16
- canonical rebuild assessment ready = 10
- P0 caution repair / G2 reassessment = 8
- P1 targeted thickening before rebuild = 8
- G4 source reachability only = 11

### Post-human decision state

- `docs/pre_ml_post_human_decision_intake.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_intake_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_status_preview_merged.csv`
- `reports/engineering_pre_ml_post_human_decision_intake_coverage_rollup.csv`

Key metrics:

- post-human decision intake rows = 18
- gate decision confirmed rows = 13
- row fix acceptance confirmed rows = 5
- targeted repair/reassessment rows = 8
- broad data collection rows = 0

### P0/P1 repair and thickening

- `docs/pre_ml_p0_caution_repair_reassessment.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv`
- `reports/engineering_pre_ml_p0_caution_repair_reassessment_coverage_rollup.csv`

Key metrics:

- P0 preview rows = 8
- row fix accepted = 5
- caution gate confirmed with note = 3

- `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv`
- `reports/engineering_pre_ml_p1_targeted_thickening_before_rebuild_coverage_rollup.csv`

Key metrics:

- P1 preview rows = 8
- targeted thickening needed = 8
- broad data collection needed = 0
- 7 rows need 2023 year gap + professional group mapping
- 1 row needs professional group mapping only

### Existing decision-pool operating state

- `docs/pre_ml_human_gpt_review_action_board_and_gate_closeout.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_action_board_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_final_gate_closeout_merged.csv`
- `reports/engineering_pre_ml_human_gpt_review_action_board_coverage_rollup.csv`
- `reports/engineering_pre_ml_final_gate_closeout_coverage_rollup.csv`
- `clean_data/engineering_guangxi_seed/guangxi_source_resolution_matrix_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_master_operating_board_merged.csv`

These files show the decision-pool state and why it should remain separate from a lower-confidence trend pool.

### Non-211 discovery / possible trend candidates

- `docs/non211_authoritative_expansion_notes.md`
- `reports/non211_authoritative_todo.csv`
- `reports/non211_authoritative_discovery_candidates_priority.csv`

These files are not clean decision-pool inputs. They are candidate material for an isolated reference trend pool or discovery thread.

## Question for GPT Pro

Given this evidence, should the next phase be:

1. Continue polishing only the 32-school decision pool;
2. Expand the decision pool;
3. Create a separate reference trend pool while keeping the decision pool closed;
4. Split work into two threads: source collection and data structuring?

The expected answer should include concrete next steps, schemas, source criteria, confidence tiers, and a 48-hour execution plan.
