# Reference trend 520 P1 batch17 JXUTCM line score reachability

Generated: 2026-05-17

## Scope

This packet records an official Guangxi exam-authority投档最低分 candidate for江西中医药大学 `10412-101`.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_jxutcm_line_score_reachability.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_line_score_reachability_rollup.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_line_score_reachability_qa.csv`
- `reports/reference_trend_520_p1_batch17_jxutcm_line_score_reachability_exclusion_log.csv`

## Source

- 广西招生考试院: https://www.gxeea.cn/view/content_1013_31850.htm

## Result

- Official exam-authority group: `10412-101`
- 投档最低分: 527
- 最低位次: not available on this source
- Plan-source short group `01` remains a suffix candidate for `101`, not an accepted mapping.

## Boundary

- This is score reachability only, not reference-trend intake.
- Rank join remains blocked pending official一分一档 or another authoritative rank source.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`.
