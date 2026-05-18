# Trend reference pool pivot

## Judgment

32 所学校不足以很好反映招生趋势。它们适合作为高精度目标决策池，不适合作为趋势学习的唯一样本池。

此前“不扩主池”的结论仍然成立，但它只适用于 canonical/ML 主入口和 32 所高精度目标池。若目标是识别广西物理类本科普通批的招生趋势，需要新增一个隔离的 reference trend pool。

## Revised data architecture

### A. Decision pool

- 范围：现有 32 所 211 工科目标校。
- 目标：逐校给出志愿风险、调剂风险、专业组可接受度和证据链。
- 标准：官方来源、专业组或可解释映射、计划数、最低分/最低位次、年份口径、特殊类型隔离。
- 状态：继续保持高门槛，canonical/ML 入口不自动打开。

### B. Reference trend pool

- 范围：广西物理类本科普通批中与目标用户分数带相关的更大样本。
- 目标：学习趋势、波动、热冷变化、计划数变化和专业组结构变化。
- 标准：可以低于 decision pool，但必须隔离标注置信度和来源类型。
- 不直接输出个体学校志愿决策，不直接写入 decision pool canonical。

## Why this is not the same as broad uncontrolled expansion

扩 decision pool 会把更多学校带入人工复核堵点；扩 reference trend pool 则是为了获得统计背景。

趋势池可以接受：

- 省考试院投档线或官方投档分数线；
- 院校专业组最低分/最低位次；
- 计划数缺失但分数/位次可靠的趋势样本；
- 专业细节不足但专业组代码清楚的记录；
- 可用作背景分布的同批次、同省份、同选科记录。

趋势池不应接受：

- 无法区分普通批、专项、预科、中外合作、民族班的混合记录；
- 无位次且无法换算位次的记录；
- 只有学校最低分、无法映射到专业组且学校存在多个普通组的记录；
- 未标明年份、批次、选科或省份的记录。

## Suggested sample strategy

趋势学习的基本单位不应是“学校”，而应是“院校专业组-年份”。

建议目标：

- 第一阶段：不少于 150 个 group-year 样本，覆盖 2023-2025。
- 第二阶段：300-600 个 group-year 样本，用于 rank delta、计划数变化和专业组结构变化。
- 第三阶段：按分数带分层，保留目标分数上下 20,000 位次内的重点样本。

## Pool boundaries

| Layer | Can Expand | Purpose | Output |
|---|---:|---|---|
| 32-school decision pool | No, not yet | 志愿决策证据链 | 人工/GPT 复核与后续 canonical rebuild |
| reference trend pool | Yes | 趋势背景、波动分布、同层比较 | trend calibration only |
| non-211 discovery pool | Yes, but isolated | 发现候选与参照样本 | 不能直接进入 decision canonical |
| G4 source branch | Only with approval | 官方来源可达性 | 不直接生成 ML 输入 |

## Immediate next step

停止把全部精力压在 32 所逐行完美化上。下一步应生成 reference trend pool schema 和 seed queue：

1. 定义 reference trend pool 字段。
2. 从已有非 211 discovery、source lists、广西物理类普通批投档/分数线材料中抽样。
3. 只收院校专业组-年份粒度记录。
4. 标注 confidence tier，而不是要求所有记录达到 decision pool 级别。
5. 生成 trend reference intake preview，不写 canonical/ML。

## Updated decision

现在应该继续搜集数据，但不是扩 32 所主决策池，也不是无边界搜学校。

应该启动隔离的 reference trend pool，用较低但可审计的门槛补充趋势样本；32 所继续作为高精度决策池保留。
