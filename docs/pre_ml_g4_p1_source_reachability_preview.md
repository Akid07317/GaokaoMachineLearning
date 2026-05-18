# G4 P1 官方来源可达性预览

本报告只汇总已缓存页面、已缓存 JS 和既有 probe 日志；不联网，不扩池，不写入 canonical/ML。

## 结论

- P1 预览学校数：3。
- 静态同家族页面已确认：2 所。
- JS/API endpoint 形状已确认：1 所。
- 远程 probe 仍受 403/483/TLS 或 cookie/header 问题阻塞：3 所。
- 当前结果只证明官方来源路线存在，不证明数据已可进入 canonical/ML。

## 分校预览

### 大连海事大学

- 队列路线：`P1_static_family_ready`。
- 预览状态：`static_family_structure_confirmed_but_remote_fetch_blocked`。
- 证据层：`cached_static_ajax_page_inventory`。
- 候选抽取路线：`static_ajax_family_parser_or_header_replay_route`。
- cached/probe 摘要：page_count=12，probe_rows=10，probe_status=http_error:10。
- 字段/接口证据：`f/ajax_lnfs_param|f/ajax_zsjh_param`。
- 下一步：保留为 G4 P1 来源可达性预览；若要继续抽取，先基于缓存页生成本地解析器，联网 header/cookie replay 需单独批准。

### 哈尔滨工程大学本科招生

- 队列路线：`P1_static_family_ready`。
- 预览状态：`static_family_structure_confirmed_but_remote_fetch_blocked`。
- 证据层：`cached_static_ajax_page_inventory`。
- 候选抽取路线：`static_ajax_family_parser_or_header_replay_route`。
- cached/probe 摘要：page_count=2，probe_rows=0，probe_status=no_recent_probe_rows。
- 字段/接口证据：`f/ajax_lnfs_param|f/ajax_zsjh_param`。
- 下一步：保留为 G4 P1 来源可达性预览；若要继续抽取，先基于缓存页生成本地解析器，联网 header/cookie replay 需单独批准。

### 江南大学

- 队列路线：`P1_js_endpoint_exposed`。
- 预览状态：`js_endpoint_shape_confirmed_but_remote_probe_blocked`。
- 证据层：`cached_frontend_js_and_probe_plan`。
- 候选抽取路线：`api_param_route_known_header_or_tls_blocked`。
- cached/probe 摘要：page_count=0，probe_rows=10，probe_status=http_error:9|url_error:1。
- 字段/接口证据：`/front/recruitmentPlan/getQuery|/front/artSpecializedSubjectCategory/getQueryFront|/front/specializedSubject/getIdNameList|/front/specializedSubject/getIdPidNameList|/front/nation/getAll|/front/fileUpload/upload|/front/specializedSubject/sign-up-specialty-list?uuid=|/front/recruitmentPlan/getQueryByYearAndProvinceIdWithRecruitmentPlan|/front/subject/getRecruitmentPlanQueryByYearAndProvinceId|/front/recruitmentPlan/getList|/front/recruitmentPlan/getProvinceQuery?year=|/front/recruitmentResult/queryResult|/front/recruitmentSignUpRecord/getList|/front/recruitmentSignUpRecord/queryResult|/front/recruitmentSignUpRecord/isRecruitmentSourceExist|/front/recruitmentSignUpRecord/isRecruitment|/front/recruitmentSignUpRecord/signUp|/front/enterSchool/getEnterSchool/|/front/recruitmentSignUpRecord/confirm-sign-up-record|/front/historyScore/getQuery|/front/historyScore/getList|/front/historyScore/getNotArtProvinceQuery?year=|/front/historyScore/getArtFrontList|/front/historyScore/getProvinceByYearAndArtSpecializedSubjectCategoryId|/front/recruitmentPlan/getQueryByYearAndProvinceIdWithOutArt|/front/subject/getQueryByYearAndProvinceIdNew|/front/historyScore/getExamModeByYearAndArtSpecializedSubjectCategoryId`。
- 下一步：保留为 G4 P1 来源可达性预览；下一步只审 header/TLS/浏览器态路线，不得直接写入 canonical/ML。

## 产物

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_p1_source_reachability_preview_merged.csv`
- `reports/engineering_pre_ml_g4_p1_source_reachability_preview_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_g4_p1_source_reachability_preview.py`
