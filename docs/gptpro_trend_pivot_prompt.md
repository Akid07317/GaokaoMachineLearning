# 给网页版 GPT Pro 的提示词

请阅读我上传的证据包附件，然后帮我判断这个广西高考志愿项目接下来怎么走。

## 背景

这是一个面向广西物理类本科普通批的高考志愿数据项目。此前项目重点是 32 所 211 工科目标校的 pre-ML 复核链路：人工/GPT gate、row fix、G4 source reachability、data sufficiency audit、P0/P1 补厚预览等。

现在我认为项目可能走进了“死磕 32 所学校数据”的死胡同。32 所学校可以做高精度目标校决策，但很难反映整体招生趋势、位次波动、计划数变化和专业组结构变化。

当前新判断是：

- 32 所应保留为 high-confidence decision pool。
- 另开一个隔离的 reference trend pool，用更大样本学习趋势背景。
- reference trend pool 不直接写入 32 所 decision pool，不直接进入 canonical/ML。
- 趋势学习的基本单位应该是“院校专业组-年份”，不是“学校”。

## 附件里最关键的证据

请重点看：

- `docs/trend_reference_pool_pivot.md`
- `docs/project_bottleneck_summary_pack.md`
- `docs/pre_ml_data_sufficiency_audit.md`
- `docs/pre_ml_p0_caution_repair_reassessment.md`
- `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`
- `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`
- `reports/engineering_pre_ml_p0_caution_repair_reassessment_coverage_rollup.csv`
- `reports/engineering_pre_ml_p1_targeted_thickening_before_rebuild_coverage_rollup.csv`
- `reports/non211_authoritative_todo.csv`
- `reports/non211_authoritative_discovery_candidates_priority.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv`

## 当前状态摘要

- 32 所主池已完成 pre-ML 人工决策 intake。
- 13 所进入 human/GPT review gate，其中 10 所 clean，3 所 caution。
- 5 所 D2 row fix acceptance 已确认。
- data sufficiency audit 显示：
  - audited school count = 32
  - broad data collection needed = 0
  - targeted collection/thickening needed = 16
  - canonical rebuild assessment ready = 10
  - P0 caution repair/G2 reassessment = 8
  - P1 targeted thickening before rebuild = 8
  - P3 hold/core gap = 3
  - P4 G4 source reachability only = 11
- P0 preview 已完成：8 行，其中 5 行 row fix accepted，3 行 caution gate confirmed with note。
- P1 preview 已完成：8 行，其中 7 行缺 2023 年份 + 专业组映射，1 行只缺专业组映射。
- canonical/ML 入口目前关闭。

## 我想请你判断的问题

1. 只用 32 所学校继续推进，是否足以支撑“招生趋势判断”？如果不够，应如何定位这 32 所？
2. 是否应该建立一个隔离的 reference trend pool？如果应该，它和 32 所 decision pool 的边界应该怎么设计？
3. “一条线程搜集资料，一条线程整理数据”是否可行？如果可行，请给出两个线程的明确分工、输入、输出、交接格式和禁止事项。
4. 搜集资料线程应该优先搜什么？
   - 广西考试院投档线？
   - 院校专业组最低分/最低位次？
   - 计划数？
   - 2023-2025 同口径数据？
   - 非 211 作为趋势样本？
5. 整理数据线程应该先建什么 schema？
   - 必填字段有哪些？
   - confidence tier 怎么分？
   - 什么记录可以进入 trend calibration？
   - 什么记录只能做背景，不可进趋势池？
6. Deep Research 是否应该使用？如果用，只能用于哪一类任务？
7. 第一阶段 reference trend pool 应该做到多大？
   - 150 个 group-year 是否够？
   - 是否应该 300-600 个 group-year？
   - 如何按分数/位次带抽样？
8. 接下来 48 小时的执行顺序应该是什么？

## 请用这个格式回答

请不要只说“继续扩数据”。请给我一个可执行判断。

输出格式：

1. 结论：项目是否确实走进了 32 所死磕误区。
2. 推荐路线：继续死磕 32 所、扩主池、还是建立隔离 reference trend pool。
3. 两线程方案：资料搜集线程 / 数据整理线程是否可并行，怎么并行。
4. 数据准入规则：哪些数据能进 trend pool，哪些不能进。
5. 最小 schema：字段清单和 confidence tier。
6. 第一阶段样本目标：学校数、group-year 数、年份范围、位次带。
7. 风险：这种转向最大的污染风险和工程风险是什么。
8. 48 小时行动清单。

请基于附件证据回答，不要假设我已经有完整趋势池。
