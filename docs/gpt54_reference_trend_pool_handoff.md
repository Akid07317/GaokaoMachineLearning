# GPT-5.4 接力文档：广西志愿项目趋势参考池转向

日期：2026-05-15  
工作目录：`/Users/don/Documents/New project`

## 1. 接力目标

本项目已经不应继续只围绕 32 所学校死磕逐行完美化。GPT Pro 回访后的新共识是：

- 32 所 211 工科目标校保留为高精度 `decision_pool`。
- 新建隔离的 `reference_trend_pool`，用于学习广西物理类本科普通批招生趋势。
- 两条线程可以并行：一条搜集资料，一条整理数据。
- 两条线程之间必须通过 `source_packet -> intake_preview -> QA_report -> eligible_flag` 交接。
- 不打开 canonical/ML，不把趋势池数据直接混入 32 所主决策池。

5.4 接手后，第一优先级不是继续修 32 所，而是把 `reference_trend_pool` 的 schema、source packet 模板、seed queue 和 QA 机制搭起来。

## 1.1 联网权限

用户已明确：**5.4 允许联网**。

联网允许范围：

- 搜集广西考试院 2024/2025 本科普通批物理类院校专业组投档线。
- 搜集 2024/2025 广西一分一档表。
- 搜集高校官方招生网的广西物理类本科普通批招生计划、录取分数、专业组信息。
- 搜集非 211 / 强双非 / 区内高校 / 行业特色高校的官方趋势样本来源。
- 验证 source packet 中的 `source_url`、官方性、发布时间、批次/科类/特殊类型隔离状态。
- 对 G4 blocked 学校做官方来源可达性检查。

联网禁止范围：

- 不允许联网结果直接写入 canonical。
- 不允许联网结果直接进入 ML。
- 不允许把联网找到的学校直接并入 32 所 `decision_pool`。
- 不允许把网页搜索结果跳过 `source_packet -> intake_preview -> QA_report -> eligible_flag` 闸门。
- 不允许用第三方页面直接覆盖官方来源。

一句话：**5.4 可以联网找资料，但只能先产出 source packet 和 preview 层；不能直接产出最终训练层或决策层。**

## 2. 当前状态

### 2.1 32 所 decision pool

32 所主池已经完成 pre-ML 人工决策 intake：

- gate decision confirmed rows: 13
- clean confirmed rows: 10
- caution confirmed rows: 3
- row fix acceptance confirmed rows: 5
- requires targeted repair / reassessment rows: 8
- remaining G4 live source approval rows: 11
- canonical/ML entry: closed

相关文件：

- `docs/project_bottleneck_summary_pack.md`
- `docs/pre_ml_post_human_decision_intake.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_post_human_decision_intake_preview_merged.csv`
- `reports/engineering_pre_ml_post_human_decision_intake_coverage_rollup.csv`

### 2.2 数据厚度审计

`data_sufficiency_audit` 的关键结果：

- audited school count: 32
- broad data collection needed for decision pool: 0
- targeted collection / thickening needed: 16
- canonical rebuild assessment ready: 10
- P0 caution repair / G2 reassessment: 8
- P1 targeted thickening before rebuild: 8
- P3 hold/core gap: 3
- P4 G4 source reachability only: 11

这说明：32 所主池内部确实还有补厚工作，但这不是趋势样本不足的根因。趋势问题需要另建更大的参考池。

相关文件：

- `docs/pre_ml_data_sufficiency_audit.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_sufficiency_audit_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv`
- `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`

### 2.3 P0/P1 已生成预览

P0 已完成复评预览：

- preview rows: 8
- row fix accepted for reassessment: 5
- caution gate confirmed with note: 3
- broad data collection needed: 0

P1 已完成定点补厚预览：

- preview rows: 8
- targeted collection/thickening needed: 8
- broad data collection needed: 0
- canonical rebuild assessment after thickening: 8
- 7 行缺 2023 年份 + 专业组映射
- 1 行只缺专业组映射

相关文件：

- `docs/pre_ml_p0_caution_repair_reassessment.md`
- `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p0_caution_repair_reassessment_preview_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_p1_targeted_thickening_before_rebuild_preview_merged.csv`

## 3. GPT Pro 回访结论

已把证据包发给网页版 ChatGPT Pro，提问会话：

- `https://chatgpt.com/c/6a059ea4-f0f0-8398-998a-9e01e34d982e`

GPT Pro 的核心判断：

1. 32 所不足以支撑“招生趋势判断”。
2. 32 所应定位为高精度 `decision_pool`，不应扩成大而杂的主池。
3. 应建立隔离的 `reference_trend_pool`。
4. 趋势学习基本单位是 `院校专业组-year`，不是学校。
5. 两线程并行可行：
   - 资料搜集线程可以联网找官方来源并产出 `source_packet`。
   - 数据整理线程只读 `source_packet`，做 schema、QA、准入和排除。
6. 2024/2025 是严格新高考专业组口径主样本；2023 应放入 `bridge_2023_old_science_background`，不能硬拼成同口径趋势。
7. 48 小时内目标是 150-220 个 strict group-year seed；正式第一阶段目标是 300-600 个 group-year。

证据包：

- `outputs/gptpro_trend_pivot_evidence_pack_2026-05-14.zip`
- `docs/gptpro_trend_pivot_prompt.md`
- `docs/gptpro_trend_pivot_evidence_manifest.md`
- `docs/trend_reference_pool_pivot.md`

## 4. 新架构边界

| Layer | 是否可扩 | 用途 | 禁止事项 |
|---|---:|---|---|
| `decision_pool` | 暂不扩 | 32 所目标校高精度志愿决策 | 不混入趋势池低置信记录 |
| `reference_trend_pool` | 可扩 | 趋势、位次波动、计划变化、组结构背景 | 不直接写 canonical/ML，不直接输出个体志愿结论 |
| `non211_discovery_pool` | 可隔离扩 | 趋势候选来源、强双非/省属参照 | 不直接并入 32 所主池 |
| `G4_source_branch` | 需人工批准 | 官方来源可达性 | 不直接生成 ML 输入 |
| `bridge_2023_old_science_background` | 可建 | 改革前旧理科背景 | 不与 2024/2025 专业组口径硬拼趋势 |

## 5. 两线程并行方案

### 5.1 资料搜集线程

任务：联网找来源，不判断趋势，不清洗成最终表。

优先来源：

1. 广西考试院 2024/2025 本科普通批首选物理院校专业组投档线。
2. 2024/2025 广西一分一档表，用于最低分到位次区间转换。
3. 院校官方招生网的广西物理类本科普通批专业组/计划/录取分数。
4. 非 211 观察池中可作为同位次段趋势样本的官方来源。
5. G4 blocked 学校只做官方来源可达性，不直接入趋势池。

输出：只产出 `reference_trend_source_packet_*.csv`、下载/缓存的原始文件路径、来源可达性报告或同结构 preview，不写最终池。

禁止：

- 禁止写 canonical。
- 禁止把非 211 候选并入 32 所 decision pool。
- 禁止把学校最低分当专业组最低分。
- 禁止混入征集、预科、民族班、专项、中外合作、提前批、艺术体育等特殊类型。
- 禁止把 2023 理科旧口径当作 2024/2025 同口径专业组趋势。
- 禁止只给搜索结果摘要而不保存 source packet。
- 禁止绕过官方来源，用第三方汇总页直接作为 T1/T2。

### 5.2 数据整理线程

任务：优先只读 source packet，做 schema、QA、分层和准入。若 5.4 需要联网，只能用于核验 source packet 的官方性、字段含义和特殊类型边界，不应重新做无边界网页发现。

输出：

- `clean_data/engineering_guangxi_seed/reference_trend_source_packet_template.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_intake_preview.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_seed_queue.csv`
- `reports/reference_trend_pool_schema_coverage_rollup.csv`
- `reports/reference_trend_pool_qa_report.csv`
- `reports/reference_trend_exclusion_log.csv`
- `docs/reference_trend_pool_schema.md`
- `docs/reference_trend_pool_48h_execution_plan.md`

禁止：

- 不做无边界联网抓取。
- 不自动信任 source packet。
- 不打开 canonical/ML。
- 不把 `background_only` 数据改成 `calibration_eligible`，除非字段补齐并通过 QA。

## 6. Source packet 最小字段

资料搜集线程交给整理线程的 source packet 至少包含：

```text
source_id
source_url
source_owner
source_title
published_date
year
province
batch
subject_category
round_type
university_name
university_code
source_contains_group_code
source_contains_min_score
source_contains_min_rank
source_contains_plan_count
special_type_detected
raw_file_path
collector_note
collector_confidence
```

建议额外字段：

```text
page_or_file_type
source_officiality
source_reachability_status
possible_group_code_examples
possible_major_scope_text
requires_rank_conversion
requires_special_type_review
duplicate_source_hint
```

## 7. Reference trend intake 最小 schema

身份字段：

```text
record_id
pool_layer
source_packet_id
year
province
batch
round_type
subject_category
admission_category
```

院校专业组字段：

```text
university_code
university_name
group_code
group_name_or_note
group_subject_requirement
major_scope_text
is_group_code_official
group_mapping_status
cross_year_group_key
cross_year_mapping_confidence
```

结果字段：

```text
min_score
min_rank
rank_interval_low
rank_interval_high
rank_source
plan_count
plan_source_status
score_rank_source_status
```

口径隔离字段：

```text
special_type_flag
special_type_detail
is_first_regular投档
is征集
is中外合作
is民族班
is预科
is专项
is提前批
ordinary_batch_clean_flag
```

来源字段：

```text
source_owner
source_url
source_title
source_publish_date
source_type
source_file_path
extraction_method
source_reachability_status
collector_note
```

准入字段：

```text
confidence_tier
calibration_eligible
background_only
exclude_flag
exclude_reason
qa_flags
created_at
updated_at
```

## 8. Confidence tier

`T1`: 广西考试院或官方投档表，明确到院校专业组-year，批次/科类/轮次清楚，最低分和位次或可验证位次区间齐全。可进 trend calibration。

`T2`: 高校官方招生网数据，广西、物理类、本科普通批、院校专业组或专业组映射清楚，最低分/最低位次/计划数较完整，并能与省级投档口径对齐。可进 trend calibration，但标注 school-official。

`T3`: 官方来源但缺一项关键字段，例如只有最低分无精确位次、计划数缺失、专业组映射需人工解释。可做 background；若能通过官方一分一档表转位次区间，可降权进入 calibration。

`T4`: 第三方转载、学校最低分、专业组不清、计划数或位次不明。只能 background/source discovery。

`T5`: 特殊类型混杂、批次不明、科类不明、年份不明、非广西、非本科普通批、无法区分普通组。直接 exclude。

## 9. Trend pool 准入规则

### 9.1 可进入 calibration

必须同时满足：

- 广西
- 本科普通批
- 普通类
- 首选物理或物理类
- 2024/2025 新高考专业组口径优先
- 第一次正式投档或可明确等价的普通批投档
- 有年份
- 有院校代码或院校名
- 有院校专业组代码，或官方可解释的专业组映射
- 有最低分
- 有最低位次，或可由当年官方一分一档表转换成位次区间
- 能排除特殊类型混杂

### 9.2 只能 background

- 有官方最低分但无位次。
- 有学校官方录取数据但专业组代码不完整。
- 有计划数但无投档位次。
- 2023 年旧理科口径。
- 非 211 官方来源只确认了计划入口或招生章程。
- 第三方转载但能回指官方原表。

### 9.3 必须 exclude 或隔离

- 征集志愿
- 预科
- 民族班
- 专项计划
- 中外合作
- 综合评价
- 提前批
- 艺术体育
- 地方专项/高校专项
- 招生章程而非投档/录取数据
- 研究生、成人、自考、专升本页面
- 学校最低分但学校有多个普通组且无法映射到具体组
- 年份/省份/批次/科类不明

## 10. 48 小时执行顺序

### 第 0 步：冻结边界

立即确认：

- `decision_pool` 仍是 32 所，不扩。
- `reference_trend_pool` 是新隔离层。
- `canonical/ML` 关闭。
- `non211_discovery_pool` 只作趋势候选来源，不直接进入 decision pool。

### 第 1 步：建 schema 与模板

先产出：

- `docs/reference_trend_pool_schema.md`
- `clean_data/engineering_guangxi_seed/reference_trend_source_packet_template.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_intake_preview.csv`
- `reports/reference_trend_pool_schema_coverage_rollup.csv`

没有 schema 前不要大规模搜集。若必须先联网探路，只能记录为 `source_discovery_note`，不要生成正式 trend intake。

### 第 2 步：做 20-30 条 pilot

用本地已有 discovery/source list、广西考试院公开表和少量高校官方来源做小样本，不追求数量。5.4 可以联网下载或保存官方页面/PDF，但每条都必须先落到 source packet。

验证：

- T1/T2/T3/T4/T5 是否能分清。
- 特殊类型是否能隔离。
- `group_code` 是否能识别。
- `rank_source` 是否能标注。
- duplicate key 是否能检查。

### 第 3 步：建立 source queue

优先队列：

1. 广西考试院 2024/2025 本科普通批物理类院校专业组投档线。
2. 2024/2025 一分一档表。
3. 强双非/区内高校/行业特色高校官方招生计划与录取分数。
4. 32 所 decision pool 可作为 anchor，但只标记 anchor，不复制低置信逻辑。

联网要求：

- 每个联网来源都要保留 `source_url`、页面标题、发布时间、官方主体、原始文件路径或缓存路径。
- 优先官方来源；第三方只可作为索引线索，不能直接成为 T1/T2。
- 若来源需要 Deep Research、浏览器态、cookie/header、表单 replay，应在 source packet 中标记 `requires_manual_or_deep_research=true`，不要直接抓成最终数据。

### 第 4 步：150-220 个 strict group-year seed

48 小时目标：

- 150-220 个 strict group-year
- 以 2024/2025 为主
- 40-60 所学校
- 每校 2-4 个普通专业组优先
- 覆盖目标分数带上下沿
- 2023 只进 bridge/background，不进入 strict calibration

### 第 5 步：报告和交接

产出：

- `reports/reference_trend_pool_seed_coverage_rollup.csv`
- `reports/reference_trend_pool_qa_report.csv`
- `reports/reference_trend_exclusion_log.csv`
- `docs/reference_trend_pool_48h_execution_report.md`

## 11. 位次带抽样建议

不要按学校数平均抽样，要按位次带分层。

先用当年一分一档表把 550-620 分换算成当年 rank band，再抽样：

- 核心目标带：550-620 对应位次区间，占 50%。
- 上沿冲刺带：高于 620 或目标位次上沿再向上扩一段，占 15%。
- 下沿保底带：低于 550 或目标位次下沿再向下扩 10,000-20,000 位，占 20%。
- 结构参照带：强双非、区内强校、行业特色学校、同专业方向相近组，占 15%。

## 12. 5.4 不要做的事

不要：

1. 直接扩 32 所 decision pool。
2. 把趋势池数据写入 canonical。
3. 打开 ML。
4. 把 2023 理科旧口径硬拼到 2024/2025 专业组趋势。
5. 把学校最低分当专业组最低分。
6. 把特殊类型混入普通批。
7. 让资料搜集线程和数据整理线程同时写一张最终表。
8. 直接把 non-211 discovery candidates 当干净趋势样本。
9. 用 Deep Research 直接生成最终数据。

5.4 允许联网，也允许在必要时使用 Deep Research，但 Deep Research 只能用于：

- 找广西考试院原始表；
- 找 G4 blocked source 的官方入口；
- 找非 211 官方招生计划/分数页；
- 找 2024/2025 广西物理类普通批官方投档线、一分一档表和官方 PDF/HTML 原始位置；
- 输出 source packet，不直接入池，不直接给趋势结论。

## 13. 推荐首轮交付物

5.4 接手后的首轮最好只交付这些：

1. `docs/reference_trend_pool_schema.md`
2. `clean_data/engineering_guangxi_seed/reference_trend_source_packet_template.csv`
3. `clean_data/engineering_guangxi_seed/reference_trend_seed_queue_preview.csv`
4. `reports/reference_trend_pool_schema_coverage_rollup.csv`
5. `docs/reference_trend_pool_48h_execution_plan.md`

完成前四个后即可启动资料搜集线程；整理线程继续维护 schema、QA 和准入规则。两条线程可以并行，但资料线程只写 source packet，整理线程只写 intake/QA/exclusion preview，不能同时写最终池。

## 14. 快速阅读清单

接手前请先读：

