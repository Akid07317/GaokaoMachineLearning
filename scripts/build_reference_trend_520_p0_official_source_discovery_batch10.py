#!/usr/bin/env python3
"""Write batch-10 official source discovery preview for P0 queue rows.

This batch records official pages/assets discovered around queue ranks 63-75.
It stays in reference-trend source-packet/preview layers only.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch10_official"

OUT = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch10_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch10_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch10_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_official_source_discovery_batch10_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_official_source_discovery_batch10.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

FIELDS = [
    "source_id",
    "queue_record_id",
    "queue_rank",
    "source_url",
    "source_owner",
    "source_title",
    "published_date",
    "year",
    "province",
    "batch",
    "subject_category",
    "round_type",
    "university_name",
    "university_code",
    "source_role",
    "source_contains_group_code",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_contains_plan_count",
    "special_type_detected",
    "raw_file_path",
    "collector_note",
    "collector_confidence",
    "source_packet_status",
    "intended_layer",
    "requires_network",
    "requires_manual_approval",
    "eligible_for_intake_preview",
    "next_action",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "record_id",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def cached(path: Path) -> str:
    return rel(path) if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def common(row: dict[str, object], idx: int) -> dict[str, object]:
    enriched = {
        "source_id": f"reference_trend_520_p0_batch10_{idx:04d}",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "intended_layer": "reference_trend_source_packet_preview_only",
        "requires_network": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "record_id": f"reference_trend_520_p0_batch10_{idx:04d}",
    }
    enriched.update(row)
    return enriched


def build_rows() -> list[dict[str, object]]:
    tjfsu_files = "|".join(
        path
        for path in [
            cached(RAW_DIR / "tjfsu_2025_charter.html"),
            cached(RAW_DIR / "tjfsu_plan_index.html"),
        ]
        if path
    )
    rows = [
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0063",
            "queue_rank": "63",
            "university_code": "10636",
            "university_name": "四川师范大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "official_source_not_found_in_web_pass",
            "source_role": "no_first_party_plan_source_found",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "",
            "raw_file_path": "",
            "collector_note": "This pass did not find a first-party 2025 Guangxi ordinary physical plan table/PDF suitable for source-packet intake.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "eligible_for_intake_preview": "false",
            "next_action": "retry targeted first-party search or keep exam-authority score/rank only until official plan source appears",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0065",
            "queue_rank": "65",
            "university_code": "13212",
            "university_name": "大连医科大学中山学院",
            "source_url": "https://recruit.dmuzs.edu.cn/NewsDetail/5973426.html",
            "source_owner": "大连医科大学中山学院招生网",
            "source_title": "大连医科大学中山学院2025年本科分省分专业招生计划",
            "published_date": "",
            "round_type": "official_plan_page_tls_blocked",
            "source_role": "official_plan_page_candidate_reachability_blocked",
            "source_contains_group_code": "unknown_until_cached",
            "source_contains_plan_count": "true_in_search_snippet_unparsed",
            "special_type_detected": "independent college/private college boundary; ordinary plan rows need source parse",
            "raw_file_path": "",
            "collector_note": "First-party plan URL was identified, but terminal cache failed with certificate verification error. Kept in reachability/backoff; no unsafe TLS bypass was used.",
            "collector_confidence": "T2_official_plan_candidate_tls_blocked_not_cached",
            "source_packet_status": "official_plan_page_tls_blocked_not_cached",
            "eligible_for_intake_preview": "false_until_official_page_cached",
            "next_action": "retry with approved browser/certificate-audited route or locate alternate first-party copy",
            "requires_manual_approval": "true_for_tls_bypass_or_browser_retry",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0067",
            "queue_rank": "67",
            "university_code": "10068",
            "university_name": "天津外国语大学",
            "source_url": "https://zsb.tjfsu.edu.cn/zsjh.htm",
            "source_owner": "天津外国语大学招生网",
            "source_title": "招生计划栏目 + 2025年普通本科招生章程",
            "published_date": "",
            "round_type": "official_charter_and_plan_index_context_only",
            "source_role": "official_context_not_structured_plan_rows",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "language university; major-language limits may matter if later parsed",
            "raw_file_path": tjfsu_files,
            "collector_note": "Official charter and plan index were cached. The plan index did not expose structured 2025 Guangxi rows in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_charter_plan_index_cached_no_structured_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "inspect plan index pagination/endpoints or find official province plan attachment",
            "requires_manual_approval": "true_if_form_or_browser_replay_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0068",
            "queue_rank": "68",
            "university_code": "10068",
            "university_name": "天津外国语大学",
            "source_url": "https://zsb.tjfsu.edu.cn/zsjh.htm",
            "source_owner": "天津外国语大学招生网",
            "source_title": "招生计划栏目 + 2025年普通本科招生章程",
            "published_date": "",
            "round_type": "official_charter_and_plan_index_context_only",
            "source_role": "same_source_packet_as_queue_rank_67",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "raw_file_path": tjfsu_files,
            "collector_note": "Same official context packet as rank 67. No structured Guangxi plan rows exposed in this pass.",
            "collector_confidence": "T3_official_context_only_no_guangxi_plan_rows",
            "source_packet_status": "official_charter_plan_index_cached_no_structured_rows",
            "eligible_for_intake_preview": "false",
            "next_action": "deduplicate with queue rank 67 during endpoint/form investigation",
            "requires_manual_approval": "true_if_form_or_browser_replay_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0070",
            "queue_rank": "70",
            "university_code": "10752",
            "university_name": "宁夏医科大学",
            "source_url": "https://www.nxmu.edu.cn/zsxxw/info/1049/2714.htm",
            "source_owner": "宁夏医科大学招生信息网",
            "source_title": "宁夏医科大学2025年普通本专科招生分省分专业计划表",
            "published_date": "",
            "round_type": "official_pdf_plan_cached_unparsed",
            "source_role": "official_pdf_plan_candidate_needs_parse",
            "source_contains_group_code": "unknown_until_pdf_parse",
            "source_contains_plan_count": "true_in_pdf_unparsed",
            "special_type_detected": "PDF may mix 本科/专科 and province rows; filter to 广西/本科普通批/物理类",
            "raw_file_path": "|".join(
                p
                for p in [
                    cached(RAW_DIR / "nxmu_2025_plan_page.html"),
                    cached(RAW_DIR / "nxmu_2025_plan.pdf"),
                ]
                if p
            ),
            "collector_note": "Official plan page and attached PDF were cached. Local environment has no pdftotext/PDF parser available in this pass, so rows remain unparsed.",
            "collector_confidence": "T2_official_pdf_plan_candidate_needs_parse",
            "source_packet_status": "official_pdf_plan_cached_not_parsed",
            "eligible_for_intake_preview": "false_until_pdf_rows_are_extracted",
            "next_action": "parse PDF or use official image/PDF extraction; keep score/rank-only until plan/group rows are verified",
            "requires_manual_approval": "false_for_cached_pdf_parse; true_if_ocr_or_browser_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0071",
            "queue_rank": "71",
            "university_code": "10749",
            "university_name": "宁夏大学",
            "source_url": "http://zscx.nxu.edu.cn/zsw/zsjh.html",
            "source_owner": "宁夏大学本科招生网/招生查询系统",
            "source_title": "宁夏大学招生计划查询入口",
            "published_date": "",
            "round_type": "official_parameterized_plan_portal",
            "source_role": "official_plan_portal_parameterized_candidate",
            "source_contains_group_code": "unknown_until_parameter_drilldown",
            "source_contains_plan_count": "conditional_after_parameter_or_api_drilldown",
            "special_type_detected": "system may include ordinary/special rows; isolate once parameters are known",
            "raw_file_path": "|".join(
                p
                for p in [
                    cached(RAW_DIR / "nxu_plan_portal.html"),
                    cached(RAW_DIR / "nxu_charter.html"),
                ]
                if p
            ),
            "collector_note": "Official plan portal and 2025 charter baseline were cached. Portal parameter/API drilldown is still required for 广西/物理类 rows.",
            "collector_confidence": "T2_official_parameterized_plan_portal_needs_drilldown",
            "source_packet_status": "official_plan_portal_found_parameterized_not_parsed",
            "eligible_for_intake_preview": "false_until_guangxi_physics_rows_are_extracted",
            "next_action": "drill down portal/API for 广西 2025 物理类; hold if form/browser state is required",
            "requires_manual_approval": "true_if_form_or_browser_replay_needed",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0072",
            "queue_rank": "72",
            "university_code": "10361",
            "university_name": "安徽理工大学",
            "source_url": "https://zs.aust.edu.cn/info/1209/4579.htm",
            "source_owner": "安徽理工大学招生网",
            "source_title": "安徽理工大学2025年招生计划官方候选",
            "published_date": "",
            "round_type": "official_candidate_404",
            "source_role": "official_plan_candidate_not_cached",
            "source_contains_group_code": "unknown_until_cached",
            "source_contains_plan_count": "unknown_until_cached",
            "special_type_detected": "",
            "raw_file_path": "",
            "collector_note": "Official-domain candidate appeared in web search, but direct cache attempt returned 404. Kept as failed candidate, not accepted as data.",
            "collector_confidence": "T3_official_candidate_404_not_cached",
            "source_packet_status": "official_plan_candidate_404_not_cached",
            "eligible_for_intake_preview": "false",
            "next_action": "retry official-domain search for current URL/list page or use exam-authority score/rank only",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0073",
            "queue_rank": "73",
            "university_code": "10445",
            "university_name": "山东师范大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "official_source_not_found_in_web_pass",
            "source_role": "no_first_party_plan_source_found",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "",
            "raw_file_path": "",
            "collector_note": "This pass did not find a first-party 2025 Guangxi ordinary physical plan table/PDF suitable for source-packet intake.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "eligible_for_intake_preview": "false",
            "next_action": "retry targeted official-domain search; deduplicate with rank 74",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0074",
            "queue_rank": "74",
            "university_code": "10445",
            "university_name": "山东师范大学",
            "source_url": "",
            "source_owner": "",
            "source_title": "",
            "published_date": "",
            "round_type": "official_source_not_found_in_web_pass",
            "source_role": "same_no_source_result_as_queue_rank_73",
            "source_contains_group_code": "false",
            "source_contains_plan_count": "false",
            "special_type_detected": "same school has multiple Guangxi group rows in queue",
            "raw_file_path": "",
            "collector_note": "Same no-source finding as rank 73. No accepted first-party Guangxi plan source in this batch.",
            "collector_confidence": "T4_no_first_party_guangxi_plan_source_found",
            "source_packet_status": "no_official_source_found_in_batch",
            "eligible_for_intake_preview": "false",
            "next_action": "retry targeted official-domain search; deduplicate with rank 73",
            "requires_manual_approval": "false",
        },
        {
            "queue_record_id": "reference_trend_520_plan_source_queue_0075",
            "queue_rank": "75",
            "university_code": "14100",
            "university_name": "山东政法学院",
            "source_url": "https://zs.sdupsl.edu.cn/info/1006/8552.htm",
            "source_owner": "山东政法学院招生信息网",
            "source_title": "2025年普通高考招生计划",
            "published_date": "",
            "round_type": "official_image_plan_page_cached",
            "source_role": "official_guangxi_image_plan_candidate_needs_ocr",
            "source_contains_group_code": "unknown_image_not_ocrd",
            "source_contains_plan_count": "true_in_image_unparsed",
            "special_type_detected": "page includes province images and may include本科/专科; filter Guangxi image before use",
            "raw_file_path": "|".join(
                p
                for p in [
                    cached(RAW_DIR / "sdupsl_2025_plan.html"),
                    cached(RAW_DIR / "sdupsl_2025_plan_alt.html"),
                ]
                if p
            ),
            "collector_note": "Official plan page was cached and contains an embedded Guangxi image block. OCR/image extraction is not performed in this batch.",
            "collector_confidence": "T2_official_image_plan_candidate_needs_ocr_or_image_parse",
            "source_packet_status": "official_image_plan_page_cached_not_ocrd",
            "eligible_for_intake_preview": "false_until_image_rows_are_extracted_and_mapped",
            "next_action": "extract Guangxi embedded image or locate text/PDF source; hold group-year calibration",
            "requires_manual_approval": "true_if_browser_image_capture_or_ocr_needed",
        },
    ]
    return [common(row, idx) for idx, row in enumerate(rows, start=1)]


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    universities = sorted({str(row["university_name"]) for row in rows if row.get("university_name")})
    manual_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    rollup = [
        {"metric": "batch10_candidate_rows", "value": len(rows), "note": ""},
        {"metric": "queue_ranks_covered", "value": ",".join(str(row["queue_rank"]) for row in rows), "note": ""},
        {"metric": "universities_covered", "value": len(universities), "note": "|".join(universities)},
        {"metric": "requires_manual_approval_rows", "value": len(manual_rows), "note": "|".join(str(row["university_name"]) for row in manual_rows)},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "Discovery/source-packet preview only."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No group-year calibration opened."},
        {"metric": "canonical_ml_entry_open", "value": "false", "note": ""},
        {"metric": "decision_pool_expansion_performed", "value": "false", "note": ""},
    ]
    for key, count in sorted(Counter(str(row["collector_confidence"]) for row in rows).items()):
        rollup.append({"metric": f"collector_confidence::{key}", "value": count, "note": ""})
    for key, count in sorted(Counter(str(row["source_packet_status"]) for row in rows).items()):
        rollup.append({"metric": f"source_packet_status::{key}", "value": count, "note": ""})
    return rollup


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    accepted_source_rows = [
        row
        for row in rows
        if row.get("source_url")
        or row.get("source_packet_status") == "no_official_source_found_in_batch"
    ]
    return [
        {
            "qa_check": "rows_are_official_or_explicit_no_source_backoff",
            "status": "pass" if len(accepted_source_rows) == len(rows) else "warn",
            "value": len(accepted_source_rows),
            "note": "Rows are official first-party URLs, official-domain reachability/backoff, or explicit no-first-party-source findings.",
        },
        {
            "qa_check": "cached_raw_source_rows",
            "status": "pass",
            "value": sum(1 for row in rows if row.get("raw_file_path")),
            "note": "Rows with raw_file_path have locally cached official pages/assets.",
        },
        {
            "qa_check": "canonical_ml_entry",
            "status": "pass",
            "value": "closed",
            "note": "No canonical/ML write.",
        },
        {
            "qa_check": "decision_pool_boundary",
            "status": "pass",
            "value": "closed",
            "note": "No merge into the 32-school decision_pool.",
        },
    ]


def build_exclusions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "queue_rank": row["queue_rank"],
            "university_name": row["university_name"],
            "source_url": row["source_url"],
            "raw_file_path": row.get("raw_file_path", ""),
            "exclusion_reason": row["source_packet_status"],
            "recommended_next_action": row["next_action"],
            "canonical_ml_entry_open": "false",
        }
        for row in rows
        if row["source_packet_status"] != "ready_for_source_packet_parse"
    ]


def write_doc(rows: list[dict[str, object]]) -> None:
    cached_rows = [row for row in rows if row.get("raw_file_path")]
    manual_rows = [row for row in rows if str(row.get("requires_manual_approval", "")).startswith("true")]
    text = f"""# Reference Trend 520 P0 Official Source Discovery Batch 10

