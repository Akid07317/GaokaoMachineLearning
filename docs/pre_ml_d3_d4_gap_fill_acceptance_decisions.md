# D3/D4 Gap-Fill Acceptance Decisions

更新时间：2026-05-14

本文件记录 `D3_gap_fill_acceptance_pending_decision` / `D4_gap_fill_caution_acceptance_pending_decision` 的本地补洞接受判断。

## 1. 结论

3 所 D3/D4 学校完成 GPT 复核覆盖表。

分布：

- 2 所建议 `accept_gap_fill_then_review`，可生成正式补洞应用层后重刷为 G1 复核候选。
- 1 所建议 `accept_gap_fill_with_note`，只能生成带备注补洞应用层后重刷为 G2 caution 复核候选。
- 0 所建议 `reject_gap_fill`。
- 0 所建议 `hold_before_ml`。

ML 入口继续关闭。

## 2. 决策规则

本轮只接受满足以下条件的本地补洞候选：

- `manual_acceptance_required = true`
- 候选来源为 `official`
- 候选年份为 2025
- 候选科类为物理类
- 候选批次为本科普通批
- 候选院校专业组数量大于 0
- 候选最低分和最低位次均存在
- 候选用途仍为 `local_gap_fill_candidate_only_not_auto_ml_input`

D3 学校若预览后达到 `G1_ready_for_human_gpt_review_gate_candidate` 且 `preview_gap_signature = complete_enough`，则建议 `accept_gap_fill_then_review`。

D4 学校若只能达到 `G2_ready_with_caution_for_review_gate_candidate`，则建议 `accept_gap_fill_with_note`，并保留 caution/隔离备注。

## 3. 学校决策表

| 学校 | 决策 | 证据等级 | 候选最低分 | 候选最低位次 | 候选组数 | 预览闸门 | 预览缺口 | 后续要求 |
|---|---|---|---:|---:|---:|---|---|---|
| 河北工业大学 | accept_gap_fill_then_review | A_gap_fill_accept_g1_candidate | 546 | 27014 | 4 | G1_ready_for_human_gpt_review_gate_candidate | complete_enough | none |
| 太原理工大学 | accept_gap_fill_then_review | A_gap_fill_accept_g1_candidate | 522 | 41040 | 1 | G1_ready_for_human_gpt_review_gate_candidate | complete_enough | none |
| 北京邮电大学本科招生网 | accept_gap_fill_with_note | B_gap_fill_accept_g2_caution_candidate | 572 | 15122 | 4 | G2_ready_with_caution_for_review_gate_candidate | missing_plan | public_school_name_label_cleanup_optional; plan_side_still_missing_keep_caution; fallback_source_resolution_keep_isolated |

## 4. 产物

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv`
- `reports/engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_school_summary.csv`
- `reports/engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions.py`

## 5. 下一步

下一步应生成正式补洞应用层，并在不进入 ML 的前提下重刷 readiness、handoff、workbench 和 gate status。

预期重刷方向：

- 河北工业大学：G1 candidate
- 太原理工大学：G1 candidate
- 北京邮电大学：G2 caution candidate，保留 missing_plan 与 fallback 隔离备注
