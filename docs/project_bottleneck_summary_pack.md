# 项目瓶颈总结包

更新时间：2026-05-13

## 1. 项目定位

本项目是广西新高考院校专业组志愿风险决策系统，不是单点分数线预测工具。

服务对象与口径：

- 广西本科普通批。
- 物理类，物化生可报。
- 重点面向 550-620 分区间。
- 211 及以上优先，偏计算机、电子信息、自动化、人工智能、软件工程、通信、数学、物理和工科方向。

最终输出应是每个可报院校专业组的：

- 最低投档位次分布。
- 录取概率区间。
- 冲稳保风险分层。
- 调剂风险。
- 专业接受度。
- 可解释原因。

关键纪律：

- 位次优先，不直接跨年混用分数。
- 院校专业组优先，不用学校最低分替代专业组。
- 只混合同口径数据：广西、物理类、本科普通批、普通类、第一次正式投档。
- 中外合作、民族班、专项、预科、征集志愿等特殊类型隔离或排除。
- 机器学习必须等 pre-ML 人工/GPT 复核闸门通过后再进入。

## 2. 当前主池状态

当前目标池为 32 所 211 工科目标校。

官方来源包：

- 32/32 学校进入来源包。
- 32/32 有 `plan_source_url`。
- 32/32 有 `score_source_url`。

pre-ML readiness：

- `M1_ready_for_pre_ml_review`: 8
- `M2_comparable_ready_with_note`: 10
- `M3_fill_gaps_then_review`: 3
- `M4_blocked_or_manual_route`: 11

pre-ML handoff pack：

- 18/32 学校进入 handoff pack。
- M1 = 8。
- M2 = 10。
- 18/18 都有计划来源和分数来源。
- 14 所达到 `exact_ready`。

来源精度矩阵：

- `exact_ready`: 15
- `mixed_ready`: 2
- `fallback_ready`: 15

pre-ML gate status：

- `G1_ready_for_human_gpt_review_gate`: 8
- `G2_ready_with_caution_for_review_gate`: 10
- `G3_local_gap_fill_needed`: 3
- `G4_blocked_or_manual_route`: 11
- 人工/GPT 复核候选合计：18/32

decision register：

- 21 所 pending。
- 18 所可直接复核。
- 3 所需要先人工接受本地补洞候选。
- 已完成复核决策：0。

## 3. 当前数据量级

现有结构化层已经不少，但真正同口径、可比较、能直接训练的记录仍然偏少。

主要量级：

- plan seed 约 538 行。
- score major seed 约 647 行。
- score summary seed 约 71 行。
- primary/canonical snapshot 为几十行量级。
- 带最低位次且可比的 canonical snapshot 只有主池覆盖层级。
- canonical trend 约 20 行。

判断：

- 原始行数不算少。
- 可直接进入 ML 的有效样本并不厚。
- 如果现在硬上机器学习，过拟合和口径混杂风险很高。

## 4. 当前瓶颈

真正瓶颈不是“没有任何数据”，而是本地 pre-ML 整理已经推到闸门前，但复核决策还没有落地。

当前卡点：

1. 21 所 decision register 仍是 pending。
2. 18 所可以直接进入人工/GPT 复核，但尚未逐校确认。
3. 3 所 G3 需要决定是否接受本地补洞候选。
4. 11 所 G4 属于 blocked/manual route，可能需要外部网页、接口、登录态、403/header replay 或人工查证。
5. 机器学习入口仍应关闭。

## 5. 扩池线索

已有一个非 211 扩池观察池雏形。

第一批候选基于教育部第二轮“双一流”名单和理工/工科匹配：

- 南京信息工程大学
- 西南石油大学
- 成都理工大学
- 天津工业大学
- 湘潭大学
- 山西大学
- 宁波大学
- 南京林业大学
- 上海科技大学
- 南方科技大学

当前状态：

- 这些学校只在 todo/discovery 层。
- 已有约 277 条 priority candidates。
- 尚未进入主 pre-ML 口径。
- 不应直接和 32 所 211 主池混合建模。

## 6. 建议决策问题

需要让网页版 GPT-5.5 Pro 判断的问题：

1. 当前是否应该立即扩充主数据池？
2. 如果扩，扩充边界是什么？
3. 如果不扩，应先处理哪一层瓶颈？
4. 样本扩充优先级如何排序：学校数、年份数、训练层级、院校专业组粒度、字段厚度？
5. 是否应该现在启用 Deep Research？
6. 如果启用，调查边界是否只限 11 所 blocked/manual route 的官方来源可达性？

## 7. 给网页版 GPT-5.5 Pro 的提问包

