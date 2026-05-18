# Reference Trend 520 P0 Official Source Discovery Batch15

Generated: 2026-05-16

Scope: queue ranks 151-170 from `reference_trend_520_plan_source_packet_queue.csv`.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch15_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch15_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch15_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch15_exclusion_log.csv`

## Summary

This batch opens the next P0/P1 source-discovery slice after batch14 moved its
blocked candidates into a manual approval queue. Stronger candidates include
中南林业科技大学 exact Guangxi plan page, 青海大学 2025招生计划 page,
长江大学/湖北大学/太原理工 official plan PDFs, and several official plan
portals that still need exact detail caching.

No row is parsed or eligible for reference_trend_pool/canonical/ML in this run.
