# GPT-5.5 接手文档

## 1. 这份文档的用途

这份文档是给后续接力的 `GPT-5.5` 用的。当前项目已经从“网页搜集阶段”推进到了“pre-ML 数据整理阶段”。  
**当前接手重点不是继续找网页，而是基于本地已有成果继续整理、复核、压缩成更适合人工预审和建模前审查的结构化层。**

## 2. 硬约束

### 2.1 不要做网络搜集

**默认不需要网络搜集信息。**

这包括但不限于：
- 不要重新搜索学校官网
- 不要重新跑发现式爬取
- 不要重新尝试外网接口探测
- 不要做新的反爬/403 解锁实验
- 不要做长时间挂起的在线检查

### 2.2 如果确实需要新增网页/外网信息

如果后续工作**确实必须**依赖新的网页信息、外网接口或新的官方页面，请：

1. **停止在 5.5 这里继续推进**
2. **切回当前这条对话线程**
3. 在这条线程里继续做网络搜集、抓取或解锁工作

一句话原则：

> **5.5 负责吃本地成果，不负责继续上网找新东西。**

### 2.3 不要开始机器学习

当前仍处于 **pre-ML** 阶段。  
不要开始：
- 模型训练
- 回归/分类实验
- 自动特征选择
- 概率校准
- 正式回测训练流程

如果工作推进到“下一步真的就是机器学习”时：

1. 先停止
2. 按主线程约定走人工/GPT 复核闸门
3. 不要直接进入 ML

## 3. 当前项目状态

### 3.1 目标池

- 当前目标池：**32 所 211 工科目标校**

### 3.2 官方来源包

官方来源包已经全覆盖：

- `32 / 32` 学校进入来源包
- `32 / 32` 有 `plan_source_url`
- `32 / 32` 有 `score_source_url`

文件：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_official_source_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_official_source_pack_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_official_source_pack_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_official_source_pack_coverage_rollup.csv:1)

### 3.3 pre-ML readiness

当前 readiness 分层：

- `M1_ready_for_pre_ml_review`: **8**
- `M2_comparable_ready_with_note`: **10**
- `M3_fill_gaps_then_review`: **3**
- `M4_blocked_or_manual_route`: **11**

文件：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_model_readiness_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_model_readiness_coverage_rollup.csv:1)

### 3.4 pre-ML handoff pack

已经有一张可直接交接的 handoff 包：

- `18 / 32` 学校进入 handoff pack
- 其中 `M1 = 8`
- 其中 `M2 = 10`
- `18 / 18` 都有计划来源和分数来源
- `14` 所达到 `exact_ready`

文件：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_handoff_pack_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_handoff_pack_coverage_rollup.csv:1)

### 3.5 统一操作板

当前统一操作板：

- `A1_action_now`: **8**
- `A2_action_with_note`: **13**
- `P1_js_endpoint_exposed`: **1**
- `P1_static_family_ready`: **2**
- `P2_cached_entry_waiting_headers`: **3**
- `P3_manual_review`: **5**

文件：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_master_operating_board_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_master_operating_board_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_master_operating_board_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_master_operating_board_coverage_rollup.csv:1)

### 3.6 来源精度矩阵

来源精度层已经区分出：

- `exact_ready`: **15**
- `mixed_ready`: **2**
- `fallback_ready`: **15**

文件：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_source_resolution_matrix_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_source_resolution_matrix_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_source_resolution_matrix_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_source_resolution_matrix_coverage_rollup.csv:1)

## 4. 5.5 接手时应优先使用的表

### 第一优先：直接交接层

1. pre-ML handoff pack  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_handoff_pack_merged.csv:1)

2. pre-ML readiness  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_model_readiness_merged.csv:1)

3. 官方来源包  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_official_source_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_official_source_pack_merged.csv:1)

### 第二优先：可比主链