1. `docs/trend_reference_pool_pivot.md`
2. `docs/gptpro_trend_pivot_evidence_manifest.md`
3. `docs/project_bottleneck_summary_pack.md`
4. `docs/pre_ml_data_sufficiency_audit.md`
5. `docs/pre_ml_p0_caution_repair_reassessment.md`
6. `docs/pre_ml_p1_targeted_thickening_before_rebuild.md`

如果只读一份：读 `docs/trend_reference_pool_pivot.md`。  
如果只看数据：看 `clean_data/engineering_guangxi_seed/guangxi_pre_ml_data_thickening_priority_queue_merged.csv` 和 `reports/engineering_pre_ml_data_sufficiency_audit_coverage_rollup.csv`。

## 15. 一句话接力指令

请把当前项目从“32 所 decision pool 的逐行完美化”切到“隔离 reference trend pool 的 schema 与 seed queue 建设”。保留 32 所主池，不扩主池，不开 ML；先做 source packet 模板、trend intake schema、QA/准入规则和 48 小时 seed queue。

## 16. 2026-05-16 自动化增量

已新增中国地质大学（北京）官方缓存 group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_cugb_group_mapping_workbench.csv`
- `reports/reference_trend_cugb_group_mapping_rollup.csv`
- `reports/reference_trend_cugb_group_mapping_qa.csv`
- `docs/reference_trend_cugb_group_mapping.md`

覆盖结果：workbench 53 行，其中专业分候选 9 行、计划候选 44 行；考试院普通组线为 2024 年 101/102/103、2025 年 101/102；校方缓存没有直接给广西院校专业组代码，因此全部保持 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`。该批只作为 32 所 decision pool 的 source evidence / mapping workbench，不进入统计背景。

下一轮优先级：若没有人工新增 intake，先处理最新出现的南京航空航天大学官方缓存行；否则回到 P0/P1 非主池官方计划来源发现队列。

## 17. 2026-05-16 南航边界增量

已新增南京航空航天大学官方缓存 group boundary workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_nanhang_group_boundary_workbench.csv`
- `reports/reference_trend_nanhang_group_boundary_rollup.csv`
- `reports/reference_trend_nanhang_group_boundary_qa.csv`
- `reports/reference_trend_nanhang_group_boundary_exclusion_log.csv`
- `docs/reference_trend_nanhang_group_boundary_workbench.md`

覆盖结果：workbench 44 行，其中 2024 专业分 19 行、2025 计划 21 行、2024 概况 4 行。考试院普通组线为 2024 年 `101:618/3954`、2025 年 `101:615/3507`；2025 年 `303:578/12953` 是未备注分组，必须继续 hold。南航 2024 专业分 API 未给最低位次，也未给广西院校专业组代码；因此全部保持 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，只作为 32 所 decision pool 的 source evidence / boundary QA。

下一轮优先级：若没有人工新增 intake 或新的官方 source packet，回到 `reference_trend_520_plan_discovery_query_pack.csv` / `reference_trend_520_plan_source_packet_queue.csv` 的 P0/P1 非主池官方计划来源发现任务。

## 18. 2026-05-16 P0/P1 官方来源发现 batch 3

已新增 P0/P1 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch3_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch3_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch3_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch3.md`

覆盖结果：7 条官方候选，覆盖 6 所学校：哈尔滨医科大学、天津中医药大学、天津理工大学、宁波诺丁汉大学、安徽中医药大学、广西师范大学。全部仍是 source discovery preview，`reference_trend_pool_eligible=0`、`canonical_ml_entry_open=false`。

可优先本地解析的 T1 候选：

- 哈尔滨医科大学 2025 校本部本科招生计划：官方 HTML 表，可解析广西列，但无院校专业组代码，含国家专项列需隔离。
- 宁波诺丁汉大学 2025 招生计划 PDF：官方 PDF 可读，需做广西列对齐，并保留中外合作/whole-school boundary。
- 广西师范大学 2025 广西招生计划：官方 HTML 表，可解析普通类/物理类/本科普通批行，但需剔除国家专项、地方专项、民族班、提前批等。

需要人工批准浏览器/OCR/表单态的候选：

- 天津中医药大学 2025 广西本科招生计划及 2024 录取情况：官方页面存在，但主体为图片，需要 OCR 或浏览器截图。
- 天津理工大学 2025 普通本科招生计划：官方入口指向查询页，需要浏览器/表单端点。
- 安徽中医药大学 2025 普通本科招生计划：官方页面存在，但主体为图片/资产，需要 OCR 或资源提取。

下一轮优先级：先解析 T1 候选形成 source_packet parse preview 和 QA；对 3 条需要 OCR/browser/form 的候选只保留 backoff，等待人工批准。

## 19. 2026-05-16 batch3 T1 source packet parse

已新增 batch3 T1 官方来源解析层：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch3_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch3_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch3_t1_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch3_t1_source_packet_parse.md`

覆盖结果：共生成 source-packet parse preview 272 行，其中广西师范大学普通类/物理类/本科普通批行 53 行、计划合计 2002；哈尔滨医科大学广西普通列合计 37、国家专项列合计 13；宁波诺丁汉 PDF 已抽出文本但仍需人工列对齐。

准入边界：本轮 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是这三类官方计划源均未给广西院校专业组代码，且 UNNC PDF 仍需人工列对齐；它们只进入 source_packet / mapping / QA 层，不进入 canonical、ML 或 32 所 decision_pool。

下一轮优先级：若无人工新增 intake，继续处理 P0/P1 官方计划来源发现队列；若用户批准浏览器/OCR/form，再处理天津中医药、天津理工、安徽中医药三条 batch3 T2 候选。

## 20. 2026-05-16 P0/P1 官方来源发现 batch 4

已新增 batch4 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch4_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch4_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch4_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch4_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch4.md`

覆盖结果：候选 9 行，覆盖 5 所学校。高价值优先解析目标是广西科技大学官方专业组 PDF、昆明理工大学官方计划 PDF、昆明理工大学官方分专业分数/位次 PDF、江苏大学 2025 广西录取情况 HTML。江西理工/江苏大学计划门户仍需端点发现；沈阳航空航天计划 PDF 与分数 XLSX 附件存在验证码下载边界，先进入 backoff，不用终端硬抓。

准入边界：本轮仍是 source discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。

下一轮优先级：先解析广西科技大学和昆明理工大学官方 PDF；若 PDF 解析受阻，再做江苏大学 HTML 分数参考解析。

## 21. 2026-05-16 batch4 source packet parse

已新增 batch4 官方来源解析层：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch4_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch4_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch4_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch4_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch4_source_packet_parse.md`

覆盖结果：parse preview 99 行。广西科技大学官方专业组 PDF 解析出 12 个组，其中普通物理组 8 个；昆明理工大学官方分专业分数/位次 PDF 解析出广西行 55 行，其中物理类 52 行；江苏大学官方广西录取 HTML 解析出 31 行，其中普通物理类 16 行。

准入边界：本轮 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。GXUST 有组结构但缺分数/位次/计划数；KMUST 有专业分/位次但缺组代码；UJS 有专业分和录取人数但缺位次/组代码。全部只进入 source_packet / mapping / QA 层。

下一轮优先级：先把广西科技大学 2025 组代码与考试院投档线 join 成 group-line workbench；再用 KMUST/UJS 专业分数行做 group mapping QA。若本地考试院行不可用，则继续 P0/P1 官方来源发现。

## 22. 2026-05-16 广西科技大学 group-line workbench

已新增广西科技大学 group-line workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_gxust_group_line_workbench.csv`
- `reports/reference_trend_gxust_group_line_workbench_rollup.csv`
- `reports/reference_trend_gxust_group_line_workbench_qa.csv`
- `reports/reference_trend_gxust_group_line_workbench_exclusion_log.csv`
- `docs/reference_trend_gxust_group_line_workbench.md`

覆盖结果：workbench 17 行，官方专业组结构 12 行，其中普通物理组 8 行已精确 join 到 2025 广西考试院投档线；另有 5 条 2025 考试院组线未在当前 PDF 解析出的普通组结构中出现，需要边界分类。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是计划数尚未解析；该表只作为 group-line / source-packet QA 工作台，不进入 canonical、ML 或 32 所 decision_pool。

下一轮优先级：寻找/解析广西科技大学官方 2025 分组计划数；若无安全来源，则继续处理昆明理工大学或江苏大学的 group mapping QA。

## 23. 2026-05-16 昆明理工/江苏大学 group mapping QA

已新增 KMUST/UJS group mapping QA 工作台：

- `clean_data/engineering_guangxi_seed/reference_trend_kmust_ujs_group_mapping_qa_workbench.csv`
- `reports/reference_trend_kmust_ujs_group_mapping_qa_rollup.csv`
- `reports/reference_trend_kmust_ujs_group_mapping_qa.csv`
- `reports/reference_trend_kmust_ujs_group_mapping_qa_exclusion_log.csv`
- `docs/reference_trend_kmust_ujs_group_mapping_qa.md`

覆盖结果：workbench 86 行，其中昆明理工大学 55 行、江苏大学 31 行。昆明理工有 6 条分数等于考试院组线的 floor 候选，46 条多组阈值候选；江苏大学有 16 条普通物理单一组候选。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。KMUST 缺官方组代码，UJS 缺位次/组结构，全部只作为 mapping QA。

下一轮优先级：继续寻找 KMUST 官方分组计划/组结构或 UJS 计划/位次来源；若无安全来源，回到 P0/P1 官方来源发现队列。


## 24. 2026-05-16 哈尔滨医科大学 group mapping workbench

已新增 HRBMU group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_hrbmu_group_mapping_workbench.csv`
- `reports/reference_trend_hrbmu_group_mapping_rollup.csv`
- `reports/reference_trend_hrbmu_group_mapping_qa.csv`
- `reports/reference_trend_hrbmu_group_mapping_exclusion_log.csv`
- `docs/reference_trend_hrbmu_group_mapping.md`

覆盖结果：workbench 22 行；普通物理计划行 19 行，计划合计 32；legacy 非物理 hold 计划合计 5，两者合计回到 HRBMU 广西普通列总数 37；国家专项 hold 1 行，计划合计 13。2025 广西考试院普通物理组线候选为 151:562/19311|152:563/18857|153:496/58830|154:519/42974|156:450/96667|157:454/92968|158:453/93925|159:447/99362；520 窗口重点 delta 为 10226-153:38102->58830(20728)|10226-154:38102->42974(4872)。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。HRBMU 官方表有计划数但无广西院校专业组代码，只能作为 mapping QA，不进入 trend pool/canonical/ML。

下一轮优先级：继续找 HRBMU 官方组结构或可审计的院校专业组映射；若没有安全来源，回到 P0/P1 官方计划来源发现队列。


## 25. 2026-05-16 plan source queue status reconciliation

已新增 plan source 队列状态对账层：

- `clean_data/engineering_guangxi_seed/reference_trend_520_plan_source_queue_status_reconciliation.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_rollup.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_qa.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_exclusion_log.csv`
- `docs/reference_trend_520_plan_source_queue_status_reconciliation.md`

覆盖结果：对账 457 个 plan-source 队列项；P0 队列 117 行，其中已有 discovery/source_packet/mapping artifact 的 P0 行为 27，仍需新官方来源发现的 P0 行为 90。已有 artifact 覆盖 19 所学校。

准入边界：这是 queue-routing 层，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。用途是避免重复搜已经进入 source_packet/mapping QA 的学校，并把下一轮自动化路由到真正缺源的 P0/P1 项。

下一轮优先级：先处理 `needs_official_source_discovery` 的 P0 行；已有 mapping/workbench 的学校优先补官方组结构或人工可审计映射规则，不重复做泛搜。


## 26. 2026-05-16 P0 官方来源发现 batch 5

已新增 batch5 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch5_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch5_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch5.md`

覆盖结果：候选 8 行，覆盖 6 所学校。河南理工大学出现 2 条 T1 高价值官方源：全国招生来源计划 PDF 与广西分专业录取分数页；安徽财经大学、成都工业学院、浙大城市学院为官方招生门户待端点/资产 drilldown；成都师范学院和沈阳理工大学本轮仍是 backoff/需重搜。

准入边界：本轮仍是 source discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。

下一轮优先级：优先解析河南理工大学官方 PDF/HTML；其余官方门户进入 endpoint 或资产 drilldown，backoff 学校继续定向搜索官方来源。

## 27. 2026-05-16 河南理工大学 2025 官方 source packet parse

已新增河南理工大学 2025 广西官方 source packet 解析层：

- `clean_data/engineering_guangxi_seed/reference_trend_hpu_2025_source_packet_parse_preview.csv`
- `reports/reference_trend_hpu_2025_source_packet_parse_rollup.csv`
- `reports/reference_trend_hpu_2025_source_packet_parse_qa.csv`
- `reports/reference_trend_hpu_2025_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_hpu_2025_source_packet_parse.md`

覆盖结果：官方广西分专业录取页解析出 29 条专业行；官方招生来源计划 XLSX 广西列与 score 页计划总数均为 60。普通物理非中外合作专业行 25 条，计划合计 50；中外合作 301 组与历史 106 组均隔离。物理类 27/27 行与 XLSX 计划数一致；历史类法学/工商管理在 score 页与 XLSX 中存在 3/1 vs 2/2 的专业内分配差异，但历史组不进入物理趋势校准。

准入边界：本轮只生成 source_packet parse preview 和 derived group-summary QA candidate；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先把 101-105 组与广西考试院 2025 物理普通批院校专业组投档线匹配，确认 group floor 后再进入 reference_trend intake preview。


## 28. 2026-05-16 河南理工大学 group-line workbench

已新增河南理工大学 group-line workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_hpu_group_line_workbench.csv`
- `reports/reference_trend_hpu_group_line_workbench_rollup.csv`
- `reports/reference_trend_hpu_group_line_workbench_qa.csv`
- `reports/reference_trend_hpu_group_line_workbench_exclusion_log.csv`
- `docs/reference_trend_hpu_group_line_workbench.md`

覆盖结果：workbench 8 行；101-105 共 5 个普通物理组已完成“校方官方分专业/计划数/组内最低”与广西考试院 2025 组投档线并排核验，普通物理计划合计 50。101/102/104/105 有 2024/2025 matched delta；103 为 2025-only 新增/重组候选。301 中外合作、106 历史、2024-only 310 均隔离。

准入边界：本轮只产生 workbench / intake-candidate 层，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可把 101-105 写成 reference_trend intake preview 候选，或继续处理下一个 P0/P1 官方计划源。


## 29. 2026-05-16 河南理工大学 group-line intake preview

已新增河南理工大学 group-line intake preview 候选层：

- `clean_data/engineering_guangxi_seed/reference_trend_hpu_group_line_intake_preview.csv`
- `reports/reference_trend_hpu_group_line_intake_preview_rollup.csv`
- `reports/reference_trend_hpu_group_line_intake_preview_qa.csv`
- `reports/reference_trend_hpu_group_line_intake_preview_exclusion_log.csv`
- `docs/reference_trend_hpu_group_line_intake_preview.md`

覆盖结果：101-105 五个普通物理组均找到既有全局 `reference_trend_intake_preview` group-year 记录，因此本轮不追加全局 intake，改为生成 plan/major-structure enrichment preview。候选计划合计 50；101/102 为 higher selectivity，104/105 为 lower selectivity，103 为 2025-only 无同码 delta。

准入边界：本轮仅 `calibration_eligible_candidate=true`，正式 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可批量接受该 enrichment，或继续处理下一个 P0/P1 官方计划源。


## 30. 2026-05-16 P0 官方来源发现 batch 6 + 浙大城市学院图片计划解析

已新增 batch6 官方来源发现与 ZUCC 图片计划解析预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch6_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch6_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch6.md`
- `clean_data/engineering_guangxi_seed/reference_trend_zucc_2025_plan_image_parse_preview.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_rollup.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_qa.csv`
- `reports/reference_trend_zucc_2025_plan_image_parse_exclusion_log.csv`
- `docs/reference_trend_zucc_2025_plan_image_parse.md`

覆盖结果：batch6 候选 8 行，覆盖 4 所学校。浙大城市学院官方广西计划页与图片资产已缓存，图片解析出 17 个专业行，广西物计划合计 80、广西史计划合计 10；但图片无专业组代码，因此仍停留在 source_packet parse preview。浙江传媒学院官方信息公开页和本科招生网入口已缓存，但未得到广西物理普通批结构化行；滨州医学院官方计划查询入口已缓存但需要表单/端点 replay；湖南医药学院官方计划页存在 TLS/reachability 阻塞。

