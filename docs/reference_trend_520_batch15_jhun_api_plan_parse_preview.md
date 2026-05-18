# reference_trend_520 batch15 JHUN API plan parse preview

Generated: 2026-05-16

江汉大学官方招生计划查询系统已缓存并解析为 2025 广西物理类普通类 source-packet preview。本产物不进入 32 所 decision_pool。

## Result

- Official portal URL: https://bkzs.jhun.edu.cn/
- Official app URL: https://zsdata.jhun.edu.cn/zsdata/lqxx/#/
- API endpoint: https://zsdata.jhun.edu.cn/lqxx/s/api/front/lqxx/getList
- API payload: `{"type":"zsjh","sf":"广西","nf":"2025","zslb":"普通类","klmc":"物理类","xqmc":""}`
- Parsed rows: 16
- Plan sum: 169
- API summary jhrs: 169
- Group code available rows: 0
- Score/rank available: 0

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_batch15_jhun_api_plan_parse_preview.csv`
- `reports/reference_trend_520_batch15_jhun_api_plan_parse_rollup.csv`
- `reports/reference_trend_520_batch15_jhun_api_plan_parse_qa.csv`
- `reports/reference_trend_520_batch15_jhun_api_plan_parse_exclusion_log.csv`

## Gate Boundary

官方 API 可提取专业计划数和选科要求，但没有广西院校专业组代码、最低分或最低位次。所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。后续需与广西考试院 group-line score/rank 和专业组上下文做 join workbench。

## QA

- official_portal_cached: PASS - raw_sources/reference_trend/batch15_official/jhun_portal.html
- official_api_endpoint_discovered: PASS - raw_sources/reference_trend/batch15_official/jhun_zsdata_app.fe50b7c2.js|raw_sources/reference_trend/batch15_official/jhun_zsdata_lqcxjg.be9430e0.js
- gettype_has_guangxi_2025_physics: PASS - raw_sources/reference_trend/batch15_official/jhun_zsjh_gettype.json
- api_plan_rows_extracted: PASS - rows=16
- plan_sum_matches_api_summary: PASS - parsed=169; summary=169
- score_rank_hold: PASS - Official API is plan-only; no score or rank.
- no_reference_trend_pool_or_canonical_ml: PASS - No trend pool/canonical/ML writes.

## Rollup

- official_portal_cached_rows: 1 (raw_sources/reference_trend/batch15_official/jhun_portal.html)
- official_app_cached_rows: 1 (raw_sources/reference_trend/batch15_official/jhun_zsdata_lqxx_index.html)
- official_api_response_cached_rows: 1 (raw_sources/reference_trend/batch15_official/jhun_2025_guangxi_physics_plan_api.json)
- gettype_guangxi_2025_physics_available: 1 (raw_sources/reference_trend/batch15_official/jhun_zsjh_gettype.json)
- parse_preview_rows_all_guangxi_physics: 16 (API list rows)
- guangxi_physics_plan_count_sum: 169 (API summary jhrs=169)
- ordinary_physics_candidate_rows: 16 (physical ordinary rows excluding special boundaries)
- ordinary_physics_candidate_plan_sum: 169 ()
- source_group_code_available_rows: 0 (API zygroup is blank for current rows)
- subject_requirement_distribution: {'物理(1门科目考生必须选考方可报考)': 2, '物理,化学(2门科目考生均须选考方可报考)': 12, '不提科目要求': 2} ()
- special_boundary_rows: 0 ({'none_detected': 16})
- score_rank_available_rows: 0 (Plan API only; no score/rank.)
- reference_trend_pool_eligible_rows: 0 (Score/rank and group join required before calibration.)
- calibration_eligible_rows: 0 (No group-year calibration opened.)
- canonical_ml_entry_open_rows: 0 (Canonical/ML remains closed.)