4. 最佳可比画像  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_primary_best_comparable_profile_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_primary_best_comparable_profile_merged.csv:1)

5. 最佳可比信号表  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_primary_best_comparable_signal_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_primary_best_comparable_signal_merged.csv:1)

6. 最佳可比预审队列  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_best_comparable_review_queue_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_best_comparable_review_queue_merged.csv:1)

### 第三优先：阻塞与补洞

7. 字段缺口矩阵  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_primary_field_gap_matrix_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_primary_field_gap_matrix_merged.csv:1)

8. 冷队列入口证据  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_cold_queue_entry_registry_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_cold_queue_entry_registry_merged.csv:1)

9. 冷队列解锁工单  
   [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_cold_queue_unlock_queue_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_cold_queue_unlock_queue_merged.csv:1)

## 5. 5.5 的推荐工作顺序

### 路线 A：继续做本地整理（推荐）

优先做这些事：

1. 基于 handoff pack，继续压缩出更适合人工复核的表
2. 基于 best comparable 链，做口径一致性检查
3. 基于 readiness / field gap，继续补本地能补的缺字段
4. 对 `M1/M2` 学校做更好的交接材料，而不是继续找网页

### 路线 B：继续补本地可救的缺口

只允许做：

1. 读取本地已有 CSV / PDF / HTML 提取结果
2. 从本地已有 structured rows 推导更高层 summary
3. 做保守位次补推
4. 做来源回链、来源精度、可比标签整理

### 路线 C：不要做

不要做这些：

1. 新开大范围网页发现
2. 新跑外网接口长探测
3. 重新尝试 `403` 解锁
4. 重新做学校官网搜索
5. 开始机器学习

## 6. 什么时候必须切回当前对话

出现下面任一情况，就不要在 5.5 那边继续顶：

1. 需要新的官方网页内容
2. 需要重新探测接口
3. 需要登录态或浏览器态
4. 需要处理 `403 / anti-bot / header replay`
5. 需要开始机器学习前的最终闸门动作

这时应直接：

> **切回当前这条对话线程继续处理。**

## 7. 对 5.5 的一句话交接

> 你现在接手的是一个已经完成大量本地结构化整理的 Guangxi gaokao 项目。你的主要工作不是再找网页，而是吃掉本地成果、补齐本地可救缺口、整理 pre-ML 交接材料。除非明确要求，否则不要做网络搜集；如果确实需要新增网页信息，请停止并切回原对话线程处理。

## 8. 本轮继续进展

已基于本地 handoff pack、字段缺口矩阵和来源精度信息，新增一张 **pre-ML 人工预审工作台**，继续遵守“不上网、不进 ML”的接手边界。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_review_workbench.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_review_workbench.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_review_workbench_rows` 字段，刷新总状态表时可识别这张工作台。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_workbench_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_workbench_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_workbench_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_workbench_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_workbench_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_workbench_coverage_rollup.csv:1)

当前工作台覆盖：
- `18 / 32` 所目标校
- `M1_ready_for_pre_ml_review`: **8**
- `M2_comparable_ready_with_note`: **10**
- `R1_clean_ready`: **8**
- `R3_caution_review`: **3**
- `R4_high_caution_review`: **7**

工作台用途：
- 把 M1/M2 学校压成逐校人工/GPT 复核清单
- 显式列出 `review_focus_flags`，包括可比年份备注、缺字段、趋势缺口、来源精度风险
- 保留计划/分数官方来源回链，方便复核人快速打开证据
- 只作为进入机器学习前的人工复核准备层，**不是 ML 输入表**

## 9. ML 前闸门状态表

已基于本地 readiness、pre-ML review workbench、字段缺口矩阵、来源精度矩阵，新增一张 **32 校全量 ML 前闸门状态表**。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_gate_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_gate_status.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_gate_status_rows` 字段，刷新总状态表时可识别这张闸门状态表。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gate_status_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gate_status_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_gate_status_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_gate_status_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_gate_status_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_gate_status_coverage_rollup.csv:1)

