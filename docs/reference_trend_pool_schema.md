# Reference Trend Pool Schema

日期：2026-05-16

## 定位

`reference_trend_pool` 是隔离趋势参考层，用于广西物理类本科普通批的位次波动、计划变化和院校专业组结构背景。它不等于 32 所 `decision_pool`，也不直接写 canonical/ML。

## 本轮落地文件

- `clean_data/engineering_guangxi_seed/reference_trend_source_packet_template.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_source_packet_local_seed_preview.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_seed_queue.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_intake_preview.csv`
- `reports/reference_trend_pool_schema_coverage_rollup.csv`
- `reports/reference_trend_pool_qa_report.csv`
- `reports/reference_trend_exclusion_log.csv`

## 基本单位

趋势池基本单位是 `院校专业组-year`，不是学校。

## Intake Preview 字段

`trend_record_id`, `year`, `province`, `batch`, `subject_category`, `university_code`, `university_name`, `group_code`, `group_year_key`, `min_score`, `min_rank_est`, `min_rank_low`, `min_rank_high`, `rank_source_method`, `plan_count`, `has_group_code`, `has_min_score`, `has_min_rank`, `has_plan_count`, `round_type`, `special_type_detected`, `confidence_tier`, `trend_pool_role`, `calibration_eligible`, `qa_status`, `qa_flags`, `source_id`, `source_url`, `source_owner`, `source_title`, `raw_source_layer`, `decision_pool_boundary`, `canonical_ml_entry_open`, `notes`

## Source Packet 字段

`source_id`, `source_url`, `source_owner`, `source_title`, `published_date`, `year`, `province`, `batch`, `subject_category`, `round_type`, `university_name`, `university_code`, `source_contains_group_code`, `source_contains_min_score`, `source_contains_min_rank`, `source_contains_plan_count`, `special_type_detected`, `raw_file_path`, `collector_note`, `collector_confidence`, `source_packet_status`, `intended_layer`, `requires_network`, `requires_manual_approval`, `eligible_for_intake_preview`, `record_id`

## 首轮覆盖

- intake preview rows: 6626
- calibration eligible rows: 6075
- eligible unique university codes: 1089
- eligible rows 2024: 3067
- eligible rows 2025: 3008
- plan count available rows: 0

## 准入规则

- 必须是广西、本科普通批、物理类。
- 2024/2025 为严格新高考专业组口径样本。
- 必须有院校专业组代码、最低分、最低位次或可审计位次区间。
- 特殊类型、混合类型或口径不明记录只进 exclusion/hold，不进 strict calibration。
- 计划数缺失不阻止作为 rank/score trend 样本，但会标注 `has_plan_count=false`，不能用于计划数变化分析。

## 边界

- 不覆盖人工决策表。
- 不扩 32 所 decision pool。
- 不打开 canonical/ML。
- 联网新增资料必须先成为 source packet，再进入 intake preview 和 QA。
