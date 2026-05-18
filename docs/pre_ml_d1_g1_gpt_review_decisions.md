# D1/G1 GPT Review Decisions

更新时间：2026-05-13

本文件记录第一批 `D1_ready_now_clean_pending_decision` / `G1_ready_for_human_gpt_review_gate` 学校的 GPT 复核闸门决策。

## 1. 结论

8 所 D1/G1 学校全部建议 `accept_for_review_gate`。

这一步只表示这些学校可以进入人工/GPT 复核闸门后的下一层 canonical 准备；不表示已经允许启动机器学习。

ML 入口仍保持关闭，直到 D2/G2、D3/D4 和 canonical snapshot/trend 重建完成后再单独判断。

## 2. 决策规则

本轮只对同时满足以下条件的学校给出 `accept_for_review_gate`：

- `decision_register_lane = D1_ready_now_clean_pending_decision`
- `gate_status = G1_ready_for_human_gpt_review_gate`
- `readiness_band = M1_ready_for_pre_ml_review`
- `data_completeness = plan_and_score`
- `reference_year = latest_year = 2025`
- `resolution_status = exact_ready`
- `trend_available = true`
- `blocker_class = none`
- `gap_signature = complete_enough`
- 计划侧和分数侧都有结构化行数与官方来源 URL

## 3. 学校决策表

| 学校 | 决策 | 最低分 | 最低位次 | 计划数 | 趋势信号 | 来源状态 | 剩余提醒 |
|---|---:|---:|---:|---:|---|---|---|
| 北京交通大学招生与就业工作处 | accept_for_review_gate | 609 | 4541 | 109 | rank_hotter | exact_ready | public_school_name_label_cleanup_optional |
| 福州大学 | accept_for_review_gate | 560 | 20173 | 133 | rank_cooler | exact_ready | none |
| 华东理工大学本科招生网 | accept_for_review_gate | 593 | 7957 | 47 | rank_cooler | exact_ready | public_school_name_label_cleanup_optional |
| 南京理工大学本科招生信息网 | accept_for_review_gate | 604 | 5539 | 72 | rank_cooler | exact_ready | public_school_name_label_cleanup_optional |
| 武汉理工大学本科招生网 | accept_for_review_gate | 592 | 8451 | 258 | rank_hotter | exact_ready | public_school_name_label_cleanup_optional |
| 西南交通大学本科生招生信息公开 | accept_for_review_gate | 578 | 12990 | 164 | rank_cooler | exact_ready | public_school_name_label_cleanup_optional |
| 郑州大学 | accept_for_review_gate | 546 | 27014 | 115 | rank_cooler | exact_ready | none |
| 中国地质大学北京 | accept_for_review_gate | 566 | 17582 | 52 | rank_cooler | exact_ready | none |

## 4. 产物

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d1_g1_gpt_review_decisions_merged.csv`
- `reports/engineering_pre_ml_d1_g1_gpt_review_decisions_school_summary.csv`
- `reports/engineering_pre_ml_d1_g1_gpt_review_decisions_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_d1_g1_gpt_review_decisions.py`

## 5. 下一步

下一步处理 10 所 D2/G2 caution pending decision。

D2/G2 不应直接照搬 D1 规则，需要逐项核对 caution 原因：缺计划、缺位次、趋势缺失、reference year 不是最新、fallback/mixed source、score only/partial plan 等。