当前闸门状态：
- `32 / 32` 所目标校已进入闸门状态表
- `G1_ready_for_human_gpt_review_gate`: **8**
- `G2_ready_with_caution_for_review_gate`: **10**
- `G3_local_gap_fill_needed`: **3**
- `G4_blocked_or_manual_route`: **11**
- 人工/GPT 复核候选合计：**18 / 32**

使用纪律：
- `G1/G2` 只能进入人工/GPT 复核闸门，不能直接启动机器学习
- `G3` 继续做本地可补字段
- `G4` 保持冷队列或人工路线；若需要新增网页、接口、登录态或 403 解锁，应切回原主线程处理

## 10. 剩余动作 backlog

已基于 ML 前闸门状态表，新增一张 **pre-ML 剩余动作 backlog**，专门排除 `G1_clean_ready`，只保留仍需动作的学校。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_remaining_action_backlog.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_remaining_action_backlog.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_remaining_action_backlog_rows` 字段，刷新总状态表时可识别这张 backlog。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_remaining_action_backlog_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_remaining_action_backlog_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_remaining_action_backlog_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_remaining_action_backlog_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_remaining_action_backlog_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_remaining_action_backlog_coverage_rollup.csv:1)

当前 backlog：
- 剩余动作学校：**24 / 32**
- `B1_review_with_caution`: **10**
- `B2_local_gap_fill`: **3**
- `B3_blocked_or_manual_boundary`: **11**
- `local_only_feasible`: **13**
- `maybe_local_if_cached_page_available`: **3**
- `not_local_without_original_thread_or_network`: **8**

使用纪律：
- `B1` 只做带备注复核材料，不直入机器学习
- `B2` 优先做本地字段补洞
- `B3` 只记录边界；涉及新增网页、接口、登录态、403 解锁时停止

## 11. B2 本地补洞候选

已基于本地官方广西投档线种子 `admission_line_table_seed.csv`，为 `B2_local_gap_fill` 学校生成 **本地补洞候选表**。这一步只生成候选证据，不自动改写主链。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_local_gap_fill_candidates.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_local_gap_fill_candidates.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_local_gap_fill_candidate_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_local_gap_fill_candidates_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_local_gap_fill_candidates_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_local_gap_fill_candidates_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_local_gap_fill_candidates_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_local_gap_fill_candidates_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_local_gap_fill_candidates_coverage_rollup.csv:1)

当前候选：
- 北京邮电大学：2025 普通批主校候选最低分 `572`，保守位次 `15122`
- 河北工业大学：2025 普通批候选最低分 `546`，保守位次 `27014`
- 太原理工大学：2025 普通批候选最低分 `522`，保守位次 `41040`

使用纪律：
- 候选值来自本地官方投档线种子，按普通批、物理类、第一次正式投档、排除特殊备注后汇总
- 只用于补洞审计或人工复核，不自动进入机器学习
- 北京邮电大学已采用规范化精确校名匹配，避免误纳“北京邮电大学世纪学院”等同名前缀学校

## 12. B2 补洞影响预览

已基于 B2 本地补洞候选，新增一张 **补洞影响预览表**。这张表只预览“如果人工接受候选值，会把学校推到哪个闸门状态”，不改写 readiness、handoff、workbench 或 ML 输入。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_gap_fill_impact_preview.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_gap_fill_impact_preview.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_gap_fill_impact_preview_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gap_fill_impact_preview_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_gap_fill_impact_preview_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_gap_fill_impact_preview_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_gap_fill_impact_preview_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_gap_fill_impact_preview_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_gap_fill_impact_preview_coverage_rollup.csv:1)

当前预览：
- 河北工业大学：可预览为 `G1_ready_for_human_gpt_review_gate_candidate`
- 太原理工大学：可预览为 `G1_ready_for_human_gpt_review_gate_candidate`
- 北京邮电大学：仍缺计划侧，只能预览为 `G2_ready_with_caution_for_review_gate_candidate`

使用纪律：
- 所有预览都需要人工接受候选口径
- 人工确认前不得生成正式 ML 输入
- 若接受候选，下一步应生成正式“补洞应用层”，再重刷 readiness / handoff / workbench / gate status

## 13. 人工/GPT 复核候选包

已把当前 `G1/G2` 闸门候选与 B2 补洞影响预览合并，新增一张 **人工/GPT 复核候选包**。这张表用于复核闸门排程，不进入机器学习。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_review_gate_candidate_pack.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_review_gate_candidate_pack.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_review_gate_candidate_pack_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_candidate_pack_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_candidate_pack_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_candidate_pack_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_candidate_pack_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_candidate_pack_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_candidate_pack_coverage_rollup.csv:1)

当前候选包：
- 合计候选：**21 / 32**
- `C1_current_clean_review_gate`: **8**
- `C2_current_caution_review_gate`: **10**
- `C3_candidate_clean_after_gap_fill_acceptance`: **2**
- `C4_candidate_caution_after_gap_fill_acceptance`: **1**
- 需先人工接受补洞候选：**3**

使用纪律：
- `C1/C2` 可直接进入人工/GPT 复核闸门
- `C3/C4` 必须先接受本地补洞候选口径，再进入复核闸门
- 复核通过前仍不得启动机器学习

## 14. 人工/GPT 复核 checklist

已基于人工/GPT 复核候选包，新增一张 **逐校复核 checklist**。这张表把每所候选校需要核对的问题、可选决策、通过/失败后的路线和 ML 边界写成结构化字段，方便后续人工或 GPT 做闸门复核。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_review_gate_checklist.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_review_gate_checklist.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_review_gate_checklist_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_checklist_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_checklist_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_checklist_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_checklist_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_checklist_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_checklist_coverage_rollup.csv:1)

当前 checklist：
- 合计候选：**21 / 32**
- 可直接进入人工/GPT 复核闸门：**18**
- 需先人工接受本地补洞候选：**3**
- `L1_current_clean_review_checklist`: **8**
- `L2_current_caution_review_checklist`: **10**
- `L3_gap_fill_acceptance_then_clean_checklist`: **2**
- `L4_gap_fill_acceptance_then_caution_checklist`: **1**

使用纪律：
- checklist 的 `checklist_status` 默认是 `pending_human_gpt_review`
- `L1/L2` 是当前可排程复核对象
- `L3/L4` 必须先接受本地补洞候选，不能自动写入主链或 ML
- 本表只服务人工/GPT 复核闸门；复核与人工确认前不得训练、特征选择、校准或回测

## 15. 闸门一致性审计

已基于 readiness、handoff pack、review workbench、gate status、review gate candidate pack、review gate checklist 和 pipeline status，新增一张 **pre-ML 闸门一致性审计表**。这张表逐校检查各层是否有行、pipeline 是否同步标记、候选包与 checklist 是否一致，以及当前是否已经到人工/GPT 复核闸门。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_review_gate_consistency_audit.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_review_gate_consistency_audit.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_review_gate_consistency_audit_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_consistency_audit_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_consistency_audit_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_consistency_audit_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_consistency_audit_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_consistency_audit_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_consistency_audit_coverage_rollup.csv:1)

当前审计结果：
- 审计覆盖：**32 / 32**
- `consistency_ok`: **32**
- `consistency_needs_attention`: **0**
- `ready_for_human_gpt_review_gate`: **18**
- `needs_manual_gap_fill_acceptance_before_review_gate`: **3**
- `blocked_or_manual_route_before_review_gate`: **11**

使用纪律：
- 审计表只证明本地 pre-ML 结构层彼此一致，不代表已经可以启动机器学习
- `ready_for_human_gpt_review_gate` 只能进入人工/GPT 复核闸门
- `needs_manual_gap_fill_acceptance_before_review_gate` 必须先人工接受本地补洞候选，再重刷正式层
- `blocked_or_manual_route_before_review_gate` 涉及新增网页、接口、登录态或 403 解锁时应停止并切回原主线程

## 16. 人工/GPT 复核决策登记表

已基于 review gate checklist，新增一张 **人工/GPT 复核决策登记表**。这张表不替人工/GPT 做结论，只为 21 所候选校预留 `review_decision`、`reviewer`、`decision_time`、`decision_notes` 等待填写字段，并继承每校的可选决策与 ML 边界。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_pre_ml_review_gate_decision_register.py](/Users/don/Documents/New%20project/scripts/build_engineering_pre_ml_review_gate_decision_register.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `pre_ml_review_gate_decision_register_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_pre_ml_review_gate_decision_register_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_decision_register_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_decision_register_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_pre_ml_review_gate_decision_register_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_pre_ml_review_gate_decision_register_coverage_rollup.csv:1)