```text
请你作为网页版 GPT-5.5 Pro，对这个广西高考志愿项目做一次项目瓶颈判断。请不要实际启动 Deep Research，也不要泛泛而谈，只基于下面的项目包给出决策。

项目定位：
- 广西新高考本科普通批，物理类，物化生可报。
- 面向 550-620 分区间，211 及以上优先，偏计算机、电子信息、自动化、AI、软件工程、通信、数学、物理、工科方向。
- 输出目标不是单点分数预测，而是院校专业组风险决策：位次分布、录取概率区间、风险分层、调剂风险、专业接受度和解释原因。
- 原则：位次优先，院校专业组优先，只混合同口径数据；特殊类型隔离；机器学习必须先通过 pre-ML 人工/GPT 复核闸门。

当前项目状态：
1. 目标池：32 所 211 工科目标校。
2. 官方来源包：32/32 学校都有 plan_source_url，32/32 都有 score_source_url。
3. pre-ML readiness：
   - M1_ready_for_pre_ml_review = 8
   - M2_comparable_ready_with_note = 10
   - M3_fill_gaps_then_review = 3
   - M4_blocked_or_manual_route = 11
4. pre-ML handoff pack：18/32 学校进入 handoff pack，其中 M1=8，M2=10；18/18 都有计划来源和分数来源；14 所 exact_ready。
5. 统一操作板：
   - A1_action_now = 8
   - A2_action_with_note = 13
   - P1_js_endpoint_exposed = 1
   - P1_static_family_ready = 2
   - P2_cached_entry_waiting_headers = 3
   - P3_manual_review = 5
6. 来源精度矩阵：
   - exact_ready = 15
   - mixed_ready = 2
   - fallback_ready = 15
7. pre-ML gate status：
   - G1_ready_for_human_gpt_review_gate = 8
   - G2_ready_with_caution_for_review_gate = 10
   - G3_local_gap_fill_needed = 3
   - G4_blocked_or_manual_route = 11
   - 人工/GPT 复核候选合计 18/32
8. decision register：21 所 pending；其中 18 所可直接复核，3 所需要先人工接受本地补洞候选；当前已完成复核决策 = 0。
9. 当前仍在 ML 前，不能直接开始训练。
10. 现有结构化量级：plan seed 约 538 行，score major seed 约 647 行，score summary seed 约 71 行，primary/canonical snapshot 只有几十行量级；真正同口径、可比较、能直接训练的记录并不多。

当前卡点：
- 本地结构化整理已经到“人工/GPT 复核闸门之前”。
- 真正卡住的是 decision register 尚未做复核决策，以及剩余 11 所 blocked/manual route 可能需要外部网页、接口、登录态、403/header replay 或人工查证。
- 如果现在硬上 ML，样本少、口径混杂、过拟合风险很高。

已有扩池线索：
- 已有一批非 211 扩池候选，基于教育部第二轮“双一流”名单和工科/理工匹配。
- 第一批 10 所种子：南京信息工程大学、西南石油大学、成都理工大学、天津工业大学、湘潭大学、山西大学、宁波大学、南京林业大学、上海科技大学、南方科技大学。
- 这些目前只是 todo/discovery 层，约 277 条 priority candidates，尚未纳入主 pre-ML 口径。

请回答这些问题：
A. 当前项目瓶颈下，是否应该立即扩充主数据池？如果扩，扩到什么边界；如果不扩，应该先做什么？
B. 如果需要扩样本，优先级应该怎么排：学校数、年份数、训练层级、院校专业组粒度、字段厚度？
C. 是否应该现在使用 Deep Research 做调查？如果应该，调查边界是什么；如果不应该，为什么？
D. 请给出 6 条以内的下一步执行顺序。
E. 最后一行请三选一输出：现在先不要扩 / 现在小扩 / 现在大扩并上 Deep Research。
```

## 8. 本地优先级建议

在网页版 GPT-5.5 Pro 给出判断前，本地优先级建议如下：

1. 不启动机器学习。
2. 不把非 211 候选直接并入主池。
3. 先处理 18 所 G1/G2 的人工/GPT 复核。
4. 再处理 3 所 G3 的本地补洞候选是否接受。
5. 将 11 所 G4 单独列为外部调查/人工路线。
6. 若要使用 Deep Research，应只用于 11 所 G4 的官方来源可达性调查，不用于大范围扩池推荐。

## 9. 网页版 GPT-5.5 Pro 附件版结论

网页版 GPT-5.5 Pro 已读取 `outputs/project_bottleneck_summary_pack_2026-05-13.zip` 附件，并按包内 markdown 与 CSV 重新判断。

最终结论：现在先不要扩。

关键判断：

- 不立即扩充主数据池。
- 不把 Deep Research 作为扩池主线。
- 当前阶段是 pre-ML 复核决策阶段，不是扩池阶段，也不是建模阶段。
- 最短路径是先处理 21 所 decision register pending：8 所 D1/G1、10 所 D2/G2、3 所 D3/D4。
- 非 211 扩池只能停留在 todo/discovery 观察池，不进入主 pre-ML 口径，不进入 canonical training layer。
- Deep Research 如启用，只能作为 11 所 G4 的官方来源可达性调查支线。

完整附件版外部判断记录见：`docs/gpt55_web_attachment_bottleneck_decision.md`。

## 10. D1/G1 首轮复核进展

已完成第一批 `D1_ready_now_clean_pending_decision` / `G1_ready_for_human_gpt_review_gate` 的 GPT 复核覆盖表。

结果：

