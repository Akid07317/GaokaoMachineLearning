# Pre-ML data sufficiency audit

本报告审计 32 所主池学校的数据厚度：年份覆盖、计划/分数/位次字段、趋势、专业组或选科映射、post-human caution/row-fix 边界。未联网，未扩池，未写 canonical，未启动 ML。

## Summary

- audited schools: 32
- broad data collection needed: 0
- targeted collection/thickening needed: 16
- canonical rebuild assessment ready: 10
- canonical/ML entry: closed
- pool expansion: closed
- non-211 search: closed
- Deep Research mainline: closed

## Priority counts

- P0_caution_repair_or_g2_reassessment: 8
- P1_targeted_thickening_before_rebuild: 8
- P2_canonical_rebuild_assessment: 2
- P3_hold_or_missing_core_fields: 3
- P4_g4_source_reachability_only: 11

## Sufficiency bands

- S1_rebuild_assessment_ready: 2
- S2_rebuild_possible_group_mapping_thin: 12
- S3_score_rank_years_present_plan_or_group_thin: 1
- S4_hold_not_sufficient: 3
- S4_too_thin_for_rebuild: 3
- S5_source_blocked_not_sufficient: 11

## Targeted Queue

- P0_caution_repair_or_g2_reassessment / 北京工业大学: missing_target_years|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 北京邮电大学本科招生网: missing_target_years|missing_plan_count|missing_canonical_trend|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 长安大学: missing_target_years|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 合肥工业大学本科招生: missing_target_years|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 河海大学: missing_target_years|missing_plan_count|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 华北电力大学: missing_target_years|missing_canonical_trend|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 南京航空航天大学招生网: missing_target_years|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P0_caution_repair_or_g2_reassessment / 西安电子科技大学本科招生网: missing_target_years|missing_canonical_trend|professional_group_mapping_not_canonical_ready|post_human_caution_or_repair_boundary
- P1_targeted_thickening_before_rebuild / 北京交通大学招生与就业工作处: missing_target_years|professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 福州大学: missing_target_years|professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 华东理工大学本科招生网: missing_target_years|professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 南京理工大学本科招生信息网: professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 武汉理工大学本科招生网: missing_target_years|professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 西南交通大学本科生招生信息公开: missing_target_years|professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 郑州大学: missing_target_years|professional_group_mapping_not_canonical_ready
- P1_targeted_thickening_before_rebuild / 中国地质大学北京: missing_target_years|professional_group_mapping_not_canonical_ready
- P3_hold_or_missing_core_fields / 东华大学: missing_target_years|missing_plan_count|missing_canonical_trend|professional_group_mapping_not_canonical_ready
- P3_hold_or_missing_core_fields / 广西大学: missing_target_years|missing_plan_count|missing_canonical_trend|professional_group_mapping_not_canonical_ready
- P3_hold_or_missing_core_fields / 苏州大学: missing_target_years|missing_plan_count|professional_group_mapping_not_canonical_ready
- P4_g4_source_reachability_only / 北京化工大学: missing_target_years|missing_plan_count|missing_minimum_score|missing_minimum_rank|missing_canonical_trend|professional_group_mapping_not_canonical_ready

## Decision

数据确实偏少，但不是继续广泛搜集学校。下一步应补厚主池：先处理 caution/row-fix 的 8 条定点重评，再处理年份/位次/专业组映射不足的学校；G4 只在人工批准后做官方来源可达性支线。

## Output files

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_sufficiency_audit_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv`
- `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`
- `reports/engineering_pre_ml_data_thickening_priority_queue_coverage_rollup.csv`
- `docs/pre_ml_data_sufficiency_audit.md`
