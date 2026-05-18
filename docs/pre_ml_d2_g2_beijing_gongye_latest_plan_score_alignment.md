# D2/G2 北京工业大学 Latest Plan-Score Alignment

生成时间：2026-05-14

## 结论

北京工业大学 `P1_latest_plan_score_alignment` 已生成本地修复预览。2025 计划侧可以补齐，2025 分数侧可以提供最新最低分，但 2025 分数材料没有最低位次，因此不能完全替代 2024 带位次可比记录。

本轮不覆盖基线表，不写入 canonical，不打开 ML。

## 核对结果

- 2025 广西物理类计划行：16 行。
- 2025 广西物理类计划数合计：46。
- 2025 广西物理类分数行：17 行。
- 2025 分数唯一专业键：15 个。
- 计划-分数匹配专业键：10 个。
- 仅计划侧出现：6 个。
- 仅分数侧出现：5 个。
- 2025 最低分：567。
- 2025 最低位次：缺失。
- 2024 best comparable rank：8700。

## 复核判断

`can_replace_2024_score = yes_with_caution`

2025 官方分数行可以提供最新最低分参考，但专业行存在计划/分数专业集合不完全一致、个别专业重复分数行的问题，需要带 caution。

`can_replace_2024_rank = no`

2025 分数行没有最低位次，不能替代 2024 带位次可比记录。北京工业大学仍应保留在 `G2_ready_with_caution_for_review_gate`，备注为 `missing_2025_rank|comparable_rank_note_required`。

## 当前状态

北京工业大学已从 `queued_for_row_fix` 推进到 `latest_plan_score_alignment_preview_ready`。

可进入下一步复核预览，但必须保留：

- `no_2025_rank` caution。
- 2024 rank 仅作为 best comparable reference。
- 2025 score 仅作为 latest score reference。
- canonical/ML 入口继续关闭。

## 本轮产物

- `scripts/build_engineering_pre_ml_d2_g2_beijing_gongye_alignment.py`
- `clean_data/engineering_guangxi_seed/beijing_gongye_latest_plan_score_alignment_row_preview.csv`
- `clean_data/engineering_guangxi_seed/beijing_gongye_latest_plan_score_alignment_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `reports/engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_coverage_rollup.csv`