- 8/8 学校建议 `accept_for_review_gate`。
- 8/8 为 `A_clean_gate_accept`。
- 0 所建议 `request_row_fix`。
- 0 所建议 `hold_before_ml`。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d1_g1_gpt_review_decisions.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d1_g1_gpt_review_decisions_merged.csv`
- `reports/engineering_pre_ml_d1_g1_gpt_review_decisions_school_summary.csv`
- `reports/engineering_pre_ml_d1_g1_gpt_review_decisions_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_d1_g1_gpt_review_decisions.py`

## 11. D2/G2 caution 复核进展

已完成第二批 `D2_ready_now_caution_pending_decision` / `G2_ready_with_caution_for_review_gate` 的 GPT 复核覆盖表。

结果：

- 10/10 学校完成 GPT 复核决策。
- 2 所建议 `accept_for_review_gate`，但必须带 caution 标记。
- 5 所建议 `request_row_fix`。
- 3 所建议 `hold_before_ml`。
- ML 入口仍保持关闭。

关键收紧规则：

- 遇到 `yoursite.com` 等占位来源 URL，即使其他字段标为 `exact_ready`，也先判为 `request_row_fix`。
- fallback 依赖较重且叠加缺计划、缺趋势或非 2025 freshness 的学校暂缓进入 canonical/ML 准备。

本轮产物：

- `docs/pre_ml_d2_g2_gpt_review_decisions.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_gpt_review_decisions_merged.csv`
- `reports/engineering_pre_ml_d2_g2_gpt_review_decisions_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_gpt_review_decisions_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_d2_g2_gpt_review_decisions.py`

## 12. D3/D4 本地补洞接受进展

已完成 `D3_gap_fill_acceptance_pending_decision` / `D4_gap_fill_caution_acceptance_pending_decision` 的本地补洞接受覆盖表。

结果：

- 3/3 学校完成 GPT 复核决策。
- 河北工业大学：`accept_gap_fill_then_review`，可作为 G1 候选重刷。
- 太原理工大学：`accept_gap_fill_then_review`，可作为 G1 候选重刷。
- 北京邮电大学：`accept_gap_fill_with_note`，只能作为 G2 caution 候选重刷，保留 missing_plan 与 fallback 隔离备注。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d3_d4_gap_fill_acceptance_decisions.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv`
- `reports/engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_school_summary.csv`
- `reports/engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions.py`

## 13. D3/D4 正式补洞应用层与 post-gap-fill 重刷

已把 D3/D4 接受结果落成独立的正式本地补洞应用层，并在不覆盖原始基线表、不打开 ML 的前提下，重刷 readiness、handoff、workbench 和 gate status 的 post-gap-fill 版本。

结果：

- 3/3 所 D3/D4 学校已进入 `pre_ml_gap_fill_application_layer`。
- 河北工业大学、太原理工大学重刷为 `G1_ready_for_human_gpt_review_gate`。
- 北京邮电大学本科招生网重刷为 `G2_ready_with_caution_for_review_gate`，继续保留 `missing_plan` 和 fallback caution。
- 可进入人工/GPT 复核闸门的学校从 18 所升至 21 所。
- `G3_local_gap_fill_needed` 从 3 所降至 0 所。
- `G4_blocked_or_manual_route` 仍为 11 所。
- ML 入口仍保持关闭；post-gap-fill 表只用于复核材料，不直接进入 canonical/ML。

本轮产物：

- `docs/pre_ml_gap_fill_application_and_refresh.md`
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

## 14. D2/G2 request_row_fix 修复队列

已把 D2/G2 GPT 复核中 5 个 `request_row_fix` 项拆成独立行级修复队列。

结果：

- 5/5 个 `request_row_fix` 已进入 `pre_ml_d2_g2_request_row_fix_queue`。
- 华北电力大学为 `P0_source_identity_fix`，原因是来源 URL 含 `yoursite.com` 占位域名，修复前不得进入 canonical。
- 北京工业大学为 `P1_latest_plan_score_alignment`，优先补齐 2025 计划侧结构化记录并确认分数/位次口径。
- 长安大学、合肥工业大学、南京航空航天大学为 `P1_reference_year_and_field_mapping`，优先复核已有官方结构化源的字段映射、计划数、最低分、最低位次和 reference_year 备注。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d2_g2_request_row_fix_queue.md`
- `scripts/build_engineering_pre_ml_d2_g2_request_row_fix_queue.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv`
- `reports/engineering_pre_ml_d2_g2_request_row_fix_queue_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_request_row_fix_queue_coverage_rollup.csv`

## 15. D2/G2 华北电力大学 source identity fix

已处理 D2/G2 修复队列中的第一项：华北电力大学 `P0_source_identity_fix`。

结果：

- 107 条华北电力行级记录全部含 `http://www.yoursite.com/` 占位 URL。
- 本地缓存页面已确认官方招生计划入口 `https://goto.ncepu.edu.cn/zsjh/index.htm` 明示 `https://goto.ncepu.edu.cn/common/plan_json.json`。
- 本地缓存页面已确认官方往年分数入口 `https://goto.ncepu.edu.cn/wnfs/index.htm` 明示 `https://goto.ncepu.edu.cn/common/aii_json.json` 和 `https://goto.ncepu.edu.cn/common/major_json.json`。
- 华北电力已从 `source_reacquisition_required` 推进到 `source_identity_fix_preview_ready`。
- detail URL 只做候选推断，不直接进入 canonical。
- `trend_missing_or_unverified` 仍未解决。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d2_g2_huabei_source_identity_fix.md`
- `scripts/build_engineering_pre_ml_d2_g2_huabei_source_identity_fix.py`
- `clean_data/engineering_guangxi_seed/huabei_dianli_source_identity_fix_row_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `reports/engineering_pre_ml_d2_g2_huabei_source_identity_fix_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_huabei_source_identity_fix_coverage_rollup.csv`