Generated: {date.today().isoformat()}

## Scope

This batch covers P0 plan-source queue rows around queue ranks 63-75. It stays in `reference_trend_source_packet_preview_only`; it does not write canonical/ML inputs and does not merge anything into the 32-school decision pool.

## Outputs

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch10_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_exclusion_log.csv`

## Key Findings

- Candidate rows: {len(rows)}
- Queue ranks covered: {', '.join(str(row['queue_rank']) for row in rows)}
- Universities covered: {len({row['university_name'] for row in rows})}
- Rows with cached official pages/assets: {len(cached_rows)}
- Manual approval / browser-form-OCR boundaries: {len(manual_rows)} ({'、'.join(sorted({row['university_name'] for row in manual_rows})) if manual_rows else 'none'})

High-value cached rows:

1. 宁夏医科大学: official 2025 plan page and attached PDF cached; PDF plan rows still need parsing.
2. 宁夏大学: official parameterized plan portal and 2025 charter baseline cached; portal/API drilldown still needed.
3. 山东政法学院: official 2025 plan page cached with embedded Guangxi image; OCR/image extraction needed.
4. 天津外国语大学: official charter and plan index cached, but no structured Guangxi plan rows exposed.

Held/backoff rows:

- 大连医科大学中山学院: first-party plan page found, but terminal cache failed on certificate verification; kept in TLS reachability/backoff.
- 安徽理工大学: official-domain candidate returned 404 on cache attempt.
- 四川师范大学、山东师范大学: no accepted first-party Guangxi plan source found in this pass.

## Boundary

`reference_trend_pool_eligible=0`, `calibration_eligible=0`, `canonical_ml_entry_open=false`. Next safe step is to parse 宁夏医科大学 PDF if a PDF parser is available, or continue official-source discovery from the next uncovered P0 rows.
"""
    DOC_OUT.write_text(text, encoding="utf-8")


def write_handoff(rows: list[dict[str, object]]) -> None:
    marker = "## 42. 2026-05-16 P0 官方来源发现 batch 10"
    content = f"""

{marker}

已新增 batch10 官方来源发现预览：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p0_official_source_discovery_batch10_preview.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_rollup.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_qa.csv`
- `reports/reference_trend_520_p0_official_source_discovery_batch10_exclusion_log.csv`
- `docs/reference_trend_520_p0_official_source_discovery_batch10.md`

