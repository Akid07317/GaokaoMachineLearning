# Reference Trend 520 P0 Official Source Discovery Batch 9

Generated: 2026-05-16

## Scope

This batch covers next P0 plan-source queue rows after batch8, mainly queue ranks 51-64 except rank 55, which already has a mapping workbench. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch9_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch9_exclusion_log.csv`

## Key Findings

- Candidate rows: 12
- Queue ranks covered: 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62, 64
- Universities covered: 9
- T1 extractable official candidates: 1 (北方工业大学)
- Manual approval / browser-form-image boundaries: 7 (五邑大学、华侨大学、南昌航空大学、四川轻化工大学)
- No first-party official source found this pass: 2 (北京建筑大学、华北理工大学)

High-value row:

1. 北方工业大学: official 2025本科分专业招生计划 HTML table includes a 广西 column and appears parseable. It does not expose Guangxi professional-group codes, so parsing must still hold group-year calibration until mapping is verified.

Held/context rows:

- 云南师范大学: official parameterized plan portal found; 广西/物理类 drilldown needs API/browser inspection.
- 五邑大学: official 2025外省招生计划 page found, but plan details are embedded images; OCR or official system extraction is needed.
- 华侨大学: official 2025分省分专业计划 page found in search, but direct open returned 403; keep in reachability/backoff.
- 南昌航空大学: official query-entry context found, but no structured Guangxi rows exposed yet.
- 四川轻化工大学: official attachment bundle candidate found; attachment parse is still pending.
- 北师香港浸会大学: official charter PDF context found; no Guangxi plan table.
- 北京建筑大学、华北理工大学: no first-party Guangxi 2025 plan source found in this pass.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next safe step is to parse 北方工业大学 T1 HTML, and separately hold 云南师范大学/五邑大学/华侨大学/四川轻化工大学 for approved browser/API/OCR/attachment handling.
