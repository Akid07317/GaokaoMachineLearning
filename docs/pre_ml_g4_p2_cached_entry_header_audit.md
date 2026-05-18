# G4 P2 缓存入口与 header 路线审计

本报告只汇总已缓存入口页、既有 ajax_family probe 日志和 static inventory；不联网、不 replay header/cookie、不写入 canonical/ML。

## 结论

- P2 审计学校数：3。
- 既有 probe 显示接口层 403 的学校：3 所。
- 已有 static inventory 的学校：1 所。
- 可从缓存 HTML 直接确认 endpoint 形状的学校：3 所。
- 三所均继续留在 G4 P2 source reachability branch；任何联网/header/cookie/browser 态动作都需要单独人工批准。

## 分校审计

### 北京科技大学本科招生网

- 预览状态：`cached_entry_html_endpoint_shape_confirmed_but_ajax_probe_403`。
- 候选 header 路线：`cached_html_endpoint_header_replay_candidate`。
- 缓存入口：3 个文件，78186 bytes。
- 缓存 endpoint：`f/newsCenter/ajax_get_category_and_link_list|f/ajax_zsjh_param|f/ajax_zsjh|f/ajax_zyjs_zy|f/ajax_lnfs_param|f/ajax_lnfs`。
- 字段证据：`nf|ssmc|zylx|zydhmc|klmc|zycc|zsjhs|remarks`。
- probe 摘要：rows=10，status=http_error:10，error=403。
- 下一步：先完成人工批准前的 header 路线审计；若要继续，只能单独申请联网/header/cookie/browser 态验证，不得直接进入 canonical/ML。

### 中国矿业大学

- 预览状态：`cached_entry_html_endpoint_shape_confirmed_but_ajax_probe_403`。
- 候选 header 路线：`cached_html_endpoint_header_replay_candidate`。
- 缓存入口：3 个文件，68344 bytes。
- 缓存 endpoint：`f/ajax_zsjh_param|f/ajax_zsjh|f/ajax_zyjs_zy|f/ajax_lnfs_param|f/ajax_lnfs|f/ajax_lqcx_param|servlet/validateCodeServlet`。
- 字段证据：`nf|ssmc|klmc|sex|campus|maxScore|minScore|yslkzx|yslwhcj|yslzhcj|yslzycj|zymc|zylx|zydhmc|zycc|zsjhs|remarks`。
- probe 摘要：rows=10，status=http_error:10，error=403。
- 下一步：先完成人工批准前的 header 路线审计；若要继续，只能单独申请联网/header/cookie/browser 态验证，不得直接进入 canonical/ML。

### 中国石油大学北京

- 预览状态：`static_inventory_and_cached_entry_confirmed_but_ajax_probe_403`。
- 候选 header 路线：`static_ajax_inventory_header_replay_candidate`。
- 缓存入口：3 个文件，75257 bytes。
- 缓存 endpoint：`f/newsCenter/ajax_get_category_and_link_list|f/ajax_zsjh_param|f/ajax_zsjh|f/ajax_zyjs_zy|f/ajax_lnfs_param|f/ajax_lnfs|f/newsCenter/ajax_lbt_list|f/newsCenter/ajax_movie_view|f/newsCenter/ajax_category_article_list`。
- 字段证据：`nf|ssmc|sex|campus|zylx|klmc|zycc|zsjhs|zydhmc|yslwhcj|yslzycj|yslzhcj|yslkzx|maxScore|maxOrder|avgScore|avgOrder|minScore|minOrder|zdx|zyzname|zymc|link|imageSrc`。
- probe 摘要：rows=10，status=http_error:10，error=403。
- 下一步：先完成人工批准前的 header 路线审计；若要继续，只能单独申请联网/header/cookie/browser 态验证，不得直接进入 canonical/ML。

## 产物

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p2_cached_entry_header_audit_preview_merged.csv`
- `reports/engineering_pre_ml_g4_p2_cached_entry_header_audit_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_g4_p2_cached_entry_header_audit.py`