准入边界：`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。本轮不进入 canonical/ML，不并入 32 所 decision_pool。

下一轮优先级：优先核验 ZUCC 广西考试院 13021-102 是否唯一/对应该 80 人物理计划；若无法本地核验，则继续处理下一个 P0/P1 官方计划源，或在人工批准后对 BZMC 查询系统做 browser/form replay。


## 31. 2026-05-16 浙大城市学院 group mapping workbench

已新增 ZUCC group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_zucc_group_mapping_workbench.csv`
- `reports/reference_trend_zucc_group_mapping_rollup.csv`
- `reports/reference_trend_zucc_group_mapping_qa.csv`
- `reports/reference_trend_zucc_group_mapping_exclusion_log.csv`
- `docs/reference_trend_zucc_group_mapping.md`

覆盖结果：本地考试院 intake 显示浙大城市学院 2025 广西物理类有 101、102 两个专业组；官网图片只有合并的“广西物”计划总数 80，不打印专业组边界。因此明确禁止把 80 人整包挂到 `13021-102`。`13021-102` 的 2024/2025 分数位次趋势仍可保留为 score/rank-only：518/44178 -> 502/54559，rank delta +10381，方向 cooler/lower selectivity。

准入边界：本轮仅 group-mapping workbench，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮继续找 ZUCC 官方组内计划拆分/专业到组映射；若找不到，则回到下一个 P0/P1 官方计划源。


## 32. 2026-05-16 plan source queue status reconciliation refresh

已刷新 plan source 队列状态对账层：

- `clean_data/engineering_guangxi_seed/reference_trend_520_plan_source_queue_status_reconciliation.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_rollup.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_qa.csv`
- `reports/reference_trend_520_plan_source_queue_status_reconciliation_exclusion_log.csv`
- `docs/reference_trend_520_plan_source_queue_status_reconciliation.md`

覆盖结果：对账 457 个 plan-source 队列项；P0 队列 117 行，其中已有 discovery/source_packet/mapping artifact 的 P0 行为 40，仍需新官方来源发现的 P0 行为 77。已有 artifact 覆盖 28 所学校。

准入边界：这是 queue-routing 层，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。用途是避免重复搜已经进入 source_packet/mapping QA 的学校，并把下一轮自动化路由到真正缺源的 P0/P1 项。

下一轮优先级：先处理 `needs_official_source_discovery` 的 P0 行；已有 mapping/workbench 的学校优先补官方组结构或人工可审计映射规则，不重复做泛搜。


## 33. 2026-05-16 P0 官方来源发现 batch 7

已新增 batch7 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch7_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch7_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch7.md`

覆盖结果：queue rank 33-41 共 9 所学校。石河子大学官方招生计划 JS 已缓存并可抽取广西本科普通批物理类 32 个专业行、计划合计 100；福建理工大学官方广西计划 HTML 表已缓存，可抽取物理类 38 个专业行、计划合计 205。西南医科大学官方附件页已缓存，但 XLS 下载有验证码；贵州财经大学官方 PDF 候选出现 TLS 阻塞；青海大学官方页只给外部海报入口；福建中医药大学、西安石油大学、陕西中医药大学本轮未找到 first-party 结构化计划源；西安外国语大学候选官方链接为 404。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先把石河子大学/福建理工大学两条 T1 来源解析成 source-packet parse preview，并继续 hold group-year calibration，直到专业组映射被人工接受。


## 34. 2026-05-16 batch7 T1 source-packet parse preview

已新增 batch7 两条 T1 官方来源的 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch7_t1_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch7_t1_source_packet_parse.md`

覆盖结果：石河子大学官方 JS 数据解析出广西本科普通批物理类 32 个专业行，计划合计 100；福建理工大学官方广西计划 HTML 表解析出物理类 38 个专业行，计划合计 205（物理+化学 110，物理+不限 95）。

准入边界：两校来源均不打印广西院校专业组代码，`queue_group_code` 只保留为队列上下文，`source_group_code` 为空。`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先做石河子/福建理工 group mapping workbench，或继续下一个 P0 官方来源发现批次。


## 35. 2026-05-16 batch7 group mapping workbench

已新增 batch7 group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch7_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch7_group_mapping_qa.csv`
- `reports/reference_trend_520_batch7_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch7_group_mapping.md`

覆盖结果：石河子大学官方计划总数 100，但广西考试院 2025 物理类有 101/102/104 三个专业组；福建理工大学官方计划总数 205（物理+化学 110、物理+不限 95），但广西考试院 2025 物理类有 150/199/759 三个组，且 759 为预科类隔离。两校官方计划源均不打印广西专业组代码。

准入边界：本轮只做 group mapping workbench，所有计划数仍未分配到 group-year；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可继续找官方组码/专业到组映射，或从 P0 rank 42 上海应用技术大学继续官方来源发现。


## 36. 2026-05-16 P0 官方来源发现 batch 8

已新增 batch8 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch8_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch8.md`

覆盖结果：queue rank 42、43、44、46、48、49、50 共 7 所学校。中南林业科技大学官方广西招生计划两页已缓存，可抽取 2025 本科普通批物理类专业行与计划数，但不打印广西院校专业组代码。上海应用技术大学、上海立信会计金融学院、中南财经政法大学只获得官方章程/规则上下文，未获得结构化广西计划表；上海第二工业大学官方候选页终端访问超时，保留在 reachability/backoff；中国人民警察大学与中央美术学院保留为特殊类型/章程边界上下文。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先把中南林业科技大学 T1 来源解析成 source-packet parse preview，并继续 hold group-year calibration，直到专业组映射被人工接受。


## 37. 2026-05-16 batch8 T1 source-packet parse preview

已新增 batch8 T1 官方来源的 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch8_t1_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch8_t1_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch8_t1_source_packet_parse.md`

覆盖结果：中南林业科技大学官方广西招生计划两页解析出 2025 本科普通批物理类 41 个专业行，计划合计 150。

准入边界：来源不打印广西院校专业组代码，`queue_group_code=106` 只保留为队列上下文，`source_group_code` 为空。`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先做中南林业科技大学 group mapping workbench，或继续下一个 P0 官方来源发现批次。


## 38. 2026-05-16 batch8 group mapping workbench

已新增 batch8 group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch8_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch8_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch8_group_mapping_qa.csv`
- `reports/reference_trend_520_batch8_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch8_group_mapping.md`

覆盖结果：中南林业科技大学官方 2025 广西本科普通批物理类计划共 41 个专业行、计划合计 150；本地广西考试院 2025 物理类同校有 104/106/108 三个专业组。官方计划源提供选科要求和计划数，但不打印广西院校专业组代码。

准入边界：本轮只做 group mapping workbench，150 人计划总数仍未分配到 group-year；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可继续找官方组码/专业到组映射，或推进下一个 P0 官方来源发现批次。


## 39. 2026-05-16 P0 官方来源发现 batch 9

已新增 batch9 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch9_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch9.md`

覆盖结果：queue rank 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62, 64。北方工业大学命中官方 2025 本科分专业招生计划 HTML 表，广西列可见，是本批唯一 T1 可解析候选；云南师范大学命中官方参数化计划门户，五邑大学命中官方外省计划图片页，华侨大学命中官方计划页但 403，南昌航空大学命中官方查询入口上下文，四川轻化工大学命中官方附件包候选。北京建筑大学、华北理工大学本轮未找到可接收的一方广西计划源。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先解析北方工业大学 T1 HTML 表；涉及云南师范大学 API/五邑大学图片 OCR/华侨大学 403/四川轻化工附件下载时继续等待人工批准或走可审计路线。


## 40. 2026-05-16 batch9 北方工业大学 source-packet parse preview

已新增 batch9 北方工业大学 T1 官方来源的 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch9_ncut_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch9_ncut_source_packet_parse.md`

覆盖结果：北方工业大学官方 2025 本科分专业招生计划 HTML 表已缓存，广西列解析出 37 个专业行、计划合计 57。其中艺术设计类和中外合作办学行已标记为特殊边界，未删除。

准入边界：来源不打印广西院校专业组代码，也不打印选科/物理类标签；`queue_group_code=304` 只保留为队列上下文，`source_group_code` 为空。`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先做北方工业大学 group/subject mapping workbench，或继续下一个 P0 官方来源发现批次。


## 41. 2026-05-16 batch9 北方工业大学 group mapping workbench

已新增 batch9 北方工业大学 group/subject mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch9_ncut_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_qa.csv`
- `reports/reference_trend_520_batch9_ncut_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch9_ncut_group_mapping.md`

覆盖结果：北方工业大学官方 2025 广西列计划共 37 个专业行、计划合计 57；其中未标记普通样态计划 48，特殊边界为 `art_design_boundary:4;sino_foreign_cooperation:5`。本地广西考试院 2025 物理类同校有 102、103、304、500 组，500 组为特殊/混合边界。

准入边界：官方计划源不打印广西院校专业组代码，也不打印选科/物理类标签；所有计划数仍未分配到 group-year，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可继续找北方工业大学官方组码/选科映射，或推进下一个 P0 官方来源发现批次。


## 42. 2026-05-16 P0 官方来源发现 batch 10

已新增 batch10 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch10_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch10.md`

覆盖结果：queue rank 63, 65, 67, 68, 70, 71, 72, 73, 74, 75。宁夏医科大学官方计划页和 PDF 已缓存但未解析；宁夏大学官方计划查询系统入口和章程已缓存但需要参数/API drilldown；山东政法学院官方计划页已缓存，广西计划在嵌入图片中，需要 OCR/图片解析；天津外国语大学官方章程和计划栏目已缓存但未暴露结构化广西计划行。大连医科大学中山学院官方计划页遇到 TLS 证书阻塞，安徽理工大学官方候选页 404，四川师范大学/山东师范大学本轮未找到可接收的一方广西计划源。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先解析宁夏医科大学 PDF（若可用 PDF parser），或推进下一个 P0 官方来源发现批次。


## 43. 2026-05-16 batch10 asset parse readiness

已新增 batch10 asset parse readiness 预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch10_asset_parse_readiness_preview.csv`
- `reports/reference_trend_520_batch10_asset_parse_readiness_rollup.csv`
- `reports/reference_trend_520_batch10_asset_parse_readiness_qa.csv`
- `reports/reference_trend_520_batch10_asset_parse_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch10_asset_parse_readiness.md`

覆盖结果：宁夏医科大学官方 PDF 已缓存，但本地缺少 PDF text parser；山东政法学院官方页面已提取广西计划嵌入图片 URL，但远程图片/OCR 需审批；宁夏大学官方计划门户已缓存但还需 API/form drilldown；天津外国语大学仅有官方上下文，未暴露结构化广西计划行；大连医科大学中山学院 TLS 阻塞、安徽理工大学候选页 404 均保留在 backoff。

准入边界：本轮只生成 asset readiness/exclusion，不解析入 reference_trend_pool；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮若无 PDF parser/OCR/browser/form 批准，应继续后续 P0 官方来源发现批次。


## 44. 2026-05-16 P0 官方来源发现 batch 11

已新增 batch11 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch11_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch11_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch11_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch11_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch11.md`

覆盖结果：queue rank 76-90。山东科技大学命中官方招生计划文章和 PDF；广东海洋大学命中官方计划页但附件下载有验证码；惠州学院命中官方招生简章/省外计划 PDF 候选；武汉轻工大学命中官方信息公开计划入口但需缓存解析。延边大学、成都中医药大学仅命中官方章程/上下文，不是计划行来源；山东财经大学、广东石油化工学院、成都师范学院、江苏师范大学、河北大学本轮没有可接收的一方广西计划源或仅有第三方引用。

准入边界：本轮只生成 source discovery preview，未缓存/解析 PDF 或 HTML 表；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先缓存/解析山东科技大学、惠州学院、武汉轻工大学的官方计划候选；广东海洋附件需验证码/浏览器态批准。


## 45. 2026-05-16 batch11 parse readiness

已新增 batch11 parse readiness 预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch11_parse_readiness_preview.csv`
- `reports/reference_trend_520_batch11_parse_readiness_rollup.csv`
- `reports/reference_trend_520_batch11_parse_readiness_qa.csv`
- `reports/reference_trend_520_batch11_parse_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch11_parse_readiness.md`

覆盖结果：山东科技大学与惠州学院的官方 PDF 均可见文本层，适合下一步缓存 PDF 后做 source-packet parse preview；武汉轻工大学官方列表可见 2025 分省分专业招生计划数入口，但明细页本轮 cache miss；广东海洋大学两个官方附件链接均返回验证码下载页，继续 approval-gated。

准入边界：本轮只做解析准备分流，不进入 reference_trend_pool/canonical/ML；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮优先缓存/解析山东科技大学和惠州学院 PDF；广东海洋等待人工附件或浏览器态批准。


## 46. 2026-05-16 batch11 PDF cache receipt

已新增 batch11 PDF cache receipt / parse preflight：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch11_pdf_cache_receipt_preview.csv`
- `reports/reference_trend_520_batch11_pdf_cache_receipt_rollup.csv`
- `reports/reference_trend_520_batch11_pdf_cache_receipt_qa.csv`
- `reports/reference_trend_520_batch11_pdf_cache_receipt_exclusion_log.csv`
- `docs/reference_trend_520_batch11_pdf_cache_receipt.md`

覆盖结果：山东科技大学、惠州学院官方 PDF 已缓存到 `raw_sources/reference_trend/batch11_official/`。网页层可见文本抽取，说明 PDF 不是死资产；但本地缺少 `pdftotext/qpdf/mutool/gs` 等表格/文本解析路线，且 PDF 是横向多列计划表，不能用扁平文本顺序硬猜广西列。

准入边界：本轮只做缓存收据和解析前置 QA，不进入 reference_trend_pool/canonical/ML；`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一轮可继续后续 P0 来源发现，或在有可靠 PDF 表格解析/人工转录路线后解析这两个 PDF。


## 47. 2026-05-16 P0 官方来源发现 batch 12

已新增 batch12 官方来源发现/既有候选承接预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch12_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch12_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch12_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch12_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch12.md`

覆盖结果：queue rank 91-110。河南理工大学、浙江传媒学院、西南医科大学、贵州财经大学承接前序非 canonical 候选状态，避免重复发现；湖南中医药大学命中官方 HTML 计划表，是本批唯一 T1 parse-ready 候选；浙江海洋大学、温州医科大学、重庆中医药学院命中官方计划/计划分数候选但尚未缓存解析；重庆科技大学命中招生计划查询入口但需 endpoint/form drilldown。浙江科技大学、温州大学、湖北工业大学、辽宁大学、重庆工商大学、长江大学目前只保留官方上下文或 score-only 参考；湘南学院、西安财经大学、西藏大学、郑州轻工业大学、长春理工大学本轮未找到可接收的一方广西计划源。

准入边界：本轮只生成 source discovery preview，不缓存/解析 PDF、endpoint、图片、附件或 HTML 表；所有行 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先解析湖南中医药大学官方 HTML 表；西南医科 captcha、贵州财经 PDF 替代抓取、重庆科技 endpoint/form/browser 路线继续 approval-gated。


## 48. 2026-05-16 batch12 湖南中医药大学 source-packet parse preview

已新增湖南中医药大学官方 HTML 表 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch12_hnucm_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch12_hnucm_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch12_hnucm_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch12_hnucm_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch12_hnucm_source_packet_parse.md`

覆盖结果：官方 2025 分省分专业招生计划 HTML 已缓存到 `raw_sources/reference_trend/batch12_official/hnucm_2025_plan.html`。已处理 HTML 表格 rowspan/colspan，广西全科类发布合计 105，解析出的广西全科类计划合计 105；其中广西物理/理科类专业行 32 行、计划合计 91。非物理类行已写入 exclusion，不混入物理趋势预览。

准入边界：来源提供专业-省份计划数，但不打印广西院校专业组代码；`queue_group_code=105` 只保留为队列上下文，不能作为 source_group_code。所有行 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮若要推进，需要寻找可靠的官方组码/专业映射，或继续 batch12 中浙江海洋大学、温州医科大学、重庆中医药学院等候选的缓存解析。


## 49. 2026-05-16 batch12 asset/API readiness