覆盖结果：queue rank {', '.join(str(row['queue_rank']) for row in rows)}。宁夏医科大学官方计划页和 PDF 已缓存但未解析；宁夏大学官方计划查询系统入口和章程已缓存但需要参数/API drilldown；山东政法学院官方计划页已缓存，广西计划在嵌入图片中，需要 OCR/图片解析；天津外国语大学官方章程和计划栏目已缓存但未暴露结构化广西计划行。大连医科大学中山学院官方计划页遇到 TLS 证书阻塞，安徽理工大学官方候选页 404，四川师范大学/山东师范大学本轮未找到可接收的一方广西计划源。

准入边界：本轮只生成 source-packet discovery preview，`reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。下一轮优先解析宁夏医科大学 PDF（若可用 PDF parser），或推进下一个 P0 官方来源发现批次。
"""
    append_handoff_once(marker, content)


def main() -> None:
    rows = build_rows()
    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, build_rollup(rows), ["metric", "value", "note"])
    write_csv(QA_OUT, build_qa(rows), ["qa_check", "status", "value", "note"])
    write_csv(
        EXCLUSION_OUT,
        build_exclusions(rows),
        [
            "record_id",
            "queue_rank",
            "university_name",
            "source_url",
            "raw_file_path",
            "exclusion_reason",
            "recommended_next_action",
            "canonical_ml_entry_open",
        ],
    )
    write_doc(rows)
    write_handoff(rows)

    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    print(f"wrote {ROLLUP_OUT.relative_to(ROOT)}")
    print(f"wrote {QA_OUT.relative_to(ROOT)}")
    print(f"wrote {EXCLUSION_OUT.relative_to(ROOT)}")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
