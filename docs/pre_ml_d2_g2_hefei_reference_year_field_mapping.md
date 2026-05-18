# D2/G2 合肥工业大学 reference year and field mapping

本轮处理 D2/G2 修复队列中的第四项：合肥工业大学 `P1_reference_year_and_field_mapping`。

## 结论

- 2025 计划侧可确认：官方广西直达页原始提取 51 行；进入 seed 去重后为 42 行。
- 2025 普通批计划侧可确认：37 行，计划数合计 193。
- 2025 国家专项计划侧单独隔离：5 行，计划数合计 17。
- 2025 计划明细的选科/院校专业组字段缺失，不能直接映射成专业组层 canonical。
- 2024 专业明细分数可确认：seed 去重后 32 行，其中普通批 30 行、国家专项 2 行。
- 2024 专业明细最低分为 572，最高分为 619；页面专业明细不含最低位次。
- 当前 `16236` 位次来自一分一档派生摘要，不是合肥工业大学页面原始字段。
- 2024 省份概览最低分为 550，与专业明细最低分 572 存在 22 分差异，需要人工判定学校/校区/投档线口径。
- 2025 广西官方投档线可作为最新候选：合肥工业大学普通组 101/102，最低分 549，最低位次 25474。
- 合肥工业大学(宣城校区)已作为独立校区候选隔离，不自动并入当前 school_key。
- 合肥工业大学可从 `queued_for_row_fix` 推进到 `reference_year_field_mapping_preview_ready`，但仍保留 G2 caution、rank 派生说明和 campus scope caution。
- ML/canonical 入口继续关闭。

## 口径判断

当前最稳的复核口径是：

- `plan_year = 2025`
- `score_reference_year = 2024`
- `data_completeness = latest_plan_with_2024_direct_page_score_reference_rank_derived`
- `minimum_score = 572`
- `minimum_rank = 16236`

但这个口径必须附带说明：`minimum_score = 572` 来自 2024 专业明细最低分，`minimum_rank = 16236` 来自一分一档派生；官方直达页概览层另有 2024 物理类最低分 550。2025 广西投档线只作为 admission-line candidate，需人工接受并明确校区边界后才能接入。

## 本轮产物

- `scripts/build_engineering_pre_ml_d2_g2_hefei_reference_mapping.py`
- `clean_data/engineering_guangxi_seed/hefei_gongda_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/hefei_gongda_reference_year_field_mapping_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `reports/engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_coverage_rollup.csv`
