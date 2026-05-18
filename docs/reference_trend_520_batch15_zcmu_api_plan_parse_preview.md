# ZCMU Batch15 Official API Plan Parse Preview

Generated: 2026-05-16

## Scope

浙江中医药大学官方招生计划入口已确认：

- 招生办首页: https://zsb.zcmu.edu.cn/
- 招生计划页: https://zscx.zcmu.edu.cn/zsb_zcmu/zsjh.html
- 招生查询系统: https://zscx.zcmu.edu.cn/#/index
- 公开计划 API: https://zscx.zcmu.edu.cn/API/yxy/yxyRecruit/noTokenList
- 2025 招生章程上下文: https://zsb.zcmu.edu.cn/info/1074/4672.htm

本轮只生成 source-packet preview/QA，不写入 `reference_trend_pool`、canonical、ML，也不并入 32 所 `decision_pool`。

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_zcmu_api_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_zcmu_api_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_zcmu_api_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_zcmu_api_plan_parse_exclusion_log.csv`

## Coverage

- 2025 广西官方计划 API: 26 行，计划数合计 129；其中本科普通批/普通类/物理类 23 行，计划数合计 124。
- 2024 广西官方计划 API: 33 行，计划数合计 129；其中本科普通批/普通类/物理类 27 行，计划数合计 108。
- 两年同一官方 API 可形成计划侧趋势旁证，但 API 不含广西院校专业组代码、最低分或最低位次。

## Gate Boundary

所有记录继续：

- `reference_trend_pool_eligible=false`
- `calibration_eligible=false`
- `canonical_ml_entry_open=false`
- `decision_pool_boundary=do_not_merge_with_32_school_decision_pool`

下一步应与广西考试院院校专业组投档线/专业组上下文做 join workbench，再判断是否进入 calibration preview。