已新增 batch12 asset/API readiness 预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch12_asset_api_readiness_preview.csv`
- `reports/reference_trend_520_batch12_asset_api_readiness_rollup.csv`
- `reports/reference_trend_520_batch12_asset_api_readiness_qa.csv`
- `reports/reference_trend_520_batch12_asset_api_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch12_asset_api_readiness.md`

覆盖结果：浙江海洋大学官方广西计划/分数页与两张大图已缓存，但仍需 OCR 或人工转录；温州医科大学官方计划页 TLS 阻塞，未形成本地资产；重庆中医药学院正确 bkzs 章程页和计划门户已缓存，章程页暴露 2 张 2025 计划图片，静态计划门户可见表头，但本轮尝试的 `/enroll-portal/api/v1/plan` 相关 API 均返回 404 HTML；重庆工商大学继续保留为无可解析资产的后续发现项。

准入边界：本轮只生成 asset/API readiness、QA 和 exclusion，不做 OCR、form replay、header/cookie replay，也不解析入 reference_trend_pool；所有行 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮若无 OCR/browser/form/TLS 批准，应继续后续 P0/P1 官方来源发现或做已缓存图片的人工转录审批准备。


## 50. 2026-05-16 P0/P1 官方来源发现 batch 13

已新增 batch13 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch13_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch13_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch13_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch13_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch13.md`

覆盖结果：queue rank 111-130。集美大学、青海大学、华侨大学、哈尔滨医科大学、四川轻化工大学、安徽工业大学、河南科技大学形成一方官方计划候选，下一步可缓存明细页/图片/附件后做 source-packet parse preview；广东海洋大学、浙江传媒学院承接既有非 canonical/approval-gated 状态；陕西科技大学、南京工程学院、无锡学院本轮只找到第三方或媒体上下文，已明确拒绝进入 intake；青岛理工大学、上海应用技术大学、成都大学、桂林理工大学目前只有官方章程/门户上下文，不能作为计划行来源。

准入边界：本轮只生成 source discovery preview、QA 和 exclusion；所有行 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先缓存/解析河南科技大学、华侨大学、四川轻化工大学、哈尔滨医科大学；青海大学和安徽工业大学图片/OCR 路线需审批。


## 51. 2026-05-16 batch13 cache parse preflight

已新增 batch13 cache/parse preflight：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_cache_parse_preflight_preview.csv`
- `reports/reference_trend_520_batch13_cache_parse_preflight_rollup.csv`
- `reports/reference_trend_520_batch13_cache_parse_preflight_qa.csv`
- `reports/reference_trend_520_batch13_cache_parse_preflight_exclusion_log.csv`
- `docs/reference_trend_520_batch13_cache_parse_preflight.md`

覆盖结果：已缓存河南科技大学、华侨大学、四川轻化工大学、哈尔滨医科大学官方候选页，并进一步缓存哈尔滨医科大学广西计划明细页。河南科技大学与哈尔滨医科大学可从官方 HTML 表抽取专业级广西物理/理科计划预览；华侨大学本轮只得到广西省份/科类汇总，不是专业/组级记录；四川轻化工大学计划为图片资产，需 OCR 或人工转录审批。

准入边界：本轮只做 source-packet parse preview/preflight。已解析的专业行仍未打印院校专业组代码，也没有分数/位次映射，因此 `reference_trend_pool_eligible=false`、`calibration_eligible=false`、`canonical_ml_entry_open=false`；不进入 32 所 decision_pool。下一轮可继续缓存/解析集美大学官方计划明细，或准备青海大学/安徽工业大学图片 OCR/人工转录审批。


## 52. 2026-05-16 batch13 集美大学 source-packet parse preview

已新增集美大学官方广西计划 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_source_packet_parse_preview.csv`
- `reports/reference_trend_520_batch13_jmu_source_packet_parse_rollup.csv`
- `reports/reference_trend_520_batch13_jmu_source_packet_parse_qa.csv`
- `reports/reference_trend_520_batch13_jmu_source_packet_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch13_jmu_source_packet_parse.md`

覆盖结果：已缓存集美大学招生计划入口 3 页和 2025 广西招生计划明细页。官方明细页直接打印“专业组”列；本科批 + 物理类共 39 行，计划数合计 160，覆盖源内专业组 04/05/06/07/08/09/10/11。提前批航海类、历史类和合计行已写入 exclusion，不混入物理普通批预览。

准入边界：本轮只做 source-packet parse preview。虽然源页打印专业组代码，但本轮没有同步广西考试院投档分/位次线，也没有做 group-line score/rank mapping，因此 `reference_trend_pool_eligible=false_until_score_rank_or_exam_authority_group_line_match`、`calibration_eligible=false_no_score_rank`、`canonical_ml_entry_open=false`；不进入 32 所 decision_pool。下一轮可继续做 JMU group-line score/rank 匹配预览，或推进青海大学/安徽工业大学图片 OCR 审批准备。


## 53. 2026-05-16 batch13 集美大学 group-line mapping workbench

已新增集美大学 group-line mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_group_line_mapping_workbench.csv`
- `reports/reference_trend_520_batch13_jmu_group_line_mapping_rollup.csv`
- `reports/reference_trend_520_batch13_jmu_group_line_mapping_qa.csv`
- `reports/reference_trend_520_batch13_jmu_group_line_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch13_jmu_group_line_mapping.md`

覆盖结果：基于集美大学官方广西计划 source packet 中打印的专业组 04/05/06/07/08/09/10/11，和既有 520 队列中的 2024/2025 位次上下文做本地候选映射。7 个专业组可形成 candidate group-line match preview，合计计划数 155；专业组 11 合计计划数 5，因当前 520 队列没有对应分数/位次上下文，继续 hold。

准入边界：本轮只是映射工作台，不是正式 trend pool intake。所有行 `reference_trend_pool_eligible=false_preview_only`、`calibration_eligible=false_pending_human_acceptance_and_score_rank_source_confirmation`、`canonical_ml_entry_open=false`；不进入 32 所 decision_pool。下一轮可对 candidate matched groups 做人工接受表，或继续推进青海大学/安徽工业大学图片 OCR/人工转录审批准备。


## 54. 2026-05-16 batch13 集美大学 group mapping acceptance sheet

已新增集美大学 group mapping acceptance decision sheet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.csv`
- `reports/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet_rollup.csv`
- `reports/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet_qa.csv`
- `reports/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet_exclusion_log.csv`
- `docs/reference_trend_520_batch13_jmu_group_mapping_acceptance_decision_sheet.md`

覆盖结果：从 group-line mapping workbench 中抽取 7 个 candidate matched group，生成待人工接受/hold/request_fix/reject 的决策表，覆盖计划数 155。专业组 11 继续在 exclusion/hold 层，不进入本决策表。

准入边界：本轮只生成空白人工决策表；未自动接受任何映射，未写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。脚本后续重跑会保护已经填写的人工决策字段。


## 55. 2026-05-16 P1 官方来源发现 batch 14

已新增 batch14 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch14_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch14_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch14_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch14_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch14.md`

覆盖结果：queue rank 131-150。苏州科技大学、西华大学、上海政法学院、上海海洋大学、天津外国语大学形成 T2 官方入口/计划列表候选，需后续缓存详情页确认是否有广西物理普通批行；集美大学和安徽工业大学作为既有候选承接，分别等待人工映射接受与图片 OCR/人工转录审批；其余学校本轮主要是官方门户/上下文，未形成可入 source-packet 的结构化计划行。

准入边界：本轮只做 source discovery preview，不缓存、不解析、不 OCR，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮优先缓存/解析上海政法学院、上海海洋大学、天津外国语大学或苏州科技大学的 2025 广西计划详情；安徽工业大学图片路线仍需人工批准。


## 56. 2026-05-16 batch14 asset/PDF readiness

已新增 batch14 asset/PDF readiness：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_asset_pdf_readiness_preview.csv`
- `reports/reference_trend_520_batch14_asset_pdf_readiness_rollup.csv`
- `reports/reference_trend_520_batch14_asset_pdf_readiness_qa.csv`
- `reports/reference_trend_520_batch14_asset_pdf_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch14_asset_pdf_readiness.md`

覆盖结果：上海政法学院官方详情页已缓存，并从页面嵌入 base64 PNG 中提取本地计划图片资产 2 个；上海海洋大学官方详情页已缓存，并根据页面 `pdfsrc` 成功缓存 2025 分省招生计划 PDF。一个旧搜索面暴露的上海海洋 PDF URL 返回 404，已写入 exclusion。

准入边界：本轮只做资产/PDF 解析前置，不做 OCR、PDF 表格解析或人工转录，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮如果没有人工批准 OCR/PDF 解析，应继续缓存/解析 batch14 中其他可直接 HTML 化的官方计划详情。


## 57. 2026-05-16 batch14 HTML cache backoff

已新增 batch14 HTML cache backoff：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_html_cache_backoff_preview.csv`
- `reports/reference_trend_520_batch14_html_cache_backoff_rollup.csv`
- `reports/reference_trend_520_batch14_html_cache_backoff_qa.csv`
- `reports/reference_trend_520_batch14_html_cache_backoff_exclusion_log.csv`
- `docs/reference_trend_520_batch14_html_cache_backoff.md`

覆盖结果：苏州科技大学官方“招生计划/历年招生计划”栏目已缓存，但静态页未暴露 2025 广西物理普通批计划行；天津外国语大学官方首页和招生计划栏目已缓存，栏目目前只列 2024 及更早计划，未暴露 2025 广西计划详情。这两条已写入 backoff，避免自动化重复抓同一入口。

准入边界：本轮只做 HTML 缓存回退记录，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮可继续寻找西华大学或其他 batch14 学校的可直接 HTML 化官方计划详情，或等待人工批准 OCR/PDF/图片解析路线。


## 58. 2026-05-16 batch14 西华大学 web reachability backoff

已新增西华大学 batch14 web reachability/backoff：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_xhu_web_reachability_backoff_preview.csv`
- `reports/reference_trend_520_batch14_xhu_web_reachability_backoff_rollup.csv`
- `reports/reference_trend_520_batch14_xhu_web_reachability_backoff_qa.csv`
- `reports/reference_trend_520_batch14_xhu_web_reachability_backoff_exclusion_log.csv`
- `docs/reference_trend_520_batch14_xhu_web_reachability_backoff.md`

覆盖结果：官方 2025 本科招生章程和 2024 本科招生计划公告可通过网页索引确认；2025 章程只给招生计划政策边界，未发布广西物理普通批院校专业组计划行；2024 公告只保留历史/聚合计划语境。终端缓存西华大学官方入口和文章时出现 412/SSL/empty reply，已记录为 backoff，避免自动化反复硬抓。

准入边界：本轮只做 source reachability/backoff，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮应转向新的 P0/P1 候选，或在用户批准后对 SHUPL/SHOU/AHUT/XHU 执行 OCR、PDF 表格解析、浏览器态或 header/cookie 路线。


## 59. 2026-05-16 batch14 manual approval queue

已新增 batch14 manual approval queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch14_manual_approval_queue.csv`
- `reports/reference_trend_520_batch14_manual_approval_queue_rollup.csv`
- `reports/reference_trend_520_batch14_manual_approval_queue_qa.csv`
- `reports/reference_trend_520_batch14_manual_approval_queue_exclusion_log.csv`
- `docs/reference_trend_520_batch14_manual_approval_queue.md`

覆盖结果：合并集美大学 group mapping 人工接受、上海政法学院 PNG OCR/人工转录、上海海洋大学 PDF 表格解析/人工转录、安徽工业大学图片 OCR/人工转录、西华大学浏览器/header/exact URL 路线，以及苏州科技大学/天津外国语大学 exact detail 或动态浏览器路线。队列只做批准决策入口，不替代原始人工表。

准入边界：本轮没有批准任何路线，也没有写 reference_trend_pool/canonical/ML；所有行在批准前均为不可入池。下一轮若仍无人工批准，应继续开新的 P0/P1 官方来源候选；若发现本队列有 selected_decision，则先做 post-approval intake/QA。


## 60. 2026-05-16 P1 官方来源发现 batch 15

已新增 batch15 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch15_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch15_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch15_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch15_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch15.md`

覆盖结果：queue rank 151-170。中南林业科技大学形成 exact 广西计划页候选；青海大学、沈阳工业大学、浙江科技大学、湖北大学、长江大学、太原理工大学等形成 2025 计划页/PDF/计划栏目候选；武汉科技大学、江汉大学、浙江中医药大学、绍兴文理学院、贵州中医药大学、长春理工大学、上海师范大学、丽水学院等暂为官方入口/章程/上下文，需后续 exact detail cache。

准入边界：本轮只做 source discovery preview，不缓存、不解析、不 OCR，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一轮优先缓存/解析中南林业科技大学 exact 广西计划页，或处理青海大学/长江大学/湖北大学等官方计划页/PDF候选。


## 61. 2026-05-16 batch15 existing artifact reconciliation

已新增 batch15 existing artifact reconciliation：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_existing_artifact_reconciliation.csv`
- `reports/reference_trend_520_batch15_existing_artifact_reconciliation_rollup.csv`
- `reports/reference_trend_520_batch15_existing_artifact_reconciliation_qa.csv`
- `reports/reference_trend_520_batch15_existing_artifact_reconciliation_exclusion_log.csv`
- `docs/reference_trend_520_batch15_existing_artifact_reconciliation.md`

覆盖结果：batch15 中南林业科技大学 168/169 两条队列被去重并承接到 batch8 既有产物：source packet parse 已有 41 个专业行、计划合计 150，group mapping workbench 已覆盖 2025 广西物理类 104/106/108 三个考试院专业组上下文。

准入边界：不再重复抓取中南林业科技大学 exact 广西计划页；官方计划源仍不打印广西院校专业组代码，因此 168/169 继续等待人工 group mapping 或官方 group split 证据。未写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。


## 62. 2026-05-16 batch15 青海大学 plan readiness/backoff

已新增青海大学 batch15 plan readiness/backoff：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_qhu_plan_readiness_preview.csv`
- `reports/reference_trend_520_batch15_qhu_plan_readiness_rollup.csv`
- `reports/reference_trend_520_batch15_qhu_plan_readiness_qa.csv`
- `reports/reference_trend_520_batch15_qhu_plan_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch15_qhu_plan_readiness.md`

覆盖结果：青海大学第一方官方 2025 招生计划页已缓存，页面正文只暴露外部 Eqxiu 海报入口；静态 HTML 没有可直接入库的广西物理类本科普通批院校专业组计划行、最低分、最低位次或专业组代码。

准入边界：本轮只做 source-chain/readiness/backoff，不做浏览器渲染、OCR 或人工转录；不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步若用户批准，可对 Eqxiu 海报执行浏览器态截图/OCR/人工转录，并单独生成 preview/QA。


## 63. 2026-05-16 batch15 湖北大学 PDF parse preview

已新增湖北大学 batch15 PDF parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_hubu_pdf_parse_preview.csv`
- `reports/reference_trend_520_batch15_hubu_pdf_parse_rollup.csv`
- `reports/reference_trend_520_batch15_hubu_pdf_parse_qa.csv`
- `reports/reference_trend_520_batch15_hubu_pdf_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_hubu_pdf_parse_preview.md`

覆盖结果：官方 2025 分省分专业招生计划 PDF 已缓存并用 pypdf 抽取文本；广西列解析出 46 个专业行，专业行计划数合计 152，与 PDF 总计行广西列 152 一致。该 PDF 提供省份-专业计划数，但不打印广西院校专业组代码。

准入边界：本轮只写 source-packet preview/QA；所有行继续 `reference_trend_pool_eligible=false_until_group_code_and_subject_mapping`，不写 canonical/ML，也不进入 32 所 decision_pool。下一步可做人审/GPT group mapping，把计划行映射到 2025 广西湖北大学 104/105/106/107/108 专业组，或因缺官方 group split 继续 hold。


## 64. 2026-05-16 batch15 长江大学 aggregate PDF backoff

已新增长江大学 batch15 aggregate PDF backoff：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_preview.csv`
- `reports/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_rollup.csv`
- `reports/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_qa.csv`
- `reports/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff_exclusion_log.csv`
- `docs/reference_trend_520_batch15_yangtzeu_pdf_aggregate_backoff.md`

覆盖结果：官方 2025“分批次、分科类招生计划”PDF 已缓存并用 pypdf 抽取文本；该 PDF 只有全校汇总口径，例如普本物理组 6113、总计 9781，不含广西、专业行、院校专业组、最低分或最低位次。

准入边界：本轮只写 aggregate context/backoff；不写 source-packet intake、reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步应继续寻找长江大学官方广西分省/分专业/专业组计划源，不能从该汇总 PDF 推断广西计划。


## 65. 2026-05-16 batch15 沈阳工业大学 image asset readiness

