# 原线程续作交接文档

## 1. 这份文档的用途

这份文档用于从当前自动化线程切回原主线程后继续推进 Guangxi gaokao 项目。

当前自动化线程已经把本地 pre-ML 数据整理推进到 **人工/GPT 复核闸门之前**。  
接下来原线程要做的不是重新整理这些本地表，而是处理两类事情：

1. 对已准备好的候选校做人工/GPT 复核决策
2. 如果要继续推进阻塞校，回到原线程处理网页、接口、登录态、403 或其他外部信息问题

## 2. 当前总状态

目标池仍为 **32 所 211 工科目标校**。

当前分层：

- 已全量进入 readiness：**32 / 32**
- 可直接进入人工/GPT 复核闸门：**18**
- 需先人工接受本地补洞候选：**3**
- 仍需原线程外部路线或人工路线：**11**
- 已进入 review gate decision register：**21**
- 当前已完成复核决策：**0**
- 当前仍在 ML 前：**是**

一句话结论：

> 本地 pre-ML 整理已经到闸门前；现在该做人工/GPT 复核决策，不能直接启动机器学习。

## 3. 原线程优先打开的表

### 第一优先：复核决策登记表

这张表是下一步主表：

- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv:1)

用途：

- 每所候选校一行
- `decision_status` 默认是 `pending_human_gpt_review_decision`
- `review_decision`、`reviewer`、`decision_time`、`decision_notes` 留空，等原线程复核后填写
- `decision_options` 已给出允许的决策选项
- `manual_acceptance_required = true` 的学校必须先处理补洞候选

### 第二优先：逐校 checklist

- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_checklist_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_checklist_merged.csv:1)

用途：

- 看每所学校要核对什么
- 看通过/失败后的路线
- 看 ML 边界说明

### 第三优先：一致性审计

- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_consistency_audit_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_consistency_audit_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_consistency_audit_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_consistency_audit_coverage_rollup.csv:1)

当前结果：

- 审计覆盖：**32 / 32**
- `consistency_ok`: **32**
- `consistency_needs_attention`: **0**

用途：

- 确认 readiness、handoff、workbench、gate、candidate pack、checklist、pipeline status 没有行数或学校集合错位

## 4. 21 所候选校怎么处理

当前 21 所候选校分四类：

- `D1_ready_now_clean_pending_decision`: **8**
- `D2_ready_now_caution_pending_decision`: **10**
- `D3_gap_fill_acceptance_pending_decision`: **2**
- `D4_gap_fill_caution_acceptance_pending_decision`: **1**

处理顺序建议：

1. 先处理 `D1` 的 8 所 clean ready
2. 再处理 `D2` 的 10 所 caution ready，重点看备注和来源精度
3. 最后处理 `D3/D4` 的 3 所补洞候选

可直接复核的 18 所：

- 使用 decision register + checklist
- 核对学校名、年份、计划数、最低分、位次、来源回链
- 决策只能写入登记表，不能直接进入 ML

需要先接受补洞候选的 3 所：

- 北京邮电大学
- 河北工业大学
- 太原理工大学

对应候选来源：

- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_local_gap_fill_candidates_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_local_gap_fill_candidates_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gap_fill_impact_preview_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gap_fill_impact_preview_merged.csv:1)

候选值：

- 北京邮电大学：2025 普通批主校候选最低分 `572`，位次 `15122`，仍缺计划侧，只能进 G2 带备注候选
- 河北工业大学：2025 普通批候选最低分 `546`，位次 `27014`，可预览进 G1 候选
- 太原理工大学：2025 普通批候选最低分 `522`，位次 `41040`，可预览进 G1 候选

## 5. 11 所仍需原线程处理的学校

当前还有 **11 所**属于：

- `blocked_or_manual_route_before_review_gate`

这些学校不适合继续在本地自动化线程里推进。  
如果原线程要继续推进它们，可能需要：

- 新增网页发现
- 官方接口探测
- 登录态或浏览器态
- 403/header replay 处理
- 人工查证或人工路线

自动化线程此前明确禁止这些动作，所以这些工作应在原线程里做。

## 6. 关键本地产物清单

当前主链文件：

- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_workbench_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_workbench_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gate_status_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gate_status_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_candidate_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_candidate_pack_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_checklist_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_checklist_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_consistency_audit_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_consistency_audit_merged.csv:1)
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv:1)

状态总表：

- [/Users/don/Documents/New project/reports/engineering_pipeline_status.csv](/Users/don/Documents/New%20project/reports/engineering_pipeline_status.csv:1)

完整自动化接手文档：

- [/Users/don/Documents/New project/docs/gpt55_takeover_handoff.md](/Users/don/Documents/New%20project/docs/gpt55_takeover_handoff.md:1)

## 7. 可复跑脚本

如需重刷当前本地闸门层，可按这个顺序复跑：

```bash
python3 scripts/build_engineering_pre_ml_review_gate_candidate_pack.py
python3 scripts/build_engineering_pre_ml_review_gate_checklist.py
python3 scripts/build_engineering_pre_ml_review_gate_consistency_audit.py
python3 scripts/build_engineering_pre_ml_review_gate_decision_register.py
python3 scripts/build_engineering_pipeline_status.py
```

不要在这些脚本之后直接启动模型训练。

## 8. 原线程下一步建议

建议原线程按这个顺序做：

1. 打开 decision register
2. 先完成 18 所直接复核候选的人工/GPT 决策
3. 决定是否接受 3 所本地补洞候选
4. 如果接受补洞候选，再生成正式补洞应用层，并重刷 readiness / handoff / workbench / gate status
5. 对剩余 11 所，决定是否开启原线程的网页、接口、登录态或 403 路线
6. 所有复核和人工确认完成后，再讨论是否进入 ML

## 9. 明确不要做的事

在复核决策完成前，不要做：

- 模型训练
- 自动特征选择
- 概率校准
- 正式回测
- 把补洞候选自动写成 ML 输入

如果要推进 11 所阻塞校，需要回原线程处理外部信息，不要让当前自动化线程继续尝试。
