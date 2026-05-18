# Reference trend 520 P1 batch17 source-packet preview action queue

Generated: 2026-05-17

## Scope

This queue turns marker 132 preview candidates into bounded next-action packets.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_source_packet_preview_action_queue.csv`
- `reports/reference_trend_520_p1_batch17_source_packet_preview_action_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_source_packet_preview_action_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_source_packet_preview_action_queue_exclusion_log.csv`

## Summary

- Source-packet preview action rows: 15
- Backoff exclusions: 5
- Safe local/static QA rows: 10
- Approval-sensitive rows: 5
- Reference trend eligible rows: 0
- Canonical/ML rows opened: 0

## Priority Counts

- `P0_ready_local_mapping_rank_join_QA`: 1
- `P0_static_html_table_alignment_QA`: 1
- `P1_candidate_plus_line_score_hold`: 5
- `P1_existing_candidate_filter_QA`: 2
- `P1_static_detail_page_retry_QA`: 1
- `P2_image_asset_manual_QA_packet`: 2
- `P2_static_api_probe_else_approval`: 2
- `P3_wechat_or_static_mirror_approval_needed`: 1

## Boundary

This artifact performs no network fetch, cache, parse, OCR, browser/form replay, login-state review, WeChat capture, reference trend intake, calibration, canonical/ML, or 32-school decision-pool update.
