# P1 Batch17 Official Score-Rank Capture Approval Packet

日期：2026-05-17

## 结果

从 marker 135 的 5 个 official score-rank lookup targets 生成浏览器态/官方 raw cache 批准包。该包用于明确：只有在用户批准浏览器态/可审计替代抓取，或提供官方 2025 广西物理类一分一档 raw artifact 后，后续模型才能选择 `min_rank`。

- 527: 1 consumer(s) -> 10412-101
- 490: 2 consumer(s) -> 10596-153|10092-151
- 462: 1 consumer(s) -> 10092-152
- 461: 1 consumer(s) -> 10407-102
- 382: 1 consumer(s) -> 10466-152

## 需要批准或人工提供的内容

- 官方来源范围：广西招生考试院 2025 一分一档表 首选物理科目组
- 可接受 artifact：官方 raw HTML、PDF、XLS/XLSX，或带 URL 与时间戳的 browser saved page
- 必填 artifact 字段：`raw_file_path`、`source_url`、`retrieved_at`、`score_column`、`rank_column`、`total_score_policy_note`

## 禁止动作

- 不重复终端 curl 已阻塞的 `qg/qn` 细分页路径
- 不使用第三方镜像位次
- 不从投档最低分推断位次
- 不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool

## 下一步

等待用户批准浏览器态/官方 raw cache 捕获，或用户直接提供官方一分一档 raw 文件。之后才能生成 score-rank parse preview。