已新增沈阳工业大学 batch15 image asset readiness：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_sut_image_asset_readiness_preview.csv`
- `reports/reference_trend_520_batch15_sut_image_asset_readiness_rollup.csv`
- `reports/reference_trend_520_batch15_sut_image_asset_readiness_qa.csv`
- `reports/reference_trend_520_batch15_sut_image_asset_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch15_sut_image_asset_readiness.md`

覆盖结果：沈阳工业大学官方 exact 2025 本科招生计划页已缓存，页面包含 2 张官方计划图片资产，均已落地本地缓存。静态 HTML 不暴露广西/物理/专业组/计划数表格文本，因此本轮未做 OCR 或人工转录。

准入边界：本轮只做 image asset readiness，不写 source-packet intake、reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步若用户批准，可对两张图片做 OCR/人工转录，并单独生成 preview/QA。


## 66. 2026-05-16 batch15 浙江科技大学 XLS parse preview

已新增浙江科技大学 batch15 XLS parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_zust_xls_parse_preview.csv`
- `reports/reference_trend_520_batch15_zust_xls_parse_rollup.csv`
- `reports/reference_trend_520_batch15_zust_xls_parse_qa.csv`
- `reports/reference_trend_520_batch15_zust_xls_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_zust_xls_parse_preview.md`

覆盖结果：官方招生计划网页和其引用的 2025 全日制本科招生计划 XLS 已缓存。XLS 广西列解析出 25 个专业计划行，计划数合计 165；其中 19 行选考要求含物理，6 行为 `不限`，需后续结合广西投档线/专业组拆分确认物理/历史路线。

准入边界：本轮只写 source-packet preview/QA；附件没有广西院校专业组代码、最低分、最低位次，所有行继续 `reference_trend_pool_eligible=false_until_group_code_and_subject_route_mapping`，不写 canonical/ML，也不进入 32 所 decision_pool。下一步可查找浙江科技大学 2025 广西投档专业组线或官方专业组拆分，用于 group mapping；否则保持计划侧 evidence。


## 67. 2026-05-16 batch15 西北民族大学 AJAX reachability backoff

已新增西北民族大学 batch15 AJAX reachability/backoff：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_preview.csv`
- `reports/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_rollup.csv`
- `reports/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_qa.csv`
- `reports/reference_trend_520_batch15_xbmu_ajax_reachability_backoff_exclusion_log.csv`
- `docs/reference_trend_520_batch15_xbmu_ajax_reachability_backoff.md`

覆盖结果：官方计划查询 UI 已缓存，静态页含广西筛选项、`zsjhTotal`/`zsjhList` 模板和 `f/ajax_zsjh_param`/`f/ajax_zsjh` endpoint 形状。终端访问参数接口返回 `http_403`，正文为 `页面不存在`；首次正常 TLS 校验失败，说明站点证书过期，后续只作为 reachability evidence 处理。

准入边界：本轮未做浏览器态、cookie/header replay 或表单 replay；不生成 source-packet rows，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步需要用户批准浏览器/会话态检查，或另找官方静态 PDF/table export。


## 68. 2026-05-16 batch15 绍兴文理学院 image asset readiness

已新增绍兴文理学院 batch15 image asset readiness：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_usx_image_asset_readiness_preview.csv`
- `reports/reference_trend_520_batch15_usx_image_asset_readiness_rollup.csv`
- `reports/reference_trend_520_batch15_usx_image_asset_readiness_qa.csv`
- `reports/reference_trend_520_batch15_usx_image_asset_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch15_usx_image_asset_readiness.md`

覆盖结果：官方 exact 2025 广西壮族自治区招生计划页已缓存，正文计划表为 1 张 PNG 图片资产，已落地本地缓存，尺寸 1080x612。静态 HTML 不暴露广西/物理/专业组/计划数表格文本，因此本轮未做 OCR 或人工转录。

准入边界：本轮只做 image asset readiness，不写 source-packet intake、reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步若用户批准，可对图片做 OCR/人工转录，并单独生成 preview/QA。


## 69. 2026-05-16 batch15 上海师范大学 PDF parse preview

已新增上海师范大学 batch15 PDF parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_shnu_pdf_parse_preview.csv`
- `reports/reference_trend_520_batch15_shnu_pdf_parse_rollup.csv`
- `reports/reference_trend_520_batch15_shnu_pdf_parse_qa.csv`
- `reports/reference_trend_520_batch15_shnu_pdf_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_shnu_pdf_parse_preview.md`

覆盖结果：官方 2025 外省市招生计划页和 PDF 已缓存，PDF 经 pdfplumber 表格解析后抽出广西列 21 个专业行，计划数合计 154。其中 6 行带艺术/体育/中外合作等特殊边界标记。

准入边界：本轮只写 source-packet preview/QA；PDF 没有广西院校专业组代码、科类/选科路线、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=false_until_group_code_and_subject_route_mapping`，不写 canonical/ML，也不进入 32 所 decision_pool。


## 70. 2026-05-16 batch15 长春理工大学 HTML parse preview

已新增长春理工大学 batch15 HTML parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_cust_html_parse_preview.csv`
- `reports/reference_trend_520_batch15_cust_html_parse_rollup.csv`
- `reports/reference_trend_520_batch15_cust_html_parse_qa.csv`
- `reports/reference_trend_520_batch15_cust_html_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_cust_html_parse_preview.md`

覆盖结果：官方 2025 广西招生计划静态 HTML 表格已缓存并解析，抽出 28 个物理类专业计划行，计划数合计 127；其中 4 行带中外合作/特殊边界标记。

准入边界：本轮只写 source-packet preview/QA；官方页没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可用广西考试院投档线/专业组上下文做 group mapping workbench，或保持计划侧 evidence。


## 71. 2026-05-16 batch15 丽水学院 Guangxi-column parse preview

已新增丽水学院 batch15 Guangxi-column parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_lsu_html_province_column_parse_preview.csv`
- `reports/reference_trend_520_batch15_lsu_html_province_column_parse_rollup.csv`
- `reports/reference_trend_520_batch15_lsu_html_province_column_parse_qa.csv`
- `reports/reference_trend_520_batch15_lsu_html_province_column_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_lsu_html_province_column_parse_preview.md`

覆盖结果：官方 2025 分省分专业招生计划页已缓存并解析，抽出广西列 32 个专业计划行，计划数合计 150；与官方广西总计行 150 对齐。

准入边界：本轮只写 source-packet preview/QA；官方表格没有广西科类/选科路线、院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可寻找广西考试院 group-line 上下文或官方专业组拆分；否则保持计划侧 evidence。


## 72. 2026-05-16 batch15 武汉科技大学 group image asset readiness

已新增武汉科技大学 batch15 group image asset readiness：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_wust_group_image_asset_readiness_preview.csv`
- `reports/reference_trend_520_batch15_wust_group_image_asset_readiness_rollup.csv`
- `reports/reference_trend_520_batch15_wust_group_image_asset_readiness_qa.csv`
- `reports/reference_trend_520_batch15_wust_group_image_asset_readiness_exclusion_log.csv`
- `docs/reference_trend_520_batch15_wust_group_image_asset_readiness.md`

覆盖结果：官方 2025 院校专业组设置页已缓存，广西对应展示图和原图均已落地。该来源是 group mapping 的强候选，但目前仍为图片资产。

准入边界：本轮不做 OCR/人工转录，不提取文本行，不写 reference_trend_pool/canonical/ML，也不进入 32 所 decision_pool。下一步需要 OCR/人工转录批准，或另找官方文本/PDF 表格。


## 73. 2026-05-16 batch15 桂林电子科技大学北海校区 group-plan parse preview

已新增桂林电子科技大学北海校区 batch15 group-plan parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_guet_bh_html_group_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_guet_bh_html_group_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_guet_bh_html_group_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_guet_bh_html_group_plan_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_guet_bh_html_group_plan_parse_preview.md`

覆盖结果：官方 2025 广西本科招生计划页已缓存并解析，抽出广西全量 15 行；其中普通类物理/理工本科批 8 行，计划数按专业组汇总为 {'161': 200, '162': 852}。

准入边界：本轮只写 source-packet preview/QA；普通物理行已有官方专业组代码和计划数，但没有最低分/最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。


## 74. 2026-05-16 batch15 贵州中医药大学 PDF column parse preview

已新增贵州中医药大学 batch15 PDF column parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_gzy_pdf_column_parse_preview.csv`
- `reports/reference_trend_520_batch15_gzy_pdf_column_parse_rollup.csv`
- `reports/reference_trend_520_batch15_gzy_pdf_column_parse_qa.csv`
- `reports/reference_trend_520_batch15_gzy_pdf_column_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_gzy_pdf_column_parse_preview.md`

覆盖结果：官方 2025 本科分省分专业招生计划 PDF 已缓存并解析，抽出广西计划列 29 行，计划数合计 77；物理/理工全量 21 行，计划数合计 67，与 PDF 物理总计 67 对齐；剔除中外合作/体育等特殊边界后的普通物理候选 20 行，计划数合计 62。PDF 总计行校验为广西合计 77。

准入边界：本轮只写 source-packet preview/QA；官方 PDF 没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench，或继续寻找官方专业组拆分表。


## 75. 2026-05-16 batch15 江汉大学 API plan parse preview

已新增江汉大学 batch15 API plan parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_jhun_api_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_jhun_api_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_jhun_api_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_jhun_api_plan_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_jhun_api_plan_parse_preview.md`

覆盖结果：官方本科招生网指向官方招生数据系统，JS 暴露 `getType/getList` API；已缓存 2025 广西物理类普通类计划响应，抽出 16 行，计划数合计 169，与 API summary `jhrs=169` 对齐。接口返回专业、计划数、学制/学费、选科要求，但 `zygroup` 为空。

准入边界：本轮只写 source-packet preview/QA；官方 API 没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。


## 76. 2026-05-16 batch15 浙江中医药大学 API plan parse preview

已新增浙江中医药大学 batch15 API plan parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_zcmu_api_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_zcmu_api_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_zcmu_api_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_zcmu_api_plan_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_zcmu_api_plan_parse_preview.md`

覆盖结果：官方招生计划页嵌入官方招生查询系统，JS 暴露公开 `/yxy/yxyRecruit/noTokenList` API；已缓存 2024/2025 广西计划响应。2025 广西 26 行、计划数 129，其中本科普通批/普通类/物理类 23 行、计划数 124；2024 广西 33 行、计划数 129，其中本科普通批/普通类/物理类 27 行、计划数 108。

准入边界：本轮只写 source-packet preview/QA；官方 API 没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。


## 77. 2026-05-16 batch15 中南林业科技大学 exact Guangxi plan parse preview

已新增中南林业科技大学 batch15 exact Guangxi plan parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_csuft_html_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_csuft_html_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_csuft_html_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_csuft_html_plan_parse_exclusion_log.csv`
- `docs/reference_trend_520_batch15_csuft_html_plan_parse_preview.md`

覆盖结果：官方 2025 广西招生计划页两页已缓存并解析，抽出全量 50 行，计划数合计 173；其中本科普通批/物理类/无特殊边界候选 41 行，计划数合计 150。历史类与体育提前批行保留在审计/排除日志，不进入普通物理候选。

准入边界：本轮只写 source-packet preview/QA；官方页没有广西院校专业组代码、最低分或最低位次，所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一步可与广西考试院 group-line score/rank 做 join workbench。


## 78. 2026-05-16 P0 上海工程技术大学 official form reachability preview

已新增上海工程技术大学 P0 official form reachability preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_sues_form_reachability_preview.csv`
- `reports/reference_trend_520_p0_sues_form_reachability_rollup.csv`
- `reports/reference_trend_520_p0_sues_form_reachability_qa.csv`
- `reports/reference_trend_520_p0_sues_form_reachability_exclusion_log.csv`
- `docs/reference_trend_520_p0_sues_form_reachability_preview.md`

覆盖结果：官方招生系统首页已缓存，确认首页同时暴露招生计划 `getzslq.do` 与历年分数 `getzsfsx.do` 表单；2025 / 广西 / 本科 / 物理类 option 参数齐全。

准入边界：本轮没有执行 form replay/browser-state 检查，不获取结果行；所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。若用户批准，可下一轮用表单 POST 或浏览器态获取官方结果页并做 source-packet QA。


## 79. 2026-05-16 P0 东北农业大学 official reachability preview

- Cached official chain: `raw_sources/reference_trend/p0_official_drilldown/neau_zsbweb_index_https.html` -> `raw_sources/reference_trend/p0_official_drilldown/neau_zsb_home.html`.
- Output preview: `clean_data/engineering_guangxi_seed/reference_trend_520_p0_neau_reachability_preview.csv`.
- QA: `reports/reference_trend_520_p0_neau_reachability_qa.csv`; rollup: `reports/reference_trend_520_p0_neau_reachability_rollup.csv`; exclusion log: `reports/reference_trend_520_p0_neau_reachability_exclusion_log.csv`.
- Result: official undergraduate admissions homepage located, but direct terminal POST to `https://zsb.neau.edu.cn/f/newsCenter/ajax_get_category_and_link_list` returned 403. Kept both NEAU group queue rows as reachability evidence only.
- Boundary: no structured plan rows, no reference_trend_pool eligibility, no canonical/ML, no decision_pool merge. Further progress requires manual approval for audited header/cookie/browser-state check.


## 80. 2026-05-16 P0 东莞理工学院 official reachability preview

- Cached official portal: `raw_sources/reference_trend/p0_official_drilldown/dgut_zsb_plan_portal.html`.
- Cached school-subdomain announcement: `raw_sources/reference_trend/p0_official_drilldown/dgut_ee_2025_plan_announcement.html`.
- Output preview: `clean_data/engineering_guangxi_seed/reference_trend_520_p0_dgut_reachability_preview.csv`.
- QA: `reports/reference_trend_520_p0_dgut_reachability_qa.csv`; rollup: `reports/reference_trend_520_p0_dgut_reachability_rollup.csv`; exclusion log: `reports/reference_trend_520_p0_dgut_reachability_exclusion_log.csv`.
- Result: official admissions portal lists the 2025 undergraduate plan item, but the target is a WeChat article; school-subdomain announcement exposes a shortlink only. Kept queue row 0003 / group 101 as reachability evidence only.
- Boundary: no structured Guangxi plan rows, no reference_trend_pool eligibility, no canonical/ML, no decision_pool merge. Further progress requires manual approval for browser capture of official WeChat/shortlink or locating a first-party structured HTML/PDF/XLSX source.


## 81. 2026-05-16 P0 云南/南京中医药 PDF gap resolution preview

已新增 P0 PDF gap resolution preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_gap_resolution_preview.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_rollup.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_qa.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_exclusion_log.csv`
- `docs/reference_trend_520_p0_pdf_gap_resolution_preview.md`

覆盖结果：将云南中医药大学 2 条队列行、南京中医药大学 4 条队列行从 `source_packet_parse_exists_but_field_gaps_remain` 收束为可审计 backoff。云南中医药大学当前官方 PDF 候选为 404 hold；南京中医药大学当前官方 PDF 已解析但无广西行，拒绝进入广西 reference trend。

准入边界：本轮不联网、不做浏览器/header/form replay、不写 canonical/ML、不并入 32 所 decision_pool。所有 6 行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。下一步只需继续重定位这两所的官方广西物理普通批计划/分数来源。


## 82. 2026-05-16 batch3 宁波诺丁汉 PDF column alignment preview

已新增宁波诺丁汉大学 batch3 PDF column alignment preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_pdf_column_alignment_preview.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_qa.csv`
- `reports/reference_trend_520_batch3_unnc_pdf_column_alignment_exclusion_log.csv`
- `docs/reference_trend_520_batch3_unnc_pdf_column_alignment_preview.md`

覆盖结果：从官方 PDF 缓存文本中抽出 17 条理/物行，按 PDF 省份序列第 10 列对齐广西，广西物理计划数暂计 20，与 PDF 顶部广西理/物合计 20 对齐。

准入边界：PDF 文本抽取仍有若干专业标签需要人工复核，且没有广西院校专业组代码；所有行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不并入 32 所 decision_pool。下一步可基于该预览生成宁波诺丁汉 group 303 的人工标签/组映射工作表。


## 83. 2026-05-16 batch3 宁波诺丁汉 label/group mapping workbench

已新增宁波诺丁汉大学 label/group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_unnc_label_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_qa.csv`
- `reports/reference_trend_520_batch3_unnc_label_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch3_unnc_label_group_mapping_workbench.md`

覆盖结果：将 17 条 PDF column alignment 行转成可人工确认的标签/专业组映射工作表，其中 8 行广西物理计划数大于 0，计划数合计 20。工作表包含 `selected_decision/reviewer/decision_notes`，后续脚本检测到人工填写会拒绝覆盖。

准入边界：这仍是人工映射工作表，不是 source-packet intake；所有行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不并入 32 所 decision_pool。下一步需要人工接受、修正或驳回标签与 group 303 映射。

## 84. 2026-05-16 batch3 广西师范大学 group mapping workbench

已新增广西师范大学 group mapping workbench：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_group_mapping_workbench.csv`
- `reports/reference_trend_520_batch3_gxnu_group_mapping_rollup.csv`
- `reports/reference_trend_520_batch3_gxnu_group_mapping_qa.csv`
- `reports/reference_trend_520_batch3_gxnu_group_mapping_exclusion_log.csv`
- `docs/reference_trend_520_batch3_gxnu_group_mapping_workbench.md`

