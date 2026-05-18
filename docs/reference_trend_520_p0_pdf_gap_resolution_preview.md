# Reference Trend 520 P0 PDF Gap Resolution Preview

Run date: 2026-05-16

This package closes out previously discovered PDF field gaps for 云南中医药大学 and 南京中医药大学. It does not search the web, does not open browser/header/form replay, and does not write canonical or ML inputs.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_pdf_gap_resolution_preview.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_rollup.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_qa.csv`
- `reports/reference_trend_520_p0_pdf_gap_resolution_exclusion_log.csv`

## Coverage

- Queue rows resolved: 6
- 云南中医药大学 rows: 2. Current official PDF candidate is held because the prior QA run saw HTTP 404.
- 南京中医药大学 rows: 4. Current official PDF is rejected for Guangxi trend use because it parsed successfully but contains no Guangxi rows.
- QA: 7 pass / 0 fail.

## Boundary

All rows remain `eligible_for_intake_preview=false`, `reference_trend_pool_eligible=0`, `calibration_eligible=0`, and `canonical_ml_entry_open=false`. The 32-school decision pool is untouched.

## Next Action

Continue official-source relocation for these schools only if useful: 云南中医药大学 needs a valid official plan page/PDF/XLSX, and 南京中医药大学 needs an official page or file containing Guangxi physical ordinary-batch rows. If the next route needs header/cookie/form/browser state, pause for approval.