## 16. D2/G2 北京工业大学 latest plan-score alignment

已处理 D2/G2 修复队列中的第二项：北京工业大学 `P1_latest_plan_score_alignment`。

结果：

- 2025 广西物理类计划侧已本地结构化：16 行，计划数合计 46。
- 2025 广西物理类分数侧已有官方专业分数：17 行，唯一专业键 15 个。
- 计划-分数匹配专业键 10 个；仅计划侧 6 个；仅分数侧 5 个。
- 2025 最低分为 567。
- 2025 最低位次缺失。
- 2024 best comparable rank 仍为 8700。
- 判断：2025 分数可以作为 latest score reference，但不能替代 2024 带位次可比记录。
- 北京工业大学可从 `queued_for_row_fix` 推进到 `latest_plan_score_alignment_preview_ready`，但仍必须保留 `no_2025_rank` caution。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment.md`
- `scripts/build_engineering_pre_ml_d2_g2_beijing_gongye_alignment.py`
- `clean_data/engineering_guangxi_seed/beijing_gongye_latest_plan_score_alignment_row_preview.csv`
- `clean_data/engineering_guangxi_seed/beijing_gongye_latest_plan_score_alignment_preview.csv`
- `reports/engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_coverage_rollup.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`

## 17. D2/G2 长安大学 reference year and field mapping

已处理 D2/G2 修复队列中的第三项：长安大学 `P1_reference_year_and_field_mapping`。

结果：

- 2025 广西物理类本科普通批计划侧已由长安大学官方 API 结构化：37 行，计划数合计 128。
- 2025 计划字段可确认：`plan_count`、`requirement`、`selection_group` 和来源 URL 均可追溯到校方 API。
- 2024 广西物理类本科普通批专业分数侧已由长安大学官方 API 结构化：32 行。
- 2024 校方 API 专业分数最低分 568，最低位次 17775，最高分 602。
- 2025 广西官方投档线存在最新候选：普通组 101/102，最低分 545，最低位次 27533。
- 2025 的 501/502 国家专项和 759 预科类已隔离为 special line，不进入普通组最低分口径。
- 判断：2025 投档线只能作为 local admission-line candidate，需要人工接受或按补充策略接入，不能直接替代校方 API 分数字段。
- 长安大学可从 `queued_for_row_fix` 推进到 `reference_year_field_mapping_preview_ready`，但仍保留 G2 caution 和 reference year 说明。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d2_g2_changan_reference_year_field_mapping.md`
- `scripts/build_engineering_pre_ml_d2_g2_changan_reference_mapping.py`
- `clean_data/engineering_guangxi_seed/changan_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/changan_reference_year_field_mapping_preview.csv`
- `reports/engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_coverage_rollup.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`

## 18. D2/G2 合肥工业大学 reference year and field mapping

已处理 D2/G2 修复队列中的第四项：合肥工业大学 `P1_reference_year_and_field_mapping`。

结果：

- 2025 广西物理类计划侧来自官方直达页；原始提取 51 行，进入 seed 去重后为 42 行。
- 2025 普通批计划侧为 37 行，计划数合计 193。
- 2025 国家专项计划侧为 5 行，计划数合计 17，继续隔离。
- 2025 计划明细缺选科/院校专业组字段，不能直接映射成专业组层 canonical。
- 2024 专业明细分数 seed 去重后为 32 行，其中普通批 30 行、国家专项 2 行。
- 2024 专业明细最低分 572，最高分 619；页面专业明细不含最低位次。
- 当前 16236 位次来自一分一档派生摘要，不是合肥工业大学页面原始字段。
- 2024 直达页概览最低分为 550，与专业明细最低分 572 相差 22 分，需人工判定学校/校区/投档线口径。
- 2025 广西官方投档线存在最新候选：合肥工业大学普通组 101/102，最低分 549，最低位次 25474。
- 合肥工业大学(宣城校区)已作为独立校区候选隔离，不自动并入当前 school_key。
- 合肥工业大学可从 `queued_for_row_fix` 推进到 `reference_year_field_mapping_preview_ready`，但仍保留 G2 caution、rank 派生说明和 campus scope caution。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d2_g2_hefei_reference_year_field_mapping.md`
- `scripts/build_engineering_pre_ml_d2_g2_hefei_reference_mapping.py`
- `clean_data/engineering_guangxi_seed/hefei_gongda_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/hefei_gongda_reference_year_field_mapping_preview.csv`
- `reports/engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_coverage_rollup.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`

## 19. D2/G2 南京航空航天大学 reference year and field mapping

已处理 D2/G2 修复队列中的第五项：南京航空航天大学 `P1_reference_year_and_field_mapping`。

结果：

- 2025 广西物理类普通类计划侧已由官方招生计划 API 结构化：21 行，计划数合计 75。
- 2025 计划侧有学院字段，共覆盖 14 个学院；但选科/院校专业组字段缺失。
- 2025 plan seed 行的 `source_url` 为空，本轮预览使用 registry/API 查询 URL 回填为来源说明，不写入 canonical。
- 2024 专业分数 API 可确认：19 行广西物理类本科普通批专业分数，最低分 618，最高分 632。
- 2024 录取概况 API 可确认：普通类最低分 618、平均分 622、最高分 632，与专业明细最低分一致。
- 2024 API 不含最低位次；当前 3971 来自一分一档派生摘要，不是 API 原始字段。
- 2025 广西官方投档线存在最新候选：普通组 101 最低分 615，最低位次 3507。
- 2025 的 303 组无备注但与 101 分组明显不同，本轮隔离为 `separate_unlabeled_group_candidate`，需人工判定是否接入。
- 2025 的 504 国家专项和 759 预科类已隔离为 special line。
- 南京航空航天大学可从 `queued_for_row_fix` 推进到 `reference_year_field_mapping_preview_ready`，但仍保留 G2 caution、rank 派生说明和 303 组边界 caution。
- D2/G2 request_row_fix 5 项均已有修复预览。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_d2_g2_nanhang_reference_year_field_mapping.md`
- `scripts/build_engineering_pre_ml_d2_g2_nanhang_reference_mapping.py`
- `clean_data/engineering_guangxi_seed/nanhang_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/nanhang_reference_year_field_mapping_preview.csv`
- `reports/engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_coverage_rollup.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`