覆盖结果：将 53 条广西师范大学 2025 广西物理类本科普通批普通类官方计划解析行转成可人工确认的专业组映射工作表，计划数合计 2002。候选考试院专业组为 151 / 152 / 155 / 156，脚本不自动归组。

准入边界：这仍是人工映射工作表，不是 source-packet intake；所有行继续 `eligible_for_intake_preview=false`、`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不并入 32 所 decision_pool。下一步需要人工按专业/组结构分配专业组或继续 hold。

## 85. 2026-05-16 group mapping action board

已新增 group mapping action board：

- `clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_action_board.csv`
- `reports/reference_trend_520_group_mapping_action_board_rollup.csv`
- `reports/reference_trend_520_group_mapping_action_board_qa.csv`
- `reports/reference_trend_520_group_mapping_action_board_exclusion_log.csv`
- `docs/reference_trend_520_group_mapping_action_board.md`

覆盖结果：聚合 15 个既有 group mapping workbench，覆盖 428 行待映射/待边界复核记录，形成后续人工接受、组映射、post-human intake 的行动面板。

准入边界：本轮只生成派生 action board，不改任何源工作表；`reference_trend_pool_eligible`、canonical/ML、32 所 decision_pool 均不打开。

## 86. 2026-05-16 广西师范大学 mapping review packet

已新增广西师范大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch3_gxnu_mapping_review_packet.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_discipline_rollup.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_batch3_gxnu_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_batch3_gxnu_mapping_review_packet.md`

覆盖结果：将广西师范大学 53 行专业组映射工作表整理为人工审核包，并按专业代码前两位聚合为 7 个学科簇，计划数校验仍为 2002。

准入边界：该包只辅助人工分配 151 / 152 / 155 / 156，不自动归组；`reference_trend_pool_eligible`、canonical/ML、32 所 decision_pool 均不打开。

## 87. 2026-05-16 KMUST/UJS mapping ambiguity packet

已新增昆明理工大学 / 江苏大学 mapping ambiguity packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_status_rollup.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_rollup.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_qa.csv`
- `reports/reference_trend_520_kmust_ujs_mapping_ambiguity_packet_exclusion_log.csv`
- `docs/reference_trend_520_kmust_ujs_mapping_ambiguity_packet.md`

覆盖结果：从既有 mapping QA workbench 派生 86 行 ambiguity packet。江苏大学有 16 行单一普通物理组分数参考但缺 rank；昆明理工大学有 6 行 exact floor candidate 与 46 行多组阈值候选，均需官方组结构或人工边界判断。

准入边界：本轮只做歧义分层和行动提示，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 88. 2026-05-16 CUGB mapping review packet

已新增中国地质大学(北京) mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_cugb_mapping_review_packet.csv`
- `reports/reference_trend_520_cugb_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_cugb_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_cugb_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_cugb_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_cugb_mapping_review_packet.md`

覆盖结果：从既有 CUGB group mapping workbench 派生 53 行审核包，其中 score-major 9 行、plan-major 44 行；单组候选 2 行、多组歧义 16 行、未匹配计划行 35 行，另有 3 行存在特殊组 floor 碰撞上下文。

准入边界：本轮只做阈值候选和特殊组碰撞分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 89. 2026-05-16 LZJTU mapping review packet

已新增兰州交通大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_lzjtu_mapping_review_packet.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_lzjtu_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_lzjtu_mapping_review_packet.md`

覆盖结果：从既有 LZJTU group mapping workbench 派生 52 行审核包，其中 score-major 26 行、plan-major 26 行；单组候选 12 行、多组歧义 40 行，计划行合计 64。

准入边界：本轮只做 101/102 组候选分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 90. 2026-05-16 NANHANG mapping review packet

已新增南京航空航天大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_nanhang_mapping_review_packet.csv`
- `reports/reference_trend_520_nanhang_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_nanhang_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_nanhang_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_nanhang_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_nanhang_mapping_review_packet.md`

覆盖结果：从既有 NANHANG group boundary workbench 派生 44 行审核包，其中 2024 专业分 rows 19 行、2025 计划 rows 21 行、2024 overview boundary rows 4 行；单组候选 38 行，未映射/边界证据 6 行，计划行合计 75。

准入边界：本轮只做 101/303 组边界与 rank 缺失分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 91. 2026-05-16 SCUEC mapping review packet

已新增中南民族大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_scuec_mapping_review_packet.csv`
- `reports/reference_trend_520_scuec_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_scuec_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_scuec_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_scuec_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_scuec_mapping_review_packet.md`

覆盖结果：从既有 SCUEC group mapping workbench 派生 35 行审核包，其中 2025 官方计划未归组 rows 32 行、2024 分数组精确证据 rows 3 行；计划行合计 492，分组证据覆盖 103|104|105。

准入边界：本轮只做 103/104/105 组证据和 2025 计划待归组分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 92. 2026-05-16 HRBMU mapping review packet

已新增哈尔滨医科大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_hrbmu_mapping_review_packet.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_hrbmu_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_hrbmu_mapping_review_packet.md`

覆盖结果：从既有 HRBMU group mapping workbench 派生 22 行审核包，其中 2025 物理普通计划缺组码 rows 19 行、计划数 32；国家专项隔离 1 行/计划数 13；非物理旧文科隔离 2 行/计划数 5。物理普通候选组为 151|152|153|154|156|157|158|159。

准入边界：本轮只做物理普通待归组、专项隔离和非物理隔离分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 93. 2026-05-16 UNNC mapping review packet

已新增宁波诺丁汉大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_unnc_mapping_review_packet.csv`
- `reports/reference_trend_520_unnc_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_unnc_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_unnc_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_unnc_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_unnc_mapping_review_packet.md`

覆盖结果：从既有 UNNC label/group mapping workbench 派生 17 行审核包，其中可人工接受的正计划 rows 8 行，zero-plan/label-review hold rows 9 行；广西物理计划 checksum 仍为 20。

准入边界：本轮只做 PDF 标签清洗与 303 组人工接受分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 94. 2026-05-16 GXUST mapping review packet

已新增广西科技大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_gxust_mapping_review_packet.csv`
- `reports/reference_trend_520_gxust_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_gxust_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_gxust_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_gxust_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_gxust_mapping_review_packet.md`

覆盖结果：从既有 GXUST group-line workbench 派生 17 行审核包，其中官方专业组结构已接上 2025 考试院线但缺计划数 rows 8 行；520 窗口内普通物理线索 3 行；考试院线缺官方组结构 hold 5 行；边界/特殊隔离 4 行。

准入边界：本轮只做组线证据、缺计划数和边界隔离分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 95. 2026-05-16 Batch7 SHZU/FJUT mapping review packet

已新增 batch7 石河子大学/福建理工大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch7_mapping_review_packet.csv`
- `reports/reference_trend_520_batch7_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_batch7_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_batch7_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_batch7_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_batch7_mapping_review_packet.md`

覆盖结果：从既有 batch7 group mapping workbench 派生 13 行审核包，覆盖石河子大学与福建理工大学；历史考试院趋势 context 5 行；官方计划数可用但广西专业组映射缺失 hold 5 行；学校级计划总数 summary 2 行；特殊/预科类隔离 1 行。2025 官方计划总数：石河子大学 100，福建理工大学 205。

准入边界：本轮只做官方计划总数、考试院组线趋势和人工组映射待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 96. 2026-05-16 NCUT mapping review packet

已新增北方工业大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_ncut_mapping_review_packet.csv`
- `reports/reference_trend_520_ncut_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_ncut_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_ncut_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_ncut_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_ncut_mapping_review_packet.md`

覆盖结果：从既有 NCUT batch9 group mapping workbench 派生 8 行审核包；历史考试院趋势 context 3 行；官方广西列计划数可用但专业组/选科映射缺失 hold 3 行；学校级计划总数 summary 1 行；特殊/混合组隔离 1 行。2025 官方广西列计划总数 57，其中普通未标记 48，特殊拆分 art_design_boundary:4;sino_foreign_cooperation:5。

准入边界：本轮只做官方计划总数、考试院组线趋势和 group/subject 人工映射待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 97. 2026-05-16 CSUFT mapping review packet

已新增中南林业科技大学 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_csuft_mapping_review_packet.csv`
- `reports/reference_trend_520_csuft_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_csuft_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_csuft_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_csuft_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_csuft_mapping_review_packet.md`

覆盖结果：从既有 CSUFT batch8 group mapping workbench 派生 7 行审核包；历史考试院趋势 context 3 行；官方计划数和选科拆分可用但广西专业组映射缺失 hold 3 行；学校级计划总数 summary 1 行。2025 官方计划总数 150，官方专业 rows 41，选科拆分：不提科目要求:5;物理(1门科目考生必须选考方可报考):19;物理,化学(2门科目考生均须选考方可报考):123;生物(1门科目考生必须选考方可报考):3。

准入边界：本轮只做官方计划总数、选科拆分、考试院组线趋势和人工组映射待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 98. 2026-05-16 ZUCC mapping review packet

已新增浙大城市学院 mapping review packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_zucc_mapping_review_packet.csv`
- `reports/reference_trend_520_zucc_mapping_review_status_rollup.csv`
- `reports/reference_trend_520_zucc_mapping_review_packet_rollup.csv`
- `reports/reference_trend_520_zucc_mapping_review_packet_qa.csv`
- `reports/reference_trend_520_zucc_mapping_review_packet_exclusion_log.csv`
- `docs/reference_trend_520_zucc_mapping_review_packet.md`

覆盖结果：从既有 ZUCC group mapping workbench 派生 5 行审核包；2025 考试院物理组 2 个；官方图片计划显示广西物理 80、广西历史 10、专业 rows 17。本包明确保留“不能把 80 个物理计划整包分配给单一 101/102 组”的 hold 规则。

准入边界：本轮只做官方图片计划总数、考试院组线趋势和组级拆分待判定分层，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。

## 99. 2026-05-16 Group mapping review closeout

已新增 reference trend group mapping review closeout：

- `clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_review_closeout_board.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_group_mapping_manual_pending_queue.csv`
- `reports/reference_trend_520_group_mapping_review_closeout_rollup.csv`
- `reports/reference_trend_520_group_mapping_review_closeout_qa.csv`
- `reports/reference_trend_520_group_mapping_review_closeout_exclusion_log.csv`
- `docs/reference_trend_520_group_mapping_review_closeout.md`

覆盖结果：15 个 action-board 项均已对上派生产物；现有 review/decision/intake preview artifact rows 合计 424 行；待人工决策或 batch acceptance rows 424 行；已检测到人工填写 rows 0 行。缺失 artifact rows 0。

准入边界：本轮只做总 closeout 和人工待判定队列，不提升任何行进入 reference trend intake；canonical/ML、32 所 decision_pool 均不打开。



## 100. 2026-05-16 P0 source discovery next actions

已新增 P0 source discovery next-actions / manual approval queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_source_discovery_next_actions.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_source_discovery_manual_approval_queue.csv`
- `reports/reference_trend_520_p0_source_discovery_next_actions_rollup.csv`
- `reports/reference_trend_520_p0_source_discovery_next_actions_qa.csv`
- `reports/reference_trend_520_p0_source_discovery_next_actions_exclusion_log.csv`
- `docs/reference_trend_520_p0_source_discovery_next_actions.md`

覆盖结果：P0 rows 117 行全部完成路由；manual/live approval rows 71 行。blocked_existing_candidate_needs_approval_or_exact_url=17；existing_candidate_parse_or_endpoint_drilldown=43；group_mapping_human_acceptance_hold=16；live_official_source_discovery_approval=36；parse_gap_review_before_new_search=3；plan_count_available_group_mapping_hold=2。

准入边界：本轮只做 P0 来源发现路由和人工/浏览器/联网批准队列，不执行联网抓取，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。


## 101. 2026-05-16 P0 local candidate drilldown queue

已新增 P0 local candidate drilldown queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_local_candidate_drilldown_queue.csv`
- `reports/reference_trend_520_p0_local_candidate_drilldown_queue_rollup.csv`
- `reports/reference_trend_520_p0_local_candidate_drilldown_queue_qa.csv`
- `reports/reference_trend_520_p0_local_candidate_drilldown_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_local_candidate_drilldown_queue.md`

覆盖结果：从 P0 existing-candidate lane 派生 60 条 candidate-level drilldown rows；context_or_no_rows_hold=25；endpoint_or_portal_drilldown=10；image_or_asset_ocr_candidate=15；metadata_drilldown_needed=2；no_local_candidate_found_in_prior_batch=7；reject_third_party_only_candidate=1。

准入边界：本轮只做已有候选的本地解析/拒绝/审批路线分流，不执行联网抓取，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。


## 102. 2026-05-16 P0 local cache inventory

已新增 P0 local cache inventory：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_local_cache_inventory.csv`
- `reports/reference_trend_520_p0_local_cache_inventory_rollup.csv`
- `reports/reference_trend_520_p0_local_cache_inventory_qa.csv`
- `reports/reference_trend_520_p0_local_cache_inventory_exclusion_log.csv`
- `docs/reference_trend_520_p0_local_cache_inventory.md`

覆盖结果：从 60 条 P0 local drilldown rows 派生 67 条 cache inventory rows；本地缓存存在 27 条，缺失/无缓存 40 条。cached_asset_or_page_ocr_preflight=4；cached_context_contains_guangxi_plan_terms_review=3；cached_context_no_structured_plan_hold=19；cached_endpoint_or_portal_page_review=1；metadata_only_no_cache_path=40。

准入边界：本轮只做本地缓存路径存在性和轻量文本关键词盘点，不执行联网抓取，不生成 source_packet parse rows，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。


## 103. 2026-05-16 P0 cached asset/endpoint preflight

已新增 P0 cached asset/endpoint preflight：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_asset_endpoint_preflight.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_rollup.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_qa.csv`
- `reports/reference_trend_520_p0_cached_asset_endpoint_preflight_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_asset_endpoint_preflight.md`

覆盖结果：从 P0 local cache inventory 中抽取 8 条本地已缓存且可继续预检的 asset/endpoint/context rows；本轮只做本地文件链接、表单、脚本、关键词和短证据预检。路线分布：cached_context_keyword_only_hold=3; cached_endpoint_form_or_script_links_found=1; cached_html_asset_links_found=3; local_pdf_parse_needed=1。QA PASS。

准入边界：本轮不联网、不浏览器 replay、不 OCR/PDF parse、不生成 source_packet parse rows；所有行仍停留在 preflight/QA 层，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。


## 104. 2026-05-16 P0 cached parse action queue

已新增 P0 cached parse action queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_parse_action_queue.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_parse_action_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_parse_action_queue.md`

覆盖结果：从 8 条 cached asset/endpoint preflight rows 派生 20 条本地下一步 action rows；路线分布：asset_link_needs_cached_capture_or_approval=11; decorative_or_site_asset_low_priority=4; endpoint_metadata_review_before_live_replay=1; keyword_context_hold_no_structured_plan_rows=3; local_pdf_text_extract_preview_queue=1。QA PASS。

准入边界：本轮只生成本地解析/审批/hold 队列，不执行 PDF parse/OCR、不联网、不浏览器 replay、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 105. 2026-05-16 P0 PDF text extract preview

已新增 P0 PDF text extract preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview.csv`
- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_text_extract_preview_text/`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_rollup.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_qa.csv`
- `reports/reference_trend_520_p0_pdf_text_extract_preview_exclusion_log.csv`
- `docs/reference_trend_520_p0_pdf_text_extract_preview.md`

覆盖结果：处理 1 条本地 PDF action row，使用 pypdf 离线抽取文本；生成 1 条 preview rows，总文本字符 2031。QA PASS。该 PDF 可读，但仍缺“广西物理/专业组”可验证映射，保留为 layout-unverified text preview。

准入边界：本轮只做本地 PDF 文本可读性和证据预览，不做 OCR、不联网、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 106. 2026-05-16 P0 PDF manual table QA queue

