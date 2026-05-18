# D2/G2 GPT Review Decisions

更新时间：2026-05-13

本文件记录第二批 `D2_ready_now_caution_pending_decision` / `G2_ready_with_caution_for_review_gate` 学校的 GPT 复核闸门决策。

## 1. 结论

10 所 D2/G2 学校完成 GPT 复核覆盖表。

分布：

- 2 所建议 `accept_for_review_gate`，但必须保留 caution 标记。
- 5 所建议 `request_row_fix`，先修字段/来源后再进入下一层。
- 3 所建议 `hold_before_ml`，暂缓进入 canonical/ML 准备。

ML 入口继续关闭。

## 2. 决策规则

D2/G2 不使用 D1/G1 的 clean accept 规则，而按 caution 类型拆分：

- `B_caution_gate_accept`：来源为 `exact_ready`，无 blocker，2025 口径基本成立，仅有有限字段备注，如趋势缺失或总计划数联动待补。
- `C_row_fix_required`：已有可修复来源，但存在 reference year 不是最新、score/rank 字段需确认、混合来源、占位来源 URL 或计划联动缺口。
- `D_hold_before_ml`：fallback 依赖较重，且叠加缺计划、缺趋势、非 2025 freshness 或结构化计划行缺失。

遇到 `yoursite.com`、`example.com`、`localhost` 等占位 URL 时，即使其他字段标为 `exact_ready`，也先判为 `request_row_fix`。

## 3. 学校决策表

| 学校 | 决策 | 证据等级 | 最低分 | 最低位次 | 计划数 | 趋势信号 | 来源状态 | 必要修正 |
|---|---|---|---:|---:|---:|---|---|---|
| 河海大学 | accept_for_review_gate | B_caution_gate_accept | 583 | 11210 | 0 | rank_cooler | exact_ready | total_plan_count_or_plan_linkage_needs_fill |
| 西安电子科技大学本科招生网 | accept_for_review_gate | B_caution_gate_accept | 592 | 8483 | 135 | no_trend | exact_ready | trend_missing_or_unverified |
| 北京工业大学 | request_row_fix | C_row_fix_required | 595 | 8700 | 0 | rank_cooler | mixed_ready | fresh_2025_record_needed; plan_side_needs_structured_fill; mixed_source_resolution_needs_upgrade |
| 长安大学 | request_row_fix | C_row_fix_required | 568 | 17775 | 0 | trend_available_unclassified | exact_ready | reference_year_not_latest; score_field_needs_confirm; rank_field_needs_confirm; total_plan_count_or_plan_linkage_needs_fill |
| 合肥工业大学本科招生 | request_row_fix | C_row_fix_required | 572 | 16236 | 0 | trend_available_unclassified | exact_ready | reference_year_not_latest; score_field_needs_confirm; rank_field_needs_confirm; total_plan_count_or_plan_linkage_needs_fill |
| 华北电力大学 | request_row_fix | C_row_fix_required | 579 | 12593 | 102 | no_trend | exact_ready | source_url_placeholder_needs_official_domain_fix; trend_missing_or_unverified |
| 南京航空航天大学招生网 | request_row_fix | C_row_fix_required | 618 | 3971 | 0 | trend_available_unclassified | exact_ready | reference_year_not_latest; score_field_needs_confirm; rank_field_needs_confirm; total_plan_count_or_plan_linkage_needs_fill |
| 东华大学 | hold_before_ml | D_hold_before_ml | 589 | 9315 | 0 | no_trend | fallback_ready | rank_field_needs_confirm; plan_side_needs_structured_fill; trend_missing_or_unverified; fallback_source_resolution_needs_upgrade |
| 广西大学 | hold_before_ml | D_hold_before_ml | 590 | 10150 | 0 | no_trend | fallback_ready | fresh_2025_record_needed; plan_side_needs_structured_fill; trend_missing_or_unverified; fallback_source_resolution_needs_upgrade |
| 苏州大学 | hold_before_ml | D_hold_before_ml | 573 | 15871 | 0 | score_hotter_only | fallback_ready | rank_field_needs_confirm; fresh_2025_record_needed; plan_side_needs_structured_fill; fallback_source_resolution_needs_upgrade |

## 4. 产物

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_gpt_review_decisions_merged.csv`
- `reports/engineering_pre_ml_d2_g2_gpt_review_decisions_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_gpt_review_decisions_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_d2_g2_gpt_review_decisions.py`

## 5. 下一步

下一步处理 3 所 D3/D4 本地补洞接受判断。

注意：D2/G2 中被判为 `request_row_fix` 或 `hold_before_ml` 的学校不应进入 canonical training layer。`accept_for_review_gate` 的两所也只能带 caution 标记进入复核闸门，进入 canonical/ML 前仍需完成对应备注项。
