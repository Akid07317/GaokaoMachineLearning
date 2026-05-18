# GPT-5.5 project drift review prompt

## Purpose

This repository contains a Guangxi gaokao volunteer-planning data project. The current question is not whether more automation can be written, but whether the work has drifted away from the original goal.

Use this document as the entry point for a GPT-5.5 review.

## Original Goal

Move from a 32-school high-precision `decision_pool` toward a sustainable, isolated data-engineering pipeline:

- `reference_trend_pool`
- auditable `source_packet`
- QA and coverage reports

The 32-school pool remains a high-precision decision pool. It must not be merged into the statistical reference trend background. Web discovery and found evidence should only enter source packets, previews, QA, rollups, and reports. Canonical and ML entry points remain closed unless explicitly approved.

## Current Scale Snapshot

Measured locally on 2026-05-18:

- Project size: about `136M`
- Full file count including ignored/generated files: about `3796`
- `clean_data`: about `15M`
- `reports`: about `14M`
- `docs`: about `1.1M`
- `scripts`: about `5.3M`
- `reference_trend` related artifacts across docs/reports/seed: about `739`
- `reference_trend` docs: about `150`
- `reports` reference_trend files: about `435`
- `clean_data/engineering_guangxi_seed` reference_trend files: about `154`
- `build_reference_trend*` scripts: about `147`
- Handoff markers reached `145`

## Required Evidence Files

Read these first:

1. `docs/trend_reference_pool_pivot.md`
2. `docs/gpt54_reference_trend_pool_handoff.md`
3. `docs/reference_trend_520_p1_batch17_pipeline_readiness_rollup.md`
4. `docs/reference_trend_520_p1_batch17_user_approval_decision_sheet.md`
5. `docs/reference_trend_520_p1_batch17_gated_branch_decision_matrix.md`
6. `docs/reference_trend_520_p1_batch17_post_mapping_action_board.md`

If generated CSVs are available locally, also inspect:

1. `reports/reference_trend_520_p1_batch17_pipeline_readiness_rollup_rollup.csv`
2. `reports/reference_trend_520_p1_batch17_pipeline_readiness_rollup_qa.csv`
3. `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_pipeline_readiness_rollup.csv`
4. `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_user_approval_decision_sheet.csv`
5. `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gated_branch_decision_matrix.csv`

## Key Current Facts

Marker 145 says:

- `readiness_rows = 8`
- `automation_can_proceed_now_rows = 0`
- `unique_lookup_scores_waiting = 382|461|462|490|527`
- `reference_trend_pool_eligible_rows = 0`
- `calibration_eligible_rows = 0`
- `canonical_ml_entry_open = 0`
- QA checks pass

Interpretation: the workflow is not currently allowed to advance without an official raw artifact, browser-state approval, OCR/WeChat approval, or a local artifact supplied by the user.

## Review Questions

Please answer as a project drift auditor, not as an implementation agent.

1. Is this project drifting?
   - Not drifting
   - Mild drift
   - Moderate drift
   - Severe drift

2. If it is drifting, where?
   - Goal drift: has it moved away from reference trend pool construction?
   - Process drift: is it producing too many queues, approval sheets, and rollups without adding usable data?
   - Risk drift: has excessive conservatism made the pipeline unable to continue?
   - Boundary drift: has fear of canonical/ML contamination trapped everything in preview/report layers?

3. Which work is still valuable?
   - Identify artifacts that improve auditability, boundary control, source discipline, or QA.

4. Which work has low marginal value?
   - Especially inspect markers 126-145 for report-on-report patterns.

5. What should stop now?

6. What should be kept?

7. What exact user approval or official artifact is needed to resume useful work?

8. Should the heartbeat automation remain paused until those inputs exist?

## Desired Output

Start with one clear sentence.

Then provide a table:

`Evidence | Interpretation | Drift Judgment`

End with no more than 10 action recommendations.

