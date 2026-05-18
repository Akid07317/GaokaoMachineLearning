# Reference Trend 520 Batch4 Source Packet Parse

Run time: 2026-05-16T15:08:41

## Result

- Parse preview rows: 99
- GXUST group-structure rows: 12 (8 regular physical groups)
- KMUST Guangxi score/rank rows: 55 (52 physical)
- UJS Guangxi score rows: 31 (16 ordinary physical)
- Hold / exclusion rows: 23
- Reference trend eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry: closed

## Boundary

GXUST has official group structure but no score/rank or plan counts. KMUST has official score/rank by major but no Guangxi group code; its plan PDF needs column alignment before plan-count rows can be expanded. UJS has official major-level scores and admission counts but no rank or group code. These are useful source-packet/mapping assets, not final group-year records.

## Next Step

Next automation should join GXUST group codes with Guangxi exam-authority 2025 group lines, then use KMUST/UJS score rows as mapping QA evidence. If no safe local join exists, continue P0/P1 official source discovery.
