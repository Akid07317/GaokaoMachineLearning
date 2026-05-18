# Pre-ML human/GPT review action board and gate closeout

本报告只合并本地已生成的 D1/G1、D2/G2、D3/D4、D2 row fix 和 G4 closeout 层；未联网，未运行 Deep Research，未 replay header/cookie/form/browser 态，也未打开 canonical/ML 入口。

## Coverage

- 主池学校数：32
- 可进入 human/GPT 复核闸门：13
- D2 row fix preview 待人工接受：5
- G4 live source approval 待批准：11
- D2 hold_before_ml：3
- canonical/ML 入口：0 所打开
- 扩池 / 非 211 搜索 / Deep Research 主线：全部关闭

## Gate buckets

- B1_ready_clean_review_gate: 10
- B2_ready_caution_review_gate: 3
- B3_row_fix_preview_requires_human_acceptance: 5
- B4_hold_before_ml: 3
- B5_g4_live_source_approval_required: 11

## Action statuses

- g4_hold_live_source_approval_required: 11
- gap_fill_application_ready_for_review_gate: 3
- hold_before_ml_from_d2_g2_review: 3
- review_gate_ready_caution_accepted: 2
- review_gate_ready_clean_accepted: 8
- row_fix_preview_ready_for_human_acceptance: 5

## Ready for human/GPT review gate

- 北京交通大学招生与就业工作处：B1_ready_clean_review_gate / accept_for_review_gate
- 福州大学：B1_ready_clean_review_gate / accept_for_review_gate
- 华东理工大学本科招生网：B1_ready_clean_review_gate / accept_for_review_gate
- 南京理工大学本科招生信息网：B1_ready_clean_review_gate / accept_for_review_gate
- 武汉理工大学本科招生网：B1_ready_clean_review_gate / accept_for_review_gate
- 西南交通大学本科生招生信息公开：B1_ready_clean_review_gate / accept_for_review_gate
- 郑州大学：B1_ready_clean_review_gate / accept_for_review_gate
- 中国地质大学北京：B1_ready_clean_review_gate / accept_for_review_gate
- 河北工业大学：B1_ready_clean_review_gate / accept_gap_fill_then_review
- 太原理工大学：B1_ready_clean_review_gate / accept_gap_fill_then_review
- 河海大学：B2_ready_caution_review_gate / accept_for_review_gate
- 西安电子科技大学本科招生网：B2_ready_caution_review_gate / accept_for_review_gate
- 北京邮电大学本科招生网：B2_ready_caution_review_gate / accept_gap_fill_with_note

## Row fix acceptance queue

- 北京工业大学：P1_latest_plan_score_alignment_preview_ready / can_reassess_g2_with_no_2025_rank_caution
- 长安大学：P1_reference_year_and_field_mapping_preview_ready / can_reassess_g2_after_human_accepts_reference_year_note
- 合肥工业大学本科招生：P1_reference_year_and_field_mapping_preview_ready / can_reassess_g2_after_human_resolves_overview_vs_major_detail_and_rank_source
- 华北电力大学：P0_source_identity_fix_preview_ready / can_reassess_g2_after_payload_url_replacement_or_manual_detail_url_verification
- 南京航空航天大学招生网：P1_reference_year_and_field_mapping_preview_ready / can_reassess_g2_after_human_accepts_rank_derivation_and_line_candidate_boundary

## G4 approval queue

- 大连海事大学：A1_static_family_lowest_live_scope / header_cookie_or_browser_state_approval / local_only=true
- 哈尔滨工程大学本科招生：A1_static_family_lowest_live_scope / header_cookie_or_browser_state_approval / local_only=true
- 江南大学：A2_browser_tls / browser_or_tls_api_probe_approval / local_only=false
- 上海大学：A2_form_high_risk / form_replay_or_state_token_approval / local_only=false
- 北京科技大学本科招生网：A2_header_cookie / header_cookie_or_browser_state_approval / local_only=false
- 中国矿业大学：A2_header_cookie / header_cookie_or_browser_state_approval / local_only=false
- 中国石油大学北京：A2_header_cookie / header_cookie_or_browser_state_approval / local_only=false
- 北京化工大学：A3_deep_research_or_manual_source / official_source_discovery_or_deep_research_approval / local_only=false
- 中国地质大学武汉：A3_deep_research_or_manual_source / official_source_discovery_or_deep_research_approval / local_only=false
- 中国矿业大学北京：A3_deep_research_or_manual_source / official_source_discovery_or_deep_research_approval / local_only=false
- 中国石油大学华东：A3_deep_research_or_manual_source / official_source_discovery_or_deep_research_approval / local_only=false

## Boundary

- 允许：逐校 human/GPT 复核、人工接受或驳回 D2 row fix preview、人工批准或驳回 G4 官方来源可达性支线。
- 禁止：扩充主数据池、非 211 搜索、把 G4 或 row fix preview 直接写入 canonical、启动模型训练。

## Output files

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_action_board_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_final_gate_closeout_merged.csv`
- `reports/engineering_pre_ml_human_gpt_review_action_board_coverage_rollup.csv`
- `reports/engineering_pre_ml_final_gate_closeout_coverage_rollup.csv`
- `docs/pre_ml_human_gpt_review_action_board_and_gate_closeout.md`
