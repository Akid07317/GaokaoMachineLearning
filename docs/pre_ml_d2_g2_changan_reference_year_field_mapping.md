# D2/G2 长安大学 reference year and field mapping

本轮处理 D2/G2 修复队列中的第三项：长安大学 `P1_reference_year_and_field_mapping`。

## 结论

- 2025 计划侧可确认：校方官方 API 已结构化 37 行广西物理类本科普通批计划，计划数合计 128。
- 2025 计划字段可确认：`plan_count`、`requirement`、`selection_group`、`source_url` 均来自长安大学官方 API。
- 2024 分数/位次侧可确认：校方官方 API 已结构化 32 行广西物理类本科普通批专业分数，最低分 568，最低位次 17775，最高分 602。
- 2025 广西官方投档线可作为最新 line candidate：普通组 101/102，最低分 545，最低位次 27533。
- 2025 的 501/502 国家专项和 759 预科类已隔离为 special line，不进入普通组最低分口径。
- 不建议直接把 2025 广西投档线写成校方 API 分数字段；如要使用，应另行人工接受为本地 admission-line supplement。
- 长安大学可从 `queued_for_row_fix` 推进到 `reference_year_field_mapping_preview_ready`，但仍保留 G2 caution 和 reference year 说明。
- ML/canonical 入口继续关闭。

## 口径判断

当前最稳的复核口径是：

- `plan_year = 2025`
- `score_reference_year = 2024`
- `latest_admission_line_year = 2025`
- `data_completeness = latest_plan_with_2024_official_api_score_rank_reference`

这意味着 2025 计划数和专业组相关字段可以进入复核材料；分数/位次仍以 2024 校方 API 专业分数作为可比 reference。2025 广西官方投档线只作为候选补充，不自动替代校方 API 分数字段。

## 本轮产物

- `scripts/build_engineering_pre_ml_d2_g2_changan_reference_mapping.py`
- `clean_data/engineering_guangxi_seed/changan_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/changan_reference_year_field_mapping_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `reports/engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_coverage_rollup.csv`