当前登记表：
- 合计待决：**21 / 32**
- `pending_review_decisions`: **21**
- `completed_review_decisions`: **0**
- 可直接人工/GPT 复核决策：**18**
- 需先人工接受本地补洞候选：**3**
- `D1_ready_now_clean_pending_decision`: **8**
- `D2_ready_now_caution_pending_decision`: **10**
- `D3_gap_fill_acceptance_pending_decision`: **2**
- `D4_gap_fill_caution_acceptance_pending_decision`: **1**

使用纪律：
- 登记表默认 `decision_status = pending_human_gpt_review_decision`
- `review_decision` 等字段留空，等待人工/GPT 复核后再填写
- 决策完成且人工确认前不得启动机器学习

## 17. GPT-5.5 接手启动台

已基于 review gate decision register、candidate pack、checklist、review workbench 和 handoff pack，新增一张 **GPT-5.5 接手启动台**。这张表专门服务于 5.5 接力：每校一行，同时带上接手优先级、是否需要人工接受本地补洞、主文档路径、项目文档路径、本地数据根路径，以及“不要做网络搜集”的硬边界。

新增脚本：
- [/Users/don/Documents/New project/scripts/build_engineering_gpt55_takeover_launchpad.py](/Users/don/Documents/New%20project/scripts/build_engineering_gpt55_takeover_launchpad.py:1)

