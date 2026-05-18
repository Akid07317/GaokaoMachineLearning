# G4 official source reachability queue

D2/G2 request_row_fix 5 项已全部生成修复预览后，本轮按 post-gap-fill gate status 生成 G4 官方来源可达性队列。

## 结论

- G4 队列共 11 所学校。
- `P1_static_family_ready`：2 所，大连海事大学、哈尔滨工程大学本科招生。
- `P1_js_endpoint_exposed`：1 所，江南大学。
- `P2_cached_entry_waiting_headers`：3 所，北京科技大学本科招生网、中国矿业大学、中国石油大学北京。
- `P3_manual_review`：5 所，北京化工大学、中国石油大学华东、上海大学、中国地质大学武汉、中国矿业大学北京。
- Deep Research 只可作为官方来源可达性支线工具，不用于扩池、不用于非 211 搜索、不直接生成 ML/canonical 输入。
- ML/canonical 入口继续关闭。

## 下一步建议

优先处理 P1：

1. 大连海事大学、哈尔滨工程大学本科招生：从已缓存静态页或同家族脚本检查可抽取表格/API。
2. 江南大学：复核已暴露 JS/API endpoint 的参数和返回结构。
3. 之后再处理 P2 的 header/payload 路线审计。
4. P3 只记录官方入口、静态页、PDF、缓存页、403/header、表单 replay 或必须人工查证原因。

## 本轮产物

- `scripts/build_engineering_pre_ml_g4_source_reachability_queue.py`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_source_reachability_queue_merged.csv`
- `reports/engineering_pre_ml_g4_source_reachability_queue_coverage_rollup.csv`