已新增 P0 PDF manual table QA queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_manual_table_qa_queue.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_rollup.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_qa.csv`
- `reports/reference_trend_520_p0_pdf_manual_table_qa_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_pdf_manual_table_qa_queue.md`

覆盖结果：从宁夏医科大学 PDF text preview 派生 31 条人工表格 QA rows；行类型：major_candidate_line=29; summary_or_total_line=2。QA PASS。所有行均标注 `manual_required_pdf_text_collapsed_columns`，不自动映射广西列。

准入边界：本轮只做人工 QA 队列，不生成 source_packet parse rows，不写入 reference trend intake，不打开 canonical/ML，也不并入 32 所 decision_pool。


## 107. 2026-05-17 P0 endpoint/form metadata audit

已新增 P0 endpoint/form metadata audit：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_endpoint_form_metadata_audit.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_rollup.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_qa.csv`
- `reports/reference_trend_520_p0_endpoint_form_metadata_audit_exclusion_log.csv`
- `docs/reference_trend_520_p0_endpoint_form_metadata_audit.md`

覆盖结果：处理滨州医学院 1 条 endpoint action row，基于本地缓存 HTML 提取 form/iframe/script endpoint metadata；状态分布：commonquery_iframe_shape_found_replay_approval_required=1; site_search_endpoint_not_plan_data=1; supporting_script_or_unknown_endpoint_shape=7。QA PASS。已确认 commonquery iframe 是更可能的招生计划查询 surface，站内搜索 form 仅作搜索端点，不可当作计划数据。

准入边界：本轮只做本地 endpoint/form 元数据审计，不执行 live replay、不联网、不浏览器操作、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 108. 2026-05-17 P0 cached branch human approval queue

已新增 P0 cached branch human approval queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_queue.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_queue_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_branch_human_approval_queue.md`

覆盖结果：合并本地 cached 分支的人工作业入口，共 9 条 approval/manual QA rows；lane 分布：browser_form_replay_approval=1; cached_asset_capture_or_manual_upload=7; manual_pdf_table_layout_qa=1。QA PASS。其中 asset candidate raw rows 已去重折叠，PDF manual table rows 折叠为 PDF-level QA 项。

准入边界：本轮只生成人工授权/人工 QA 队列，不执行联网、浏览器/form replay、资产捕获、OCR、source_packet parse 或 reference trend intake；canonical/ML、32 所 decision_pool 均继续关闭。


## 109. 2026-05-17 P0 cached branch human approval decision sheet

已新增 P0 cached branch human approval decision sheet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_human_approval_decision_sheet.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_human_approval_decision_sheet_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_branch_human_approval_decision_sheet.md`

覆盖结果：为 108 approval queue 生成 9 条可填写人工决策 rows；lane 分布：browser_form_replay_approval=1; cached_asset_capture_or_manual_upload=7; manual_pdf_table_layout_qa=1；当前 selected_decision 分布：__blank__=9。QA PASS。若后续人工填写 selected_decision/reviewer/decision_notes，脚本重跑会保留已填字段。

准入边界：本轮只生成可填写人工决策表，不执行联网、浏览器/form replay、资产捕获、OCR、source_packet parse 或 reference trend intake；canonical/ML、32 所 decision_pool 均继续关闭。


## 110. 2026-05-17 P0 cached branch post-decision status preview

已新增 P0 cached branch post-decision status preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_cached_branch_post_decision_status_preview.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_rollup.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_qa.csv`
- `reports/reference_trend_520_p0_cached_branch_post_decision_status_preview_exclusion_log.csv`
- `docs/reference_trend_520_p0_cached_branch_post_decision_status_preview.md`

覆盖结果：读取 109 决策表并生成 9 条 post-decision status rows；当前 selected_decision 分布：__blank__=9；status route 分布：waiting_human_decision=9。QA PASS。当前没有可执行授权行。

准入边界：本轮只做决策状态预览，不执行联网、浏览器/form replay、资产捕获、OCR、source_packet parse 或 reference trend intake；canonical/ML、32 所 decision_pool 均继续关闭。


## 111. 2026-05-17 P1 official source discovery batch16

已新增 P1 official source discovery batch16：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_official_source_discovery_batch16_preview.csv`
- `reports/reference_trend_520_p1_official_source_discovery_batch16_rollup.csv`
- `reports/reference_trend_520_p1_official_source_discovery_batch16_qa.csv`
- `reports/reference_trend_520_p1_official_source_discovery_batch16_exclusion_log.csv`
- `docs/reference_trend_520_p1_official_source_discovery_batch16.md`

覆盖结果：处理 P1 queue ranks 171-190，压缩为 17 条官方来源候选/官方上下文 rows；其中 T1 精确官方计划/查询候选 3 条，T2 官方计划候选 7 条，T3 官方上下文-only 7 条。QA PASS。

准入边界：本轮只做 source discovery preview，不缓存、不解析、不 OCR、不表单 replay、不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 112. 2026-05-17 P1 batch16 action queue

已新增 P1 batch16 action queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_action_queue.csv`
- `reports/reference_trend_520_p1_batch16_action_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch16_action_queue_qa.csv`
- `reports/reference_trend_520_p1_batch16_action_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch16_action_queue.md`

覆盖结果：从 marker 111 的 17 条 source-discovery preview rows 派生 17 条下一步 action rows；按 exact page/query/PDF/portal/context/special boundary 分流。QA PASS。

准入边界：本轮只生成行动队列，不联网、不缓存、不解析、不 OCR、不浏览器/form replay、不生成 source_packet parse 或 intake rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 113. 2026-05-17 P1 batch16 cache readiness packet

已新增 P1 batch16 cache readiness packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_cache_readiness_packet.csv`
- `reports/reference_trend_520_p1_batch16_cache_readiness_packet_rollup.csv`
- `reports/reference_trend_520_p1_batch16_cache_readiness_packet_qa.csv`
- `reports/reference_trend_520_p1_batch16_cache_readiness_packet_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch16_cache_readiness_packet.md`

覆盖结果：从 marker 112 的 17 条 action rows 派生 17 条 readiness rows；分流出静态官方页面/PDF/query 缓存候选、detail drilldown 候选、context hold 和 special boundary hold。QA PASS。

准入边界：本轮只生成 readiness packet，不联网、不缓存、不解析、不 OCR、不浏览器/form replay、不生成 source_packet parse 或 intake rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 114. 2026-05-17 P1 batch16 static cache execution queue

已新增 P1 batch16 static cache execution queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_execution_queue.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_execution_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_execution_queue_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_execution_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch16_static_cache_execution_queue.md`

覆盖结果：从 marker 113 的 17 条 readiness rows 中抽出 10 条可作为后续静态缓存/查询候选的 rows；其余 7 条保持 context/special-boundary hold。该队列只定义后续官方 URL 静态抓取边界，不执行联网、不缓存、不解析、不 OCR、不浏览器/form replay。QA PASS。

准入边界：本轮只生成 execution queue，不生成 source_packet parse 或 intake rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 115. 2026-05-17 P1 batch16 static cache run manifest

已新增 P1 batch16 static cache run manifest：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_run_manifest.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_run_manifest_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_run_manifest_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_run_manifest_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch16_static_cache_run_manifest.md`

覆盖结果：为 marker 114 的 10 条 static-cache execution candidates 预留 target cache paths 与 receipt IDs；按 detail_url_discovery/static_html/static_pdf/static_query 分流。QA PASS。

准入边界：本轮只生成 run manifest，不联网、不缓存、不解析、不 OCR、不浏览器/form replay；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 116. 2026-05-17 P1 batch16 static cache approval sheet

已新增 P1 batch16 static cache approval sheet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_approval_sheet.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_approval_sheet_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_approval_sheet_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_approval_sheet_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch16_static_cache_approval_sheet.md`

覆盖结果：为 marker 115 的 10 条 run manifest rows 生成可填写人工批准表，并保留 selected_decision/reviewer/decision_notes/approved_at 字段。当前未检测到人工决策 rows。QA PASS。

准入边界：本轮只生成 approval sheet，不联网、不缓存、不解析、不 OCR、不浏览器/form replay；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 117. 2026-05-17 P1 batch16 static cache post-approval status

已新增 P1 batch16 static cache post-approval status preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch16_static_cache_post_approval_status.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_post_approval_status_rollup.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_post_approval_status_qa.csv`
- `reports/reference_trend_520_p1_batch16_static_cache_post_approval_status_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch16_static_cache_post_approval_status.md`

覆盖结果：读取 marker 116 的 10 条 approval rows 并生成 post-approval status；当前 selected_decision 仍全空，future_runner_eligible rows 为 0。QA PASS。

准入边界：本轮只生成 post-approval status preview，不联网、不缓存、不解析、不 OCR、不浏览器/form replay；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 118. 2026-05-17 P1 batch17 discovery workset

已新增 P1 batch17 official-source discovery workset：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_discovery_workset.csv`
- `reports/reference_trend_520_p1_batch17_discovery_workset_rollup.csv`
- `reports/reference_trend_520_p1_batch17_discovery_workset_qa.csv`
- `reports/reference_trend_520_p1_batch17_discovery_workset_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_discovery_workset.md`

覆盖结果：从 plan_source_packet_queue 抽取 ranks 191-210，共 20 条 group-level workset rows，覆盖 19 所院校；所有行仍为 P1_plan_source_packet_high。QA PASS。

准入边界：本轮只生成发现工作集和 QA/rollup，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 119. 2026-05-17 P1 batch17 university discovery queue

已新增 P1 batch17 university-level discovery queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_university_discovery_queue.csv`
- `reports/reference_trend_520_p1_batch17_university_discovery_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_university_discovery_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_university_discovery_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_university_discovery_queue.md`

覆盖结果：将 marker 118 的 20 条 group-level workset rows 折叠为 19 条院校级 discovery tasks；河北北方学院两个 group rows 已合并为一个院校级任务。QA PASS。

准入边界：本轮只做去重后的官方来源发现队列，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 120. 2026-05-17 P1 batch17 discovery execution packet

已新增 P1 batch17 discovery execution packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_discovery_execution_packet.csv`
- `reports/reference_trend_520_p1_batch17_discovery_execution_packet_rollup.csv`
- `reports/reference_trend_520_p1_batch17_discovery_execution_packet_qa.csv`
- `reports/reference_trend_520_p1_batch17_discovery_execution_packet_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_discovery_execution_packet.md`

覆盖结果：从 marker 119 的 19 条院校级 discovery tasks 派生 19 条执行约束 rows，覆盖 20 个 group-level 目标；按本地院校、医学/民族/农学/师范语言/标准官方计划发现 lane 分流，并为每条记录写入 stop condition 和人工批准触发条件。QA PASS。

准入边界：本轮只生成未来官方来源发现的 execution packet，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；不声明任何官方来源已找到；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 121. 2026-05-17 P1 batch17 official candidate preview

已新增 P1 batch17 official-source candidate preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_candidate_preview.csv`
- `reports/reference_trend_520_p1_batch17_official_candidate_preview_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_candidate_preview_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_candidate_preview_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_candidate_preview.md`

覆盖结果：从 marker 120 execution packet 中抽取 7 条院校任务做官方来源候选预览；其中 1 条为 T1 精确广西计划页候选，其余为官方查询页/计划门户/JS 入口/图片计划页/聚合计划页候选或 backoff。QA PASS。

准入边界：本轮只记录官方来源候选和阻塞原因；不执行终端抓取、缓存、解析、OCR、浏览器/form replay；不生成 source_packet parse rows；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 122. 2026-05-17 P1 batch17 JXUTCM source packet parse preview

已新增江西中医药大学 T1 官方页 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview.md`

覆盖结果：从 marker 121 的江西中医药大学精确广西计划页候选中解析出 26 条 2025 广西本科普通批物理类专业计划 rows，计划合计 62；按源页短专业组代码汇总为 5 个 source group-year preview rows（01=13, 04=4, 06=30, 08=7, 02=8）。QA PASS。

准入边界：本轮只生成 source_packet 解析预览；源页为计划表，不含最低分/最低位次，且短专业组代码仍需与广西填报系统/投档线做映射 QA；reference trend intake、calibration、canonical/ML、32 所 decision_pool 均继续关闭。


## 123. 2026-05-17 P1 batch17 JXUTCM group join readiness

已新增江西中医药大学 source-group join readiness：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_group_join_readiness.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_group_join_readiness_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_group_join_readiness_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_group_join_readiness_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_jxutcm_group_join_readiness.md`

覆盖结果：将 marker 122 的 26 条专业计划 rows 汇总为 5 条 source-group readiness rows，计划合计保持 62；仅 `01 -> 101` 记录为后缀候选映射，不作为已确认映射；未发现本地 10412 投档线/最低位次 source，可 join rows 为 0。QA PASS。

准入边界：本轮只生成 group mapping 与 line/rank join readiness；不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步需要官方广西 2025 本科普通批物理类投档线/最低位次，并验证源页短专业组代码与广西填报系统专业组代码映射。


## 124. 2026-05-17 P1 batch17 JXUTCM line score reachability

已新增江西中医药大学官方投档最低分 reachability：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_line_score_reachability.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_line_score_reachability_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_line_score_reachability_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_line_score_reachability_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_jxutcm_line_score_reachability.md`

覆盖结果：定位到广西招生考试院 2025 本科普通批首选物理科目组投档最低分页面中的 `10412 江西中医药大学 101 527`，生成 1 条 official exam-authority line-score candidate；最低位次未在该源页提供，rank join rows 仍为 0。QA PASS。

准入边界：本轮只生成 score reachability，不做位次换算、不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool；`01 -> 101` 仍为源计划短组到考试院专业组的候选映射，需后续官方一分一档/位次来源与映射 QA。


## 125. 2026-05-17 P1 batch17 JXUTCM rank backoff candidates

已新增江西中医药大学 527 分位次 backoff QA 候选包：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_jxutcm_rank_backoff_candidates.md`

覆盖结果：在官方细分页仍未缓存/解析的前提下，记录两个第三方镜像候选位次，仅用于 QA backoff：`总分=总成绩+全国性加分` 口径下 527 分候选名次 `37291`，`总成绩+全国性加分和地方性加分的最高分` 口径下候选名次 `37372`。由于来源不是已缓存官方页，且总分口径未选择，selected rank rows 仍为 0。QA PASS。

准入边界：本轮不把 37291/37372 写入最低位次，不做位次 join，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步需要官方广西招生考试院一分一档细页浏览器态缓存或其他可审计官方表格来确认 527 的正确位次口径。


## 126. 2026-05-17 P1 batch17 exam-authority line-score batch

已新增 P1 batch17 广西考试院投档最低分批量 reachability：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_exam_authority_line_score_batch.csv`
- `reports/reference_trend_520_p1_batch17_exam_authority_line_score_batch_rollup.csv`
- `reports/reference_trend_520_p1_batch17_exam_authority_line_score_batch_qa.csv`
- `reports/reference_trend_520_p1_batch17_exam_authority_line_score_batch_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_exam_authority_line_score_batch.md`

覆盖结果：基于广西招生考试院 2025 本科普通批首选物理科目组投档最低分官方页的索引片段，覆盖 marker 121 的 8 条 group target rows；其中 6 条可确认官方最低分：`10596-153=490`、`10412-101=527`、`10407-102=461`、`10092-151=490`、`10092-152=462`、`10466-152=382`。`14275-105` 与 `10513-105` 在本轮官方物理页片段搜索中未确认，保持 blank。QA PASS。

准入边界：本轮只生成 line-score reachability；官方投档线页不含最低位次，所有 `min_rank` 继续为空，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。


## 127. 2026-05-17 P1 batch17 coverage rollup

已新增 P1 batch17 覆盖面总账：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_coverage_rollup.csv`
- `reports/reference_trend_520_p1_batch17_coverage_rollup.csv`
- `reports/reference_trend_520_p1_batch17_coverage_rollup_qa.csv`
- `reports/reference_trend_520_p1_batch17_coverage_rollup_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_coverage_rollup.md`

覆盖结果：将 marker 118-126 的 workset、官方候选源、江西中医药计划解析、广西考试院投档最低分、位次 backoff QA 合并为 20 条 group-target coverage rows。当前 8/20 个 group rows 已覆盖官方候选源，6/20 个 group rows 已补官方投档最低分，1/20 个 group rows 有计划数候选解析，0/20 个 group rows 有可采信官方最低位次。QA PASS。

准入边界：本轮只生成 coverage/QA/exclusion/rollup，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步应优先补 12 条 workset-only 的官方候选源，或对 6 条已有最低分 rows 做官方一分一档位次缓存/验证。


## 128. 2026-05-17 P1 batch17 official candidate gap queue