## 20. G4 官方来源可达性队列

D2/G2 request_row_fix 5 项均已有修复预览后，已按 post-gap-fill gate status 生成 G4 官方来源可达性队列。

结果：

- G4 队列共 11 所学校。
- `P1_static_family_ready`：2 所，大连海事大学、哈尔滨工程大学本科招生。
- `P1_js_endpoint_exposed`：1 所，江南大学。
- `P2_cached_entry_waiting_headers`：3 所，北京科技大学本科招生网、中国矿业大学、中国石油大学北京。
- `P3_manual_review`：5 所，北京化工大学、中国石油大学华东、上海大学、中国地质大学武汉、中国矿业大学北京。
- Deep Research 只可作为官方来源可达性支线工具，不用于扩池、不用于非 211 搜索、不直接生成 ML/canonical 输入。
- ML 入口仍保持关闭。

本轮产物：

- `docs/pre_ml_g4_source_reachability_queue.md`
- `scripts/build_engineering_pre_ml_g4_source_reachability_queue.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_source_reachability_queue_merged.csv`
- `reports/engineering_pre_ml_g4_source_reachability_queue_coverage_rollup.csv`

## 21. G4 P1 官方来源可达性预览

已处理 G4 队列中的 P1 支线：大连海事大学、哈尔滨工程大学本科招生、江南大学。

结果：

- 大连海事大学与哈尔滨工程大学本科招生均为 `static_family_structure_confirmed_but_remote_fetch_blocked`。
- 两校缓存静态页均已确认同家族 `f/ajax_zsjh_param`、`f/ajax_lnfs_param`、`f/ajax_zsjh`、`f/ajax_lnfs` 路线。
- 大连海事大学既有 probe 为 10/10 `403`；哈尔滨工程大学本轮未新联网，registry 记录为同家族接口带 cookie 后仍 403。
- 江南大学为 `js_endpoint_shape_confirmed_but_remote_probe_blocked`，缓存 JS 已确认计划与历史分数 endpoint、字段与参数链路；既有 probe 为 9 个 `483` 与 1 个 TLS EOF。
- 3 所均只保留在 G4 source reachability branch，不进入 canonical/ML。
- Deep Research 仍只可用于官方来源可达性支线，不用于扩池、不用于非 211 搜索。

本轮产物：

- `docs/pre_ml_g4_p1_source_reachability_preview.md`
- `scripts/build_engineering_pre_ml_g4_p1_source_reachability_preview.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p1_source_reachability_preview_merged.csv`
- `reports/engineering_pre_ml_g4_p1_source_reachability_preview_coverage_rollup.csv`

## 22. G4 P2 缓存入口与 header 路线审计

已处理 G4 队列中的 P2 支线：北京科技大学本科招生网、中国矿业大学、中国石油大学北京。

结果：

- P2 审计共 3 所学校，三所均有缓存入口页和已知 ajax endpoint 形状。
- 北京科技大学本科招生网与中国矿业大学可从缓存 HTML 确认 `f/ajax_zsjh_param`、`f/ajax_zsjh`、`f/ajax_lnfs_param`、`f/ajax_lnfs` 等路线，但未进入 static inventory。
- 中国石油大学北京已有 static/ajax inventory，且缓存页中存在专业组相关 `zyz` 路线证据。
- 三所既有 ajax_family probe 均为 10/10 `403`，说明当前不是“缺入口”，而是 header/cookie/浏览器态或服务端拦截问题。
- 本轮未联网、未 replay header/cookie、未打开浏览器态检查。
- 三所均继续保留在 G4 P2 source reachability branch，不进入 canonical/ML。

本轮产物：

- `docs/pre_ml_g4_p2_cached_entry_header_audit.md`
- `scripts/build_engineering_pre_ml_g4_p2_cached_entry_header_audit.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p2_cached_entry_header_audit_preview_merged.csv`
- `reports/engineering_pre_ml_g4_p2_cached_entry_header_audit_coverage_rollup.csv`

