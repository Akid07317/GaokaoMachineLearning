# Reference Trend SCUEC Source Packet Parse

日期：2026-05-16

## 结论

已把中南民族大学两条 T1 官方候选页推进到 source packet 解析预览层。2025 计划页可抽取广西列计划数；2024 分数页可抽取广西普通类物理组分数参考。但两者都缺显式广西院校专业组代码，分数页也缺最低位次，因此本轮仍不生成 trend record，不进入 calibration/canonical/ML。

## 覆盖

- parsed rows: 43
- plan rows: 33
- score/reference rows: 10
- ordinary candidate rows: 36
- excluded special-type rows: 7
- parse status counts: {'parsed_plan_row': 32, 'parsed_excluded_special_type': 7, 'parsed_score_reference': 4}

## 下一步

- 将普通候选行继续用于 group mapping QA，而不是直接视为院校专业组-year。
- 用广西考试院投档线或一分一档补齐最低位次后，才能评估 calibration_eligible。
- 保持 32 所 decision_pool、canonical 和 ML 入口关闭。
