# D2/G2 Request Row Fix Queue

生成时间：2026-05-14

## 结论

已把 D2/G2 GPT 复核中 5 个 `request_row_fix` 项拆成独立修复队列。该队列只处理行级修复和来源/字段复核，不打开 ML，不直接写入 canonical 层。

## 队列分层

- `P0_source_identity_fix`：1 所，华北电力大学。原因是来源 URL 含 `yoursite.com` 占位域名，必须先重获官方招生计划/历年分数 URL。
- `P1_latest_plan_score_alignment`：1 所，北京工业大学。重点是补齐 2025 计划侧结构化记录，并确认 2025 分数/位次是否可替代 2024 可比记录。
- `P1_reference_year_and_field_mapping`：3 所，长安大学、合肥工业大学、南京航空航天大学。重点是用已有官方结构化源复核字段映射，把计划数、最低分、最低位次与 reference_year 说明写实。

## 当前处理原则

1. 含占位 URL 的学校先停在 row fix，不进入 canonical。
2. reference year 不是最新的学校，先修字段映射和备注，不用学校最低分硬替专业组口径。
3. 已有结构化计划/分数源的学校优先做本地字段复核，不重新扩池。
4. 所有修复项完成后再重刷 D2/G2 decision、post-gap-fill gate、handoff 和 workbench。

## 本轮产物

- `scripts/build_engineering_pre_ml_d2_g2_request_row_fix_queue.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv`
- `reports/engineering_pre_ml_d2_g2_request_row_fix_queue_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_request_row_fix_queue_coverage_rollup.csv`
