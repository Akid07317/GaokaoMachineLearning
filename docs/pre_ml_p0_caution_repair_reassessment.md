# P0 caution repair / G2 reassessment preview

本报告只处理 data thickening queue 中的 P0 caution/row-fix 8 行，生成非基线、非 canonical、非 ML 的复评预览。未联网，未扩池，未写 canonical，未启动 ML。

## Summary

- preview rows: 8
- row fix accepted for reassessment: 5
- caution gate confirmed with note: 3
- broad data collection needed: 0
- targeted repair needed: 8
- canonical/ML entry: closed
- pool expansion: closed
- non-211 search: closed
- Deep Research mainline: closed

## P0 rows

- 北京工业大学: preview_ready_reassess_g2_after_rank_boundary_note / 补齐或解释目标年份缺口(2025)|补专业组/选科组到 canonical 口径的映射说明|确认 2025 分数不能替代 2024 位次
- 北京邮电大学本科招生网: preview_ready_reassess_g2_after_caution_note / 补齐或解释目标年份缺口(2024|2025)|补齐计划数或保留计划数缺失 caution|补齐趋势链路或保留 no_trend caution
- 长安大学: preview_ready_reassess_g2_after_reference_year_note / 补齐或解释目标年份缺口(2023)|补专业组/选科组到 canonical 口径的映射说明|确认 reference_year 不是 latest_year 的可比边界
- 合肥工业大学本科招生: preview_ready_reassess_g2_after_rank_boundary_note / 补齐或解释目标年份缺口(2023)|补专业组/选科组到 canonical 口径的映射说明|确认 reference_year 不是 latest_year 的可比边界|确认最低位次为派生值而非页面/API 字段|人工判定概览最低分与专业明细最低分口径
- 河海大学: preview_ready_reassess_g2_after_caution_note / 补齐或解释目标年份缺口(2023)|补齐计划数或保留计划数缺失 caution|补专业组/选科组到 canonical 口径的映射说明
- 华北电力大学: preview_ready_reassess_g2_after_source_identity_fix / 补齐或解释目标年份缺口(2023|2024)|补齐趋势链路或保留 no_trend caution|补专业组/选科组到 canonical 口径的映射说明|确认官方 payload URL 替代占位/推断 detail URL
- 南京航空航天大学招生网: preview_ready_reassess_g2_after_rank_boundary_note / 补齐或解释目标年份缺口(2023)|补专业组/选科组到 canonical 口径的映射说明|确认 reference_year 不是 latest_year 的可比边界|确认最低位次为派生值而非页面/API 字段
- 西安电子科技大学本科招生网: preview_ready_reassess_g2_after_caution_note / 补齐或解释目标年份缺口(2023|2024)|补齐趋势链路或保留 no_trend caution|补专业组/选科组到 canonical 口径的映射说明

## Decision

P0 的正确动作不是扩池，而是把已接受的 row-fix preview 和已确认的 caution note 转成 G2 复评边界。复评只处理年份、位次、趋势、专业组映射和来源身份备注；通过后也只能进入 canonical rebuild assessment，不能直接写 canonical/ML。

## Output files

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv`
- `reports/engineering_pre_ml_p0_caution_repair_reassessment_coverage_rollup.csv`
- `docs/pre_ml_p0_caution_repair_reassessment.md`
