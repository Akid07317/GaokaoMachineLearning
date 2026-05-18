# Reference Trend 520 P0 Official Source Discovery Batch 10

Generated: 2026-05-16

## Scope

This batch covers P0 plan-source queue rows around queue ranks 63-75. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch10_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_exclusion_log.csv`

## Key Findings

- Candidate rows: 10
- Queue ranks covered: 63, 65, 67, 68, 70, 71, 72, 73, 74, 75
- Universities covered: 8
- Rows with cached official pages/assets: 5
- Manual approval / browser-form-OCR boundaries: 5 (大连医科大学中山学院、天津外国语大学、宁夏大学、山东政法学院)

High-value cached rows:

1. 宁夏医科大学: official 2025 plan page and attached PDF cached; PDF plan rows still need parsing.
2. 宁夏大学: official parameterized plan portal and 2025 charter baseline cached; portal/API drilldown still needed.
3. 山东政法学院: official 2025 plan page cached with embedded Guangxi image; OCR/image extraction needed.
4. 天津外国语大学: official charter and plan index cached, but no structured Guangxi plan rows exposed.

Held/backoff rows:

- 大连医科大学中山学院: first-party plan page found, but terminal cache failed on certificate verification; kept in TLS reachability/backoff.
- 安徽理工大学: official-domain candidate returned 404 on cache attempt.
- 四川师范大学、山东师范大学: no accepted first-party Guangxi plan source found in this pass.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next safe step is to parse 宁夏医科大学 PDF if a PDF parser is available, or continue official-source discovery from the next uncovered P0 rows.
