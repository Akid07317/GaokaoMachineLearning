# Reference Trend Lanzhou Jiaotong Group Mapping Workbench

日期：2026-05-16

## 结论

已基于广西考试院 `2024` 兰州交通大学物理类本科普通批投档线，对校方官方 API 的计划/专业分记录生成候选专业组映射工作台。考试院存在两个专业组：`101` 与 `102`；校方 API 未直接给组代码，因此本轮只生成候选映射，不产生正式 `院校专业组-year` 趋势记录。

## 考试院组线

- 2024 group 101: min_score 527, rank 38700
- 2024 group 102: min_score 503, rank 54153

## 覆盖

- workbench rows: 52
- score-major candidate rows: 26
- plan-major candidate rows: 26
- single-candidate rows: 12
- ambiguous candidate rows: 40
- unmapped rows: 0
- reference trend eligible rows: 0
- canonical/ML entry: closed

## 使用边界

候选规则只利用“专业最低分不低于组最低投档线”的必要条件，不能替代官方专业组结构。分数低于 `101` 组线且不低于 `102` 组线的专业可形成较强的 `102` 候选；高于 `101` 组线的专业仍可能属于任一组，需要招生计划专业组结构或人工核验。

## 下一步

1. 优先寻找兰州交通大学 `2024/2025` 专业组结构或广西招生计划 PDF/静态表。
2. 若找不到组结构，只能把该校保留为 source-packet + mapping workbench，不能正式进入 group-year trend pool。
3. 下一轮可继续处理新落地的北京工业大学/东华大学等官方缓存行，或推进下一批 P0/P1 非主池发现。
