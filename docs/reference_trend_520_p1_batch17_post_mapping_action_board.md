# P1 batch17 post-mapping action board

## Summary

本轮读取 marker 133/136/138/139 的本地产物，将 batch17 后续工作拆为 group action、coverage backoff 和 unique score-rank lookup target 三类。未联网、未缓存新页面、未 OCR、未打开浏览器/form/header/cookie/微信状态，也未选择最低位次。

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_post_mapping_action_board.csv`
- `reports/reference_trend_520_p1_batch17_post_mapping_action_board_rollup.csv`
- `reports/reference_trend_520_p1_batch17_post_mapping_action_board_qa.csv`
- `reports/reference_trend_520_p1_batch17_post_mapping_action_board_exclusion_log.csv`

## Rollup

- Group action rows: 15
- Coverage backoff rows: 5
- Unique score-rank lookup targets: 5
- Group rows with official min_score: 6
- Selected min_rank rows: 0
- Rows needing user approval or official raw artifact: 17

## Boundary

All rows keep `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false`. The board is for source-packet/QA workflow routing only and does not modify canonical, ML input, baseline data, or the 32-school decision pool.