已新增 P1 batch17 official-candidate gap queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_candidate_gap_queue.csv`
- `reports/reference_trend_520_p1_batch17_official_candidate_gap_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_candidate_gap_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_candidate_gap_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_candidate_gap_queue.md`

覆盖结果：从 marker 127 的 coverage rollup 中抽取 12 条 `workset_only_no_official_candidate` rows，并回连 marker 120 execution packet 的搜索 query、lane、stop condition 和人工批准触发条件。QA PASS。

准入边界：本轮只生成下一轮官方来源发现 gap queue，不执行联网搜索、终端抓取、浏览器/form replay、缓存、解析或 OCR；不声明任何官方来源已找到；reference trend intake、canonical/ML、32 所 decision_pool 均继续关闭。


## 129. 2026-05-17 P1 batch17 gap search pulse A

已新增 P1 batch17 gap search pulse A：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gap_search_pulse_a.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_a_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_a_qa.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_a_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_gap_search_pulse_a.md`

覆盖结果：对 marker 128 前 4 条 gap rows 做官方-only web discovery 记录；3 条进入后续 source-packet preview/reachability 候选（浙大宁波理工学院官方招生计划查询页、浙江中医药大学官方招生计划查询入口、温州大学官方省外招生计划图片页），1 条海南师范大学仅确认官方站点/招生入口，未找到可用计划页。QA PASS。

准入边界：本轮只记录官方来源候选/回退状态，不缓存、不解析、不 OCR、不浏览器/form replay、不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。


## 130. 2026-05-17 P1 batch17 gap search pulse B

已新增 P1 batch17 gap search pulse B：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gap_search_pulse_b.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_b_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_b_qa.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_b_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_gap_search_pulse_b.md`

覆盖结果：对 marker 128 的 gap rows 0005-0008 做官方-only web discovery 记录；3 条进入后续 source-packet preview/reachability 候选（湖南农业大学官方外省招生计划 HTML 表、湖南理工学院官方 2025 本科招生计划图片页、牡丹江医科大学官方招生计划列表中的广西详情链接），1 条湖南师范大学仅确认官方招生站链接到计划查询，但可访问查询面提示登录/缓存缺失，保持 reachability backoff。QA PASS。

准入边界：本轮只记录官方来源候选/回退状态，不缓存、不解析、不 OCR、不使用浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。


## 131. 2026-05-17 P1 batch17 gap search pulse C

已新增 P1 batch17 gap search pulse C：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gap_search_pulse_c.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_c_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_c_qa.csv`
- `reports/reference_trend_520_p1_batch17_gap_search_pulse_c_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_gap_search_pulse_c.md`

覆盖结果：对 marker 128 的 gap rows 0009-0012 做官方-only web discovery 记录；1 条进入后续 source-packet preview/reachability 候选（福建中医药大学官方招生站链接的 2025 普通本科招生计划微信公众号页），3 条保持 reachability/backoff（西北民族大学官方招生工作入口未定位静态计划页，西华大学官方招生计划导航重定向缓存缺失，西安外国语大学官方招生计划栏可读但未定位 2025 全国/广西计划）。QA PASS。

准入边界：本轮只记录官方来源候选/回退状态，不缓存、不解析、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。


## 132. 2026-05-17 P1 batch17 gap pulse coverage update

已新增 P1 batch17 gap pulse coverage update：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gap_pulse_coverage_update.csv`
- `reports/reference_trend_520_p1_batch17_gap_pulse_coverage_update_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gap_pulse_coverage_update_qa.csv`
- `reports/reference_trend_520_p1_batch17_gap_pulse_coverage_update_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_gap_pulse_coverage_update.md`

覆盖结果：将 marker 129-131 的 12 条 gap pulse 结果合并回 marker 127 的 20 条 batch17 group-target coverage ledger。现在 20/20 条都有官方候选或官方 reachability/backoff 结果；其中 15/20 条进入后续 source-packet preview/QA 跟进候选，5/20 条保持 backoff；6/20 条保留广西考试院官方最低分，0/20 条有可采信官方最低位次。QA PASS。

准入边界：本轮只生成合并 coverage/QA/exclusion/rollup，不联网、不缓存、不解析、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。


## 133. 2026-05-17 P1 batch17 source-packet preview action queue

已新增 P1 batch17 source-packet preview action queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_source_packet_preview_action_queue.csv`
- `reports/reference_trend_520_p1_batch17_source_packet_preview_action_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_source_packet_preview_action_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_source_packet_preview_action_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_source_packet_preview_action_queue.md`

覆盖结果：从 marker 132 的 15 条 source-packet preview 候选生成可执行 QA 队列，另将 5 条仅 reachability/backoff rows 写入 exclusion log。队列中 10/15 条可优先做本地/静态 QA 或 mapping/rank join readiness，5/15 条涉及浏览器/JS、图片资产、OCR、微信或其他人工授权边界。QA PASS。

准入边界：本轮只生成行动队列/QA/exclusion/rollup，不联网、不缓存、不解析、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态，不写入 reference trend intake、canonical/ML 或 32 所 decision_pool。


## 134. 2026-05-17 P1 batch17 official rank join gap queue

已新增 P1 batch17 official rank join gap queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_rank_join_gap_queue.csv`
- `reports/reference_trend_520_p1_batch17_official_rank_join_gap_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_rank_join_gap_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_rank_join_gap_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_rank_join_gap_queue.md`

覆盖结果：从 marker 133 的 15 条 action queue rows 中抽取 6 条已有广西考试院官方最低分、但缺官方最低位次的 group-year rows，形成 5 个 unique score lookup targets：527, 490, 462, 461, 382。其余 9 条因尚无官方最低分或不具备 rank join 条件写入 exclusion log。QA PASS。

准入边界：本轮只生成官方位次 join 缺口队列，不抓取一分一档细页、不重复已阻塞的终端 curl、不采用第三方镜像位次、不做位次换算；reference trend intake、calibration、canonical/ML、32 所 decision_pool 继续关闭。


## 135. 2026-05-17 P1 batch17 official score-rank lookup targets

已新增 P1 batch17 official score-rank lookup targets：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_score_rank_lookup_targets.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_lookup_targets_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_lookup_targets_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_lookup_targets_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_score_rank_lookup_targets.md`

覆盖结果：将 marker 134 的 6 条 rank join gap rows 去重为 5 个 official score-rank lookup targets；其中 `490` 一次 lookup 服务 `10596-153` 与 `10092-151` 两条 group-year consumers。QA PASS。

准入边界：本轮只生成去重 lookup target/QA/rollup，不抓取一分一档细页、不重复已阻塞终端 curl、不采用第三方镜像位次、不选择或推断 min_rank；reference trend intake、calibration、canonical/ML、32 所 decision_pool 继续关闭。


## 136. 2026-05-17 P1 batch17 official score-rank capture approval packet

已新增 P1 batch17 official score-rank capture approval packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.md`

覆盖结果：将 marker 135 的 5 个 official score-rank lookup targets 转成浏览器态/官方 raw cache 批准包，覆盖 6 条 group-year consumers；`490` 继续保持一次 lookup 服务 2 条 group-year 的 fanout。QA PASS。

准入边界：本轮只生成批准包/QA/rollup，不抓取一分一档细页、不重复已阻塞终端 curl、不采用第三方镜像位次、不选择或推断 min_rank；等待用户批准浏览器态/可审计替代抓取或提供官方 raw artifact 后才能继续。

## 137. 2026-05-17 P1 batch17 safe static QA subqueue

已新增 P1 batch17 safe static QA subqueue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_safe_static_qa_subqueue.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_subqueue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_subqueue_qa.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_subqueue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_safe_static_qa_subqueue.md`

覆盖结果：从 marker 133 的 15 条 source-packet preview action queue 中拆出 8 条无需新增批准的 strict local/static QA rows，另将 7 条因浏览器/JS、条件 fetch、图片/OCR 或 WeChat 边界写入 exclusion log。子队列中 6 条保留官方最低分用于 QA/readiness，但 `min_rank` 全部继续为空。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步可在该子队列内做本地表格对齐、既有 source_packet preview QA、group mapping readiness 和 coverage rollup；官方位次仍等待 marker 136 批准包或用户提供官方 raw artifact。

## 138. 2026-05-17 P1 batch17 safe static QA local artifact inventory

已新增 P1 batch17 safe static QA local artifact inventory：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory_rollup.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory_qa.csv`
- `reports/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_safe_static_qa_local_artifact_inventory.md`

覆盖结果：读取 marker 137 的 8 条 strict safe/static QA rows，并仅用本地已有 batch17 文件回连 artifact inventory。6 条保留官方最低分用于 QA/readiness，0 条选择最低位次；当前仅 1 条（江西中医药大学 `10412-101`）具备本地 parsed plan preview/group join readiness 可立即做 mapping consistency QA，其余 7 条仍需本地 parse/mapping artifact、官方位次 raw cache 或人工批准后才能进入下一层。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开微信/浏览器/form/header/cookie/login 状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步可优先对 `10412-101` 做本地 mapping consistency QA，或等待 marker 136 官方一分一档 raw artifact/浏览器态批准以补 5 个分数位次。

## 139. 2026-05-17 P1 batch17 JXUTCM mapping consistency QA

已新增 P1 batch17 江西中医药大学 mapping consistency QA：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_jxutcm_mapping_consistency_qa.md`

覆盖结果：读取 marker 122/123/124/138 的本地产物，对 `10412-101` 做 source short group 到广西考试院专业组的保守一致性检查。`01 -> 101` 仅为后缀候选映射，不作为已确认映射；该候选组有 6 个专业、计划数 13，并含 1 条 `5+3` 行，已标记 special-type/boundary review。广西考试院官方最低分 `527` 已回连到候选组，但最低位次继续为空；`02/04/06/08` 作为相邻 source groups 全部排除出目标组 mapping。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步需要官方 group-code 映射确认或 marker 136 的官方一分一档 raw artifact，才能继续 rank join/eligibility 判断。

## 140. 2026-05-17 P1 batch17 post-mapping action board

已新增 P1 batch17 post-mapping action board：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_post_mapping_action_board.csv`
- `reports/reference_trend_520_p1_batch17_post_mapping_action_board_rollup.csv`
- `reports/reference_trend_520_p1_batch17_post_mapping_action_board_qa.csv`
- `reports/reference_trend_520_p1_batch17_post_mapping_action_board_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_post_mapping_action_board.md`

覆盖结果：读取 marker 133/136/138/139 的本地产物，把 batch17 后续工作拆成 15 条 group action、5 条 coverage backoff 和 5 条 unique score-rank lookup target。当前 6 条 group rows 有官方最低分但均无最低位次；5 个分数 lookup target（527/490/462/461/382）仍等待 marker 136 的用户批准或官方 raw artifact。`10412-101` 已携带 marker 139 的 candidate-only mapping 结论继续阻塞在官方 group-code confirmation + rank raw artifact。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可从 action board 中优先处理本地 checklist rows，或在用户批准/提供官方 raw 后处理 score-rank fanout。

## 141. 2026-05-17 P1 batch17 local checklist execution queue

已新增 P1 batch17 local checklist execution queue：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_local_checklist_execution_queue.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_execution_queue_rollup.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_execution_queue_qa.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_execution_queue_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_local_checklist_execution_queue.md`

覆盖结果：读取 marker 140 的 25 条 action board rows，仅抽取 8 条无需新用户批准的本地 checklist/backoff 路由项；其中 3 条为本地 checklist/placeholder（湖南农业大学 table alignment、湖北师范大学 group boundary、牡丹江医科大学 local cache placeholder），5 条为 official-only discovery backoff queue。其余 17 条因等待官方 raw artifact、browser/static endpoint approval、OCR/manual image review、WeChat capture 或 rank/group confirmation 写入 exclusion log。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可对 3 条本地 checklist 行生成更细的表格/边界审核模板，或在用户批准后处理官方 rank/browser/OCR/WeChat 分支。

## 142. 2026-05-17 P1 batch17 local checklist review templates

已新增 P1 batch17 local checklist review templates：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_local_checklist_review_templates.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_review_templates_rollup.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_review_templates_qa.csv`
- `reports/reference_trend_520_p1_batch17_local_checklist_review_templates_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_local_checklist_review_templates.md`

覆盖结果：读取 marker 141 的 8 条 local checklist execution queue，将 3 条无需新批准的本地 checklist 行细化为 15 条审核模板：湖南农业大学 `10537-101` 表格列/专业组/特殊类型边界模板 5 条，牡丹江医科大学 `10229-101` 本地 cache 缺口/医学边界/位次闸门模板 5 条，湖北师范大学 `10513-105` aggregate source/group 105/师范语言方向/位次闸门模板 5 条。另将 5 条 official-only discovery backoff rows 保持在 exclusion log。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可在本地 artifact 或用户批准出现后填充这些模板，或继续等待 marker 136 官方一分一档 raw artifact/浏览器态批准。

## 143. 2026-05-17 P1 batch17 gated branch decision matrix

已新增 P1 batch17 gated branch decision matrix：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_gated_branch_decision_matrix.csv`
- `reports/reference_trend_520_p1_batch17_gated_branch_decision_matrix_rollup.csv`
- `reports/reference_trend_520_p1_batch17_gated_branch_decision_matrix_qa.csv`
- `reports/reference_trend_520_p1_batch17_gated_branch_decision_matrix_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_gated_branch_decision_matrix.md`

覆盖结果：读取 marker 140 action board、marker 136 官方 score-rank 批准包与 marker 142 本地审核模板，将 25 条 action board rows 归并为 10 个 gated decision families。矩阵保留 3 条本地模板分支、5 条 official-only backoff、5 个官方分数位次 raw lookup targets（527/490/462/461/382，覆盖 6 条 group-year consumers）、以及 browser/static endpoint、OCR/manual image、WeChat、JXUTCM group-code confirmation 等需要批准的分支。22 条非本地模板 rows 写入 exclusion log，等待官方 raw artifact 或用户批准。QA PASS。

准入边界：本轮不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不重复已阻塞终端 curl，不使用第三方位次，不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化可按矩阵等待用户批准/官方 raw，或在本地 artifact 出现后填 marker 142 模板。

## 144. 2026-05-17 P1 batch17 user approval decision sheet

已新增 P1 batch17 user approval decision sheet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_user_approval_decision_sheet.csv`
- `reports/reference_trend_520_p1_batch17_user_approval_decision_sheet_rollup.csv`
- `reports/reference_trend_520_p1_batch17_user_approval_decision_sheet_qa.csv`
- `reports/reference_trend_520_p1_batch17_user_approval_decision_sheet_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_user_approval_decision_sheet.md`

覆盖结果：读取 marker 143 的 10 个 gated decision families，抽取 7 条需要用户批准或官方 raw artifact 才能推进的 approval options：P0 官方 2025 物理类一分一档 raw/cache、P0 已有官方最低分的 min_rank join、P0 江西中医药大学 group-code confirmation + rank raw、P1 browser/static endpoint capture、P1 OCR/official extracted table、P1 WeChat 官方 artifact/capture、P2 optional backoff review。3 条本地模板分支写入 exclusion log，因为它们无需新批准。QA PASS。

准入边界：本轮只生成待批准 decision sheet，不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不重复已阻塞终端 curl，不使用第三方位次，不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化只有在用户批准或提供官方 raw artifact 后，才可按对应 option 进入 capture/QA preview。

## 145. 2026-05-17 P1 batch17 pipeline readiness rollup

已新增 P1 batch17 pipeline readiness rollup：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_pipeline_readiness_rollup.csv`
- `reports/reference_trend_520_p1_batch17_pipeline_readiness_rollup_rollup.csv`
- `reports/reference_trend_520_p1_batch17_pipeline_readiness_rollup_qa.csv`
- `reports/reference_trend_520_p1_batch17_pipeline_readiness_rollup_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_pipeline_readiness_rollup.md`

覆盖结果：读取 marker 143 decision matrix、marker 144 approval decision sheet 与 marker 142 local checklist templates，生成 8 条 readiness rows：1 条本地模板 bundle（3 所学校、15 条模板，等待本地/批准 artifact 才能填充）与 7 条待批准/官方 raw artifact 分支。当前可自主继续执行的 rows 为 0；5 个官方位次 lookup 分数（382/461/462/490/527）继续等待广西考试院官方 raw/cache 或浏览器态批准。QA PASS。

准入边界：本轮只生成 readiness/coverage rollup，不联网、不缓存、不解析新网页、不 OCR、不打开浏览器/form/header/cookie/微信状态；不重复已阻塞终端 curl，不使用第三方位次，不做人工边界接受，不选择或推断最低位次，不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool。下一步自动化应等待用户批准/提供官方 raw artifact，或等待本地 artifact 后再填 marker 142 模板。

