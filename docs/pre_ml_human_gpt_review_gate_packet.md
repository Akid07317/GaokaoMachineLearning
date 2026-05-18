# Pre-ML human/GPT review gate packet

本报告从全项目 action board 抽取 `ready_for_human_gpt_review_gate = true` 的学校，生成复核包和人工决策表。未联网，未运行 Deep Research，未写 canonical，未打开 ML。

## Coverage

- review gate packet 学校数：13
- clean bucket：10
- caution bucket：3
- decision sheet 待人工决策：13
- D2 row fix acceptance sheet：5
- canonical/ML 入口：关闭
- 扩池 / 非 211 搜索 / Deep Research 主线：关闭

## Clean bucket

- 北京交通大学招生与就业工作处：计划 109，最低分 609，最低位次 4541，趋势 rank_hotter
- 福州大学：计划 133，最低分 560，最低位次 20173，趋势 rank_cooler
- 华东理工大学本科招生网：计划 47，最低分 593，最低位次 7957，趋势 rank_cooler
- 南京理工大学本科招生信息网：计划 72，最低分 604，最低位次 5539，趋势 rank_cooler
- 武汉理工大学本科招生网：计划 258，最低分 592，最低位次 8451，趋势 rank_hotter
- 西南交通大学本科生招生信息公开：计划 164，最低分 578，最低位次 12990，趋势 rank_cooler
- 郑州大学：计划 115，最低分 546，最低位次 27014，趋势 rank_cooler
- 中国地质大学北京：计划 52，最低分 566，最低位次 17582，趋势 rank_cooler
- 河北工业大学：计划 37，最低分 546，最低位次 27014，趋势 trend_available_unclassified
- 太原理工大学：计划 482，最低分 522，最低位次 41040，趋势 trend_available_unclassified

## Caution bucket

- 河海大学：计划 0，最低分 583，最低位次 11210，备注 comparable_note_required|missing_plan|score_only_or_partial_plan
- 西安电子科技大学本科招生网：计划 135，最低分 592，最低位次 8483，备注 comparable_note_required|missing_trend|trend_missing_or_unverified
- 北京邮电大学本科招生网：计划 0，最低分 572，最低位次 15122，备注 missing_plan

## D2 row fix acceptance sheet

- 北京工业大学：P1_latest_plan_score_alignment_preview_ready / can_reassess_g2_with_no_2025_rank_caution
- 长安大学：P1_reference_year_and_field_mapping_preview_ready / can_reassess_g2_after_human_accepts_reference_year_note
- 合肥工业大学本科招生：P1_reference_year_and_field_mapping_preview_ready / can_reassess_g2_after_human_resolves_overview_vs_major_detail_and_rank_source
- 华北电力大学：P0_source_identity_fix_preview_ready / can_reassess_g2_after_payload_url_replacement_or_manual_detail_url_verification
- 南京航空航天大学招生网：P1_reference_year_and_field_mapping_preview_ready / can_reassess_g2_after_human_accepts_rank_derivation_and_line_candidate_boundary

## Boundary

- 复核包只用于人工/GPT 闸门确认。
- row fix acceptance sheet 只用于接受/驳回修复预览。
- 所有表都保留 manual decision columns；脚本重跑会保留人工填写内容。
- 禁止直接写 canonical/ML、扩池、非 211 搜索或把 Deep Research 当主线。

## Output files

- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_gate_packet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_human_gpt_review_gate_decision_sheet_merged.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_row_fix_acceptance_decision_sheet_merged.csv`
- `reports/engineering_pre_ml_human_gpt_review_gate_packet_coverage_rollup.csv`
- `reports/engineering_pre_ml_d2_row_fix_acceptance_decision_sheet_coverage_rollup.csv`
- `docs/pre_ml_human_gpt_review_gate_packet.md`