## 23. G4 P3 官方来源人工路线预览

已处理 G4 队列中的 P3 支线：北京化工大学、中国石油大学华东、上海大学、中国地质大学武汉、中国矿业大学北京。

结果：

- P3 manual review 共 5 所学校。
- 4 所已有本地缓存页证据，5 所均已有 discovery candidates。
- 北京化工大学与中国石油大学华东均为官方主页/栏目已缓存，但稳定招生计划与历年分数入口仍缺失。
- 上海大学为 FineUI/form replay 阻塞，已记录 `__VIEWSTATE`、入口页和表单路线，但不回放表单。
- 中国地质大学武汉需要区分招生就业页、继续教育录取查询和招生子域，先确认本科普通批官方入口。
- 中国矿业大学北京当前缓存偏研究生/信息公开弱证据，需要确认本科招生计划与历年分数官方入口。
- 5 所下一步均需要人工批准后才能进行 live source 检查、Deep Research、表单/header/cookie replay 或浏览器态验证。
- P3 结果只作为来源路线预览，不进入 canonical/ML。

本轮产物：

- `docs/pre_ml_g4_p3_manual_source_review.md`
- `scripts/build_engineering_pre_ml_g4_p3_manual_source_review.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p3_manual_source_review_preview_merged.csv`
- `reports/engineering_pre_ml_g4_p3_manual_source_review_coverage_rollup.csv`

## 24. G4 来源可达性 closeout 与人工批准队列

已合并 G4 P1/P2/P3 本地预览，生成 11 所 G4 的 closeout 和人工批准队列。

结果：

- G4 closeout 共 11 所学校。
- 11 所均仍需 live source 人工批准后才能继续，不进入 canonical/ML。
- 2 所可仅本地继续做缓存静态解析预览：大连海事大学、哈尔滨工程大学本科招生。
- 5 所需要 header/cookie 或浏览器态批准：大连海事大学、哈尔滨工程大学本科招生、北京科技大学本科招生网、中国矿业大学、中国石油大学北京。
- 1 所需要浏览器/TLS/API probe 批准：江南大学。
- 1 所需要 form/state-token replay 批准：上海大学。
- 4 所只适合在人工批准后做官方来源可达性限定版 Deep Research/人工源确认：北京化工大学、中国石油大学华东、中国地质大学武汉、中国矿业大学北京。
- 批准范围被限定为官方来源可达性验证；禁止扩池、非 211 搜索、直接写 canonical/ML、模型训练或未复核合并。

本轮产物：

- `docs/pre_ml_g4_source_reachability_closeout.md`
- `scripts/build_engineering_pre_ml_g4_source_reachability_closeout.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_source_reachability_closeout_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_human_approval_queue_merged.csv`
- `reports/engineering_pre_ml_g4_source_reachability_closeout_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_human_approval_queue_coverage_rollup.csv`

## 25. 全项目 pre-ML human/GPT action board 与 gate closeout

已将 D1/G1、D2/G2、D3/D4、D2 row fix status preview、G4 source reachability closeout/approval queue 合并成 32 所主池逐校行动板。

结果：

- 主池行动板共 32 所。
- 13 所可进入 human/GPT 复核闸门：10 所 clean bucket，3 所 caution bucket。
- 5 所 D2/G2 row fix preview 已就绪，下一步是人工接受或驳回；接受前不得进入复核闸门。
- 3 所 D2/G2 保持 hold_before_ml。
- 11 所 G4 保持 source reachability branch，全部需要 live source approval 才能继续。
- canonical/ML 入口仍为 0；扩池、非 211 搜索、Deep Research 主线仍关闭。

本轮产物：

- `docs/pre_ml_human_gpt_review_action_board_and_gate_closeout.md`
- `scripts/build_engineering_pre_ml_human_action_board_closeout.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_action_board_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_final_gate_closeout_merged.csv`
- `reports/engineering_pre_ml_human_gpt_review_action_board_coverage_rollup.csv`
- `reports/engineering_pre_ml_final_gate_closeout_coverage_rollup.csv`

## 26. Human/GPT review gate packet 与 D2 row fix acceptance sheet

已从 action board 中抽取 13 所 `ready_for_human_gpt_review_gate = true` 学校，生成复核包和人工决策表；同时准备 5 所 D2 row fix preview 的接受/驳回工作表。

结果：

- review gate packet 共 13 所。
- clean bucket 10 所：8 所 D1/G1 clean accepted，加 2 所 D3 gap-fill clean accepted。
- caution bucket 3 所：2 所 D2/G2 caution accepted，加北京邮电大学 D4 gap-fill caution accepted。
- gate decision sheet 13 行，当前均待人工选择。
- D2 row fix acceptance sheet 5 行，当前均待人工接受/驳回。
- 所有人工列会在脚本重跑时保留，避免 15 分钟自动化覆盖人工改动。
- canonical/ML、扩池、非 211 搜索、Deep Research 主线继续关闭。

本轮产物：

- `docs/pre_ml_human_gpt_review_gate_packet.md`
- `scripts/build_engineering_pre_ml_review_gate_packet.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_gate_packet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_gate_decision_sheet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_row_fix_acceptance_decision_sheet_merged.csv`
- `reports/engineering_pre_ml_human_gpt_review_gate_packet_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_row_fix_acceptance_decision_sheet_coverage_rollup.csv`

