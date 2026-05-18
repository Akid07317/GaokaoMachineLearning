# Reference Trend 520 P0 Official Source Discovery Batch 8

Generated: 2026-05-16

## Scope

This batch covers uncovered P0 plan-source queue rows around queue ranks 42-50. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch8_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch8_exclusion_log.csv`

## Key Findings

- Candidate rows: 7
- Universities covered: 7
- T1 extractable official candidates: 1 (中南林业科技大学)
- Manual approval / browser-replay boundaries: 1 (上海第二工业大学)

High-value row:

1. 中南林业科技大学: official Guangxi plan HTML pages cached. Local table parse found 本科普通批物理类 major rows and plan counts, but no Guangxi professional-group code is printed.

Held/context rows:

- 上海应用技术大学、上海立信会计金融学院、中南财经政法大学: official charter/context pages cached; no first-party Guangxi group/major plan table found in this pass.
- 上海第二工业大学: official-domain candidate timed out in terminal fetch and is kept in reachability/backoff.
- 中国人民警察大学: official charter page is embedded PDF/image context, with public-security boundary concerns; not ordinary trend input.
- 中央美术学院: official charter context confirms art/ordinary boundary but not Guangxi ordinary plan rows.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next step should parse the 中南林业科技大学 T1 source into source-packet parse preview, then keep it held until group mapping/acceptance is explicit.
