# GPT-5.5 Pro Web Attachment Bottleneck Decision

更新时间：2026-05-13

来源：网页版 GPT-5.5 Pro 对 `outputs/project_bottleneck_summary_pack_2026-05-13.zip` 附件内容的复核判断。

## 1. 总结论

结论：现在先不要扩。

GPT-5.5 Pro 在读取附件内的 `docs/project_bottleneck_summary_pack.md`、pre-ML gate status、decision register、`guangxi_pre_ml_*`、source resolution matrix、master operating board 以及非 211 两张 CSV 后，判断比纯文本摘要阶段更明确：

- 不应该立即扩充主数据池。
- 不应该把 Deep Research 用作扩池主线。
- 当前阶段是 pre-ML 复核决策阶段，不是扩池阶段，也不是建模阶段。

## 2. 不扩主池的依据

主池 32 所已经全部有 pre-ML gate status：

- 18 所已经能进入人工/GPT 复核闸门。
- 3 所只差人工接受本地补洞候选。
- 11 所是 `G4_blocked_or_manual_route`。

decision register 已有 21 所，但 21 所全部仍是 `pending_human_gpt_review_decision`，完成复核决策数为 0。

因此当前瓶颈不是候选学校太少，而是已有候选没有完成闸门决策。最短路径是先处理这 21 所 decision register：

- 8 所 `D1_clean_pending_decision`。
- 10 所 `D2_caution_pending_decision`。
- 3 所 `D3/D4_gap_fill_acceptance_pending_decision`。

非 211 扩池文件也不支持立即扩主池：

- `non211_authoritative_todo.csv` 只有 10 所候选，其中 1 所 `seed_discovered`，1 所 `seed_needs_refine`，8 所 `queued`。
- `non211_authoritative_discovery_candidates_priority.csv` 虽有 277 行，但实际主要覆盖南京信息工程大学和西南石油大学两个 `source_name`，且大量行属于 review/noise。

非 211 当前只能作为观察池/发现池，不能并入主 pre-ML 口径。

## 3. 扩样本优先级

GPT-5.5 Pro 建议将“扩样本”拆成先扩可训练层，再扩学校：

1. 训练层级/数据层级：先把 18+3 所从 pending 推到 accepted/caution/hold/reject，再重建 canonical snapshot 和 trend。
2. 院校专业组粒度：不能用学校最低分替代专业组；无专业组映射的样本只能做背景参考。
3. 同口径年份数：在专业组粒度成立后补同口径年份，不能硬混不同批次、特殊类型、非第一次正式投档或选科口径不一致年份。
4. 字段厚度：最低位次、最低分、计划数、专业组内专业构成、选科要求、特殊类型标记、来源精度、是否 2025 最新、趋势信号等字段决定解释质量。
5. 学校数：最后才扩学校。过早扩校只会把 21 个 pending 扩成更多 pending。

压缩判断：先复核层级，再专业组粒度，再同口径年份，再字段厚度，最后才扩学校数。

## 4. Deep Research 边界

不建议现在把 Deep Research 作为主线启动。

当前最有价值的动作是处理 decision register，不是重新开大范围外部调查。

Deep Research 只可作为非常窄的后置支线：针对 11 所 `G4_blocked_or_manual_route` 的官方来源可达性调查。

允许调查范围：

- 官方招生计划来源是否可达。
- 官方历年录取分数来源是否可达。
- 页面是静态页、JS 接口、PDF、缓存页、403/header 问题、登录态问题、表单 replay 问题，还是必须人工查证。
- 对应路线拆为 `P1_static_family_ready`、`P1_js_endpoint_exposed`、`P2_cached_entry_waiting_headers`、`P3_manual_review`。

禁止用途：

- 不做扩池推荐。
- 不做非 211 大搜集。
- 不替代复核决策。
- 不直接生成 ML 输入。

## 5. 下一步顺序

1. 冻结主池和 ML 入口。主池保持 32 所 211 工科目标校；非 211 10 所只保留在 todo/discovery 层；机器学习继续关闭。
2. 先处理 8 所 D1/G1 clean pending decision：北京交通大学、福州大学、华东理工大学、南京理工大学、武汉理工大学、西南交通大学、郑州大学、中国地质大学北京。
3. 再处理 10 所 D2/G2 caution pending decision：重点核对缺计划、缺位次、趋势缺失、reference year 不是最新、fallback source、score only/partial plan 等问题。
4. 处理 3 所 D3/D4 本地补洞接受判断：河北工业大学、太原理工大学可预览为 G1 candidate；北京邮电大学仍偏 G2 caution candidate。
5. 把 11 所 G4 单独拆成外部来源任务；可选用窄边界 Deep Research，但只查官方来源可达性和技术路线。
6. 复核完成后重建 canonical snapshot/trend，再判断是否小扩。

## 6. 项目行动口径

短期项目口径固定为：

- 不扩主池。
- 不启动 ML。
- 不把非 211 观察池并入主数据池。
- 优先处理 D1/G1 与 D2/G2 的 pending review decision。
- Deep Research 仅保留为 G4 官方来源可达性支线。