## 27. Post-human-decision intake 与是否继续搜集数据

已根据用户指示记录人工决策：13 所 ready gate 全过，5 所 D2 row fix preview 全部接受用于 caution bucket 修复/重评。

结果：

- post-human intake 共 18 行。
- gate decision confirmed 13 行：10 所 clean confirmation，3 所 caution confirmation with note。
- row fix acceptance confirmed 5 行。
- 需要定点修复/重评的行数为 8：3 所 caution gate 和 5 所 D2 row fix。
- 需要广泛继续搜集数据的行数为 0。
- G4 仍有 11 所需要 live source approval，但只属于官方来源可达性支线，不属于扩池或主线搜集。
- canonical/ML、扩池、非 211 搜索、Deep Research 主线继续关闭。

判断：

不建议继续做广泛数据搜集或扩池。当前主线应进入 post-human caution repair/reassessment 和 canonical rebuild assessment；若要继续补数据，只允许针对已知 row fix、caution 或 G4 blocker 做定点补证。

本轮产物：

- `docs/pre_ml_post_human_decision_intake.md`
- `scripts/build_engineering_pre_ml_post_human_decision_intake.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_intake_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_status_preview_merged.csv`
- `reports/engineering_pre_ml_post_human_decision_intake_coverage_rollup.csv`

## 28. 数据厚度审计与补厚优先级队列

已完成 32 所主池的数据 sufficiency audit，按年份覆盖、计划/分数/位次字段、趋势、专业组或选科映射、post-human caution/row-fix 边界生成补厚优先级。

结果：

- audited schools = 32。
- broad data collection needed = 0。
- targeted collection/thickening needed = 16。
- canonical rebuild assessment ready = 10。
- P0 caution repair / G2 reassessment = 8。
- P1 targeted thickening before rebuild = 8。
- P2 canonical rebuild assessment = 2。
- P3 hold or core field gap = 3。
- P4 G4 source reachability only = 11。
- canonical/ML、扩池、非 211 搜索、Deep Research 主线继续关闭。

判断：

数据确实偏少，但缺口集中在主池内部的定点补厚，不是继续广泛搜集学校。下一步应先处理 8 条 P0 caution/row-fix 重评，再处理 8 条 P1 年份/位次/专业组映射补厚；G4 继续等待官方来源可达性批准。

本轮产物：

- `docs/pre_ml_data_sufficiency_audit.md`
- `scripts/build_engineering_pre_ml_data_sufficiency_audit.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_sufficiency_audit_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv`
- `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`
- `reports/engineering_pre_ml_data_thickening_priority_queue_coverage_rollup.csv`

## 29. P0 caution repair / G2 reassessment 预览

已按 data thickening priority queue 处理 P0 caution/row-fix 8 行，生成非基线、非 canonical、非 ML 的复评预览。

结果：

- P0 preview rows = 8。
- row fix accepted for reassessment = 5。
- caution gate confirmed with note = 3。
- targeted repair needed = 8。
- broad data collection needed = 0。
- canonical/ML、扩池、非 211 搜索、Deep Research 主线继续关闭。

分流：

- 3 行需要 rank boundary note：北京工业大学、合肥工业大学、南京航空航天大学招生网。
- 1 行需要 reference_year note：长安大学。
- 1 行需要 source identity fix：华北电力大学。
- 3 行需要 caution note 后继续补厚：北京邮电大学本科招生网、河海大学、西安电子科技大学本科招生网。

判断：

P0 的下一步不是扩池，而是把已接受的 row-fix preview 与 caution note 转成 G2 复评边界。复评只处理年份、位次、趋势、专业组映射和来源身份备注；通过后也只能进入 canonical rebuild assessment，不能直接写 canonical/ML。

本轮产物：

- `docs/pre_ml_p0_caution_repair_reassessment.md`
- `scripts/build_engineering_pre_ml_p0_caution_repair_reassessment.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv`
- `reports/engineering_pre_ml_p0_caution_repair_reassessment_coverage_rollup.csv`

## 30. P1 targeted thickening before rebuild 预览

已按 data thickening priority queue 处理 P1 targeted thickening 8 行，生成非基线、非 canonical、非 ML 的定点补厚预览。

结果：

- P1 preview rows = 8。
- targeted collection/thickening needed = 8。
- broad data collection needed = 0。
- 补厚后可进入 canonical rebuild assessment 的候选 = 8。
- canonical/ML、扩池、非 211 搜索、Deep Research 主线继续关闭。

分流：

- 7 行需要补 2023 年份缺口并补专业组映射：北京交通大学、福州大学、华东理工大学、武汉理工大学、西南交通大学、郑州大学、中国地质大学北京。
- 1 行只需要补专业组映射：南京理工大学。
- 8 行均属于 selection requirement groups present but no admission group code 的口径，需要把选科组/招生专业映射到院校专业组口径。

判断：

P1 的下一步仍不是扩池，而是对 clean 通过学校做本地定点补厚。补齐目标年份、最低位次和专业组映射后，也只能进入 canonical rebuild assessment，不能直接写 canonical/ML。