同步更新：
- [/Users/don/Documents/New project/scripts/build_engineering_pipeline_status.py](/Users/don/Documents/New%20project/scripts/build_engineering_pipeline_status.py:1) 已新增 `gpt55_takeover_launchpad_rows` 字段。

新增产物：
- [/Users/don/Documents/New project/clean_data/engineering_guangxi_seed/guangxi_gpt55_takeover_launchpad_merged.csv](/Users/don/Documents/New%20project/clean_data/engineering_guangxi_seed/guangxi_gpt55_takeover_launchpad_merged.csv:1)
- [/Users/don/Documents/New project/reports/engineering_gpt55_takeover_launchpad_school_summary.csv](/Users/don/Documents/New%20project/reports/engineering_gpt55_takeover_launchpad_school_summary.csv:1)
- [/Users/don/Documents/New project/reports/engineering_gpt55_takeover_launchpad_coverage_rollup.csv](/Users/don/Documents/New%20project/reports/engineering_gpt55_takeover_launchpad_coverage_rollup.csv:1)

当前启动台目标：
- 覆盖所有已进入人工/GPT 复核闸门或补洞接受闸门的学校
- 一校一行给出接手优先级、复核路线、最关键字段和来源回链
- 默认规则：`NO_NETWORK_COLLECTION_USE_LOCAL_ARTIFACTS_ONLY`
- 如需新增网页、403 解锁、登录态或真正进入机器学习，必须切回当前主线程
