# P1 targeted thickening before rebuild

本报告只处理 data thickening queue 中的 P1 targeted thickening 8 行，生成非基线、非 canonical、非 ML 的补厚预览。未联网，未扩池，未写 canonical，未启动 ML。

## Summary

- preview rows: 8
- broad data collection needed: 0
- targeted collection/thickening needed: 8
- canonical rebuild assessment after thickening: 8
- canonical/ML entry: closed
- pool expansion: closed
- non-211 search: closed
- Deep Research mainline: closed

## Status counts

- preview_ready_thicken_group_mapping_before_rebuild: 1
- preview_ready_thicken_year_and_group_mapping_before_rebuild: 7

## P1 rows

- 北京交通大学招生与就业工作处: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径
- 福州大学: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径
- 华东理工大学本科招生网: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径
- 南京理工大学本科招生信息网: preview_ready_thicken_group_mapping_before_rebuild / 把选科组/招生专业映射到院校专业组口径
- 武汉理工大学本科招生网: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径
- 西南交通大学本科生招生信息公开: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径
- 郑州大学: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径
- 中国地质大学北京: preview_ready_thicken_year_and_group_mapping_before_rebuild / 补齐或解释目标年份缺口(2023)|把选科组/招生专业映射到院校专业组口径

## Decision

P1 的正确动作是本地定点补厚，不是继续搜学校。补齐目标年份、最低位次和专业组映射后，仍然只进入 canonical rebuild assessment；canonical/ML 入口保持关闭。

## Output files

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv`
- `reports/engineering_pre_ml_p1_targeted_thickening_before_rebuild_coverage_rollup.csv`
- `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`