本轮产物：

- `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`
- `scripts/build_engineering_pre_ml_p1_targeted_thickening_before_rebuild.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv`
- `reports/engineering_pre_ml_p1_targeted_thickening_before_rebuild_coverage_rollup.csv`

## 31. 打包文件清单

本总结包建议随同以下文件一起交接：

- `docs/gpt55_takeover_handoff.md`
- `docs/original_thread_return_handoff.md`
- `docs/non211_authoritative_expansion_notes.md`
- `reports/engineering_pre_ml_gate_status_coverage_rollup.csv`
- `reports/engineering_pre_ml_review_gate_decision_register_coverage_rollup.csv`
- `reports/engineering_pipeline_status.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_gate_status_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_source_resolution_matrix_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_master_operating_board_merged.csv`
- `reports/non211_authoritative_todo.csv`
- `reports/non211_authoritative_discovery_candidates_priority.csv`
- `docs/pre_ml_d1_g1_gpt_review_decisions.md`
- `docs/pre_ml_d2_g2_gpt_review_decisions.md`
- `docs/pre_ml_d3_d4_gap_fill_acceptance_decisions.md`
- `docs/pre_ml_gap_fill_application_and_refresh.md`
- `docs/pre_ml_d2_g2_request_row_fix_queue.md`
- `docs/pre_ml_d2_g2_huabei_source_identity_fix.md`
- `docs/pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment.md`
- `docs/pre_ml_d2_g2_changan_reference_year_field_mapping.md`
- `docs/pre_ml_d2_g2_hefei_reference_year_field_mapping.md`
- `docs/pre_ml_d2_g2_nanhang_reference_year_field_mapping.md`
- `docs/pre_ml_g4_source_reachability_queue.md`
- `docs/pre_ml_g4_p1_source_reachability_preview.md`
- `docs/pre_ml_g4_p2_cached_entry_header_audit.md`
- `docs/pre_ml_g4_p3_manual_source_review.md`
- `docs/pre_ml_g4_source_reachability_closeout.md`
- `docs/pre_ml_human_gpt_review_action_board_and_gate_closeout.md`
- `docs/pre_ml_human_gpt_review_gate_packet.md`
- `docs/pre_ml_post_human_decision_intake.md`
- `docs/pre_ml_data_sufficiency_audit.md`
- `docs/pre_ml_p0_caution_repair_reassessment.md`
- `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d1_g1_gpt_review_decisions_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_gpt_review_decisions_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d3_d4_gap_fill_acceptance_decisions_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_gap_fill_application_layer_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv`
- `clean_data/engineering_guangxi_seed/huabei_dianli_source_identity_fix_row_preview.csv`
- `clean_data/engineering_guangxi_seed/beijing_gongye_latest_plan_score_alignment_row_preview.csv`
- `clean_data/engineering_guangxi_seed/beijing_gongye_latest_plan_score_alignment_preview.csv`
- `clean_data/engineering_guangxi_seed/changan_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/changan_reference_year_field_mapping_preview.csv`
- `clean_data/engineering_guangxi_seed/hefei_gongda_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/hefei_gongda_reference_year_field_mapping_preview.csv`
- `clean_data/engineering_guangxi_seed/nanhang_reference_year_field_mapping_row_preview.csv`
- `clean_data/engineering_guangxi_seed/nanhang_reference_year_field_mapping_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_source_reachability_queue_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p1_source_reachability_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p2_cached_entry_header_audit_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p3_manual_source_review_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_source_reachability_closeout_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_human_approval_queue_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_action_board_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_final_gate_closeout_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_gate_packet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_gate_decision_sheet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_row_fix_acceptance_decision_sheet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_intake_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_status_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_sufficiency_audit_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv`
- `reports/engineering_pre_ml_d1_g1_gpt_review_decisions_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_gpt_review_decisions_coverage_rollup.csv`
- `reports/engineering_pre_ml_d3_d4_gap_fill_acceptance_decisions_coverage_rollup.csv`
- `reports/engineering_pre_ml_gap_fill_application_layer_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_request_row_fix_queue_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_huabei_source_identity_fix_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_beijing_gongye_latest_plan_score_alignment_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_changan_reference_year_field_mapping_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_hefei_reference_year_field_mapping_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_g2_nanhang_reference_year_field_mapping_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_source_reachability_queue_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_p1_source_reachability_preview_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_p2_cached_entry_header_audit_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_p3_manual_source_review_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_source_reachability_closeout_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_human_approval_queue_coverage_rollup.csv`
- `reports/engineering_pre_ml_human_gpt_review_action_board_coverage_rollup.csv`
- `reports/engineering_pre_ml_final_gate_closeout_coverage_rollup.csv`
- `reports/engineering_pre_ml_human_gpt_review_gate_packet_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_row_fix_acceptance_decision_sheet_coverage_rollup.csv`
- `reports/engineering_pre_ml_post_human_decision_intake_coverage_rollup.csv`
- `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`
- `reports/engineering_pre_ml_data_thickening_priority_queue_coverage_rollup.csv`
- `reports/engineering_pre_ml_p0_caution_repair_reassessment_coverage_rollup.csv`
- `reports/engineering_pre_ml_p1_targeted_thickening_before_rebuild_coverage_rollup.csv`
