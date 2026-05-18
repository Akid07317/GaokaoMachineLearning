# D2/G2 南京航空航天大学 reference year and field mapping

本轮处理 D2/G2 修复队列中的第五项：南京航空航天大学 `P1_reference_year_and_field_mapping`。

## 结论

- 2025 计划侧可确认：官方招生计划 API 已结构化 21 行广西物理类普通类计划，计划数合计 75。
- 2025 计划侧有学院字段，共覆盖 14 个学院；但选科/院校专业组字段缺失。
- 2025 plan seed 行的 `source_url` 为空，本轮预览使用 registry/API 查询 URL 回填为来源说明，不写入 canonical。
- 2024 专业分数 API 可确认：19 行广西物理类本科普通批专业分数，最低分 618，最高分 632。
- 2024 录取概况 API 可确认：普通类最低分 618、平均分 622、最高分 632，与专业明细最低分一致。
- 2024 API 不含最低位次；当前 `3971` 来自一分一档派生摘要，不是 API 原始字段。
- 2025 广西官方投档线可作为最新候选：普通组 101 最低分 615，最低位次 3507。
- 2025 的 303 组无备注但与 101 分组明显不同，本轮隔离为 `separate_unlabeled_group_candidate`，需人工判定是否接入。
- 2025 的 504 国家专项和 759 预科类已隔离为 special line。
- 南京航空航天大学可从 `queued_for_row_fix` 推进到 `reference_year_field_mapping_preview_ready`，但仍保留 G2 caution、rank 派生说明和 303 组边界 caution。
- D2/G2 request_row_fix 5 项均已有修复预览；下一步转向 G4 官方来源可达性支线。
- ML/canonical 入口继续关闭。

## 口径判断

当前最稳的复核口径是：

- `plan_year = 2025`
- `score_reference_year = 2024`
- `data_completeness = latest_plan_with_2024_official_api_score_reference_rank_derived`
- `minimum_score = 618`
- `minimum_rank = 3971`

但这个口径必须附带说明：`minimum_score = 618` 来自 2024 官方专业分数 API 和录取概况 API，两层一致；`minimum_rank = 3971` 来自一分一档派生摘要。2025 广西投档线只作为 admission-line candidate，尤其 303 组需要单独判定。

## 本轮产物

- `scripts/build_engineering_pre_ml_d2_g2_nanhang_reference_mapping.py`
- `clean_data/engineering_guangxi_seed/nanhang_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/nanhang_reference_year_field_mapping_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `reports/engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_coverage_rollup.csv`
