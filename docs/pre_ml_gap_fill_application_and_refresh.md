# Pre-ML 本地补洞应用层与重刷结果

生成时间：2026-05-14

## 结论

已把 D3/D4 接受结果落成独立的正式本地补洞应用层，并在不覆盖原始基线表、不打开 ML 的前提下重刷 post-gap-fill 版本的 readiness、handoff、workbench 和 gate status。

本轮只改变 pre-ML 复核材料的预览层，不写入 canonical training layer。

## 应用结果

| 学校 | 应用结论 | post-gap-fill 闸门 | 备注 |
|---|---|---|---|
| 河北工业大学 | `accept_gap_fill_then_review` | `G1_ready_for_human_gpt_review_gate` | 本地补洞后具备最低分/位次，可进入人工/GPT 复核闸门。 |
| 太原理工大学 | `accept_gap_fill_then_review` | `G1_ready_for_human_gpt_review_gate` | 本地补洞后具备最低分/位次，可进入人工/GPT 复核闸门。 |
| 北京邮电大学本科招生网 | `accept_gap_fill_with_note` | `G2_ready_with_caution_for_review_gate` | 仅补入分数/位次候选，仍保留 `missing_plan` 与 fallback caution。 |

## 重刷后覆盖

- `pre_ml_model_readiness_post_gap_fill`：32 所。
- `pre_ml_handoff_pack_post_gap_fill`：21 所。
- `pre_ml_review_workbench_post_gap_fill`：21 所。
- `pre_ml_gate_status_post_gap_fill`：32 所。
- 可进入人工/GPT 复核闸门的学校从 18 所升至 21 所。
- `G1` 从 8 所升至 10 所。
- `G2` 从 10 所升至 11 所。
- `G3_local_gap_fill_needed` 从 3 所降至 0 所。
- `G4_blocked_or_manual_route` 仍为 11 所。

## ML 边界

ML 仍保持关闭。

这些 post-gap-fill 表只用于人工/GPT 复核闸门材料，不等同于 canonical snapshot/trend，也不应直接作为训练输入。下一步应优先处理 D2/G2 的 `request_row_fix` 项，再把 11 所 G4 单独拆到官方来源可达性支线。

## 本轮产物

- `scripts/build_engineering_pre_ml_gap_fill_application_layer.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_gap_fill_application_layer_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_post_gap_fill_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_post_gap_fill_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_workbench_post_gap_fill_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_gate_status_post_gap_fill_merged.csv`
- `reports/engineering_pre_ml_gap_fill_application_layer_school_summary.csv`
- `reports/engineering_pre_ml_gap_fill_application_layer_coverage_rollup.csv`
- `reports/engineering_pre_ml_model_readiness_post_gap_fill_coverage_rollup.csv`
- `reports/engineering_pre_ml_handoff_pack_post_gap_fill_coverage_rollup.csv`
- `reports/engineering_pre_ml_review_workbench_post_gap_fill_coverage_rollup.csv`
- `reports/engineering_pre_ml_gate_status_post_gap_fill_school_summary.csv`
- `reports/engineering_pre_ml_gate_status_post_gap_fill_coverage_rollup.csv`
