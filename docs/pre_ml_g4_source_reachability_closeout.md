# G4 来源可达性 closeout 与人工批准队列

本报告合并 P1/P2/P3 本地预览；不联网，不启用 Deep Research，不 replay header/cookie/form，不写入 canonical/ML。

## Closeout 结论

- G4 closeout 学校数：11。
- 需要 live source 人工批准：11 所。
- 需要 Deep Research 批准：4 所。
- 需要 header/cookie 批准：5 所。
- 需要 form replay 批准：1 所。
- 需要 browser/TLS 态批准：7 所。
- 可仅本地继续做解析预览：2 所。
- 进入 canonical/ML 的学校数：0。

## 人工批准队列

### 1. 大连海事大学

- 优先级：`A1_static_family_lowest_live_scope`。
- 批准类型：`header_cookie_or_browser_state_approval`。
- 当前阻塞：`ajax_header_cookie_403_blocked`。
- 批准范围：header/cookie replay against listed official endpoints; browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 2. 哈尔滨工程大学本科招生

- 优先级：`A1_static_family_lowest_live_scope`。
- 批准类型：`header_cookie_or_browser_state_approval`。
- 当前阻塞：`ajax_header_cookie_403_blocked`。
- 批准范围：header/cookie replay against listed official endpoints; browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 3. 北京科技大学本科招生网

- 优先级：`A2_header_cookie`。
- 批准类型：`header_cookie_or_browser_state_approval`。
- 当前阻塞：`ajax_header_cookie_403_blocked`。
- 批准范围：header/cookie replay against listed official endpoints; browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 4. 中国矿业大学

- 优先级：`A2_header_cookie`。
- 批准类型：`header_cookie_or_browser_state_approval`。
- 当前阻塞：`ajax_header_cookie_403_blocked`。
- 批准范围：header/cookie replay against listed official endpoints; browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 5. 中国石油大学北京

- 优先级：`A2_header_cookie`。
- 批准类型：`header_cookie_or_browser_state_approval`。
- 当前阻塞：`ajax_header_cookie_403_blocked`。
- 批准范围：header/cookie replay against listed official endpoints; browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 6. 江南大学

- 优先级：`A2_browser_tls`。
- 批准类型：`browser_or_tls_api_probe_approval`。
- 当前阻塞：`remote_probe_483_or_tls_blocked`。
- 批准范围：browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 7. 上海大学

- 优先级：`A2_form_high_risk`。
- 批准类型：`form_replay_or_state_token_approval`。
- 当前阻塞：`form_replay_or_state_token_blocked`。
- 批准范围：form/state-token replay audit only; browser-state/TLS verification。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 8. 北京化工大学

- 优先级：`A3_deep_research_or_manual_source`。
- 批准类型：`official_source_discovery_or_deep_research_approval`。
- 当前阻塞：`official_source_gap_or_discovery_needed`。
- 批准范围：Deep Research limited to official source reachability。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 9. 中国石油大学华东

- 优先级：`A3_deep_research_or_manual_source`。
- 批准类型：`official_source_discovery_or_deep_research_approval`。
- 当前阻塞：`official_source_gap_or_discovery_needed`。
- 批准范围：Deep Research limited to official source reachability。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 10. 中国地质大学武汉

- 优先级：`A3_deep_research_or_manual_source`。
- 批准类型：`official_source_discovery_or_deep_research_approval`。
- 当前阻塞：`weak_official_or_undergraduate_source_disambiguation`。
- 批准范围：Deep Research limited to official source reachability。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

### 11. 中国矿业大学北京

- 优先级：`A3_deep_research_or_manual_source`。
- 批准类型：`official_source_discovery_or_deep_research_approval`。
- 当前阻塞：`weak_official_or_undergraduate_source_disambiguation`。
- 批准范围：Deep Research limited to official source reachability。
- 禁止事项：pool expansion; non-211 discovery; direct canonical/ML writes; model training; unreviewed merged data

## 产物

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_source_reachability_closeout_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_g4_human_approval_queue_merged.csv`
- `reports/engineering_pre_ml_g4_source_reachability_closeout_coverage_rollup.csv`
- `reports/engineering_pre_ml_g4_human_approval_queue_coverage_rollup.csv`
- `scripts/build_engineering_pre_ml_g4_source_reachability_closeout.py`
