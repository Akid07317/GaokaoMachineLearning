#!/usr/bin/env python3
"""Build a source-identity repair preview for Huabei Dianli D2/G2 P0 row fix."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"

QUEUE = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_queue_merged.csv"
PLAN = SEED_DIR / "huabei_dianli_guangxi_plan_physics.csv"
SCORE_SUMMARY = SEED_DIR / "huabei_dianli_guangxi_score_summary_physics.csv"
SCORE_MAJOR = SEED_DIR / "huabei_dianli_guangxi_score_major_physics.csv"

REPAIR_ROWS = SEED_DIR / "huabei_dianli_source_identity_fix_row_preview.csv"
STATUS_PREVIEW = SEED_DIR / "guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv"
SCHOOL_SUMMARY = REPORT_DIR / "engineering_pre_ml_d2_g2_huabei_source_identity_fix_school_summary.csv"
ROLLUP = REPORT_DIR / "engineering_pre_ml_d2_g2_huabei_source_identity_fix_coverage_rollup.csv"

SCHOOL_KEY = "huabei_dianli_211"
SCHOOL_NAME = "华北电力大学"
PLACEHOLDER_PREFIX = "http://www.yoursite.com/"
OFFICIAL_PREFIX = "https://goto.ncepu.edu.cn/"
PLAN_PAGE = "https://goto.ncepu.edu.cn/zsjh/index.htm"
SCORE_PAGE = "https://goto.ncepu.edu.cn/wnfs/index.htm"
PLAN_PAYLOAD = "https://goto.ncepu.edu.cn/common/plan_json.json"
SCORE_SUMMARY_PAYLOAD = "https://goto.ncepu.edu.cn/common/aii_json.json"
SCORE_MAJOR_PAYLOAD = "https://goto.ncepu.edu.cn/common/major_json.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def candidate_detail_url(url: str) -> str:
    if url.startswith(PLACEHOLDER_PREFIX):
        return OFFICIAL_PREFIX + url.removeprefix(PLACEHOLDER_PREFIX)
    return url


def repair_row(source_table: str, source_kind: str, row: dict[str, str]) -> dict[str, object]:
    if source_kind == "plan":
        official_page = PLAN_PAGE
        official_payload = PLAN_PAYLOAD
    elif source_kind == "score_summary":
        official_page = SCORE_PAGE
        official_payload = SCORE_SUMMARY_PAYLOAD
    else:
        official_page = SCORE_PAGE
        official_payload = SCORE_MAJOR_PAYLOAD

    original_url = row.get("source_url", "")
    placeholder_detected = original_url.startswith(PLACEHOLDER_PREFIX)
    return {
        "school_key": SCHOOL_KEY,
        "school_name": SCHOOL_NAME,
        "source_table": source_table,
        "source_kind": source_kind,
        "year": row.get("year", ""),
        "province": row.get("province", ""),
        "type": row.get("type", ""),
        "science_category": row.get("science_category", ""),
        "major": row.get("major", ""),
        "record_id": row.get("record_id", ""),
        "source_url_original": original_url,
        "placeholder_detected": str(placeholder_detected).lower(),
        "official_page_url": official_page,
        "official_payload_url": official_payload,
        "candidate_detail_url": candidate_detail_url(original_url),
        "repair_status": "official_payload_backed_detail_url_inferred" if placeholder_detected else "no_placeholder_detected",
        "repair_confidence": "medium_payload_verified_locally_detail_inferred" if placeholder_detected else "high",
        "repair_note": "本地缓存页面明示官方 JSON payload；detail URL 仅做域名模式推断，复核材料优先引用官方 page/payload。",
    }


def build_repair_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source_table, source_kind, path in [
        ("huabei_dianli_guangxi_plan_physics.csv", "plan", PLAN),
        ("huabei_dianli_guangxi_score_summary_physics.csv", "score_summary", SCORE_SUMMARY),
        ("huabei_dianli_guangxi_score_major_physics.csv", "score_major", SCORE_MAJOR),
    ]:
        for row in read_csv(path):
            rows.append(repair_row(source_table, source_kind, row))
    return rows


def build_status_preview(queue_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in queue_rows:
        preview = dict(row)
        if row.get("school_key") == SCHOOL_KEY:
            preview["fix_queue_status"] = "source_identity_fix_preview_ready"
            preview["fix_priority"] = "P0_source_identity_fix_preview_ready"
            preview["fix_class"] = "official_payload_urls_identified|detail_urls_inferred_not_network_verified"
            preview["recommended_action"] = (
                "复核时引用官方入口页和 JSON payload；如必须保留逐行 detail URL，先人工/联网验证 goto.ncepu.edu.cn 路径。"
            )
            preview["fix_route"] = "official_payload_reference_ready_detail_url_verify_optional"
            preview["exit_condition"] = "can_reassess_g2_after_payload_url_replacement_or_manual_detail_url_verification"
            preview["plan_source_url"] = f"{PLAN_PAGE}|{PLAN_PAYLOAD}"
            preview["score_source_url"] = f"{SCORE_PAGE}|{SCORE_SUMMARY_PAYLOAD}|{SCORE_MAJOR_PAYLOAD}"
            preview["required_row_fixes"] = "payload_source_url_replacement_ready|detail_url_manual_verification_optional|trend_missing_or_unverified"
            preview["ml_boundary_note"] = "source identity fix preview only; canonical/ML remain closed"
            preview["record_id"] = f"{SCHOOL_KEY}-d2-g2-request-row-fix-status-preview"
            preview["source_slug"] = "pre_ml_d2_g2_request_row_fix_status_preview"
        else:
            preview["record_id"] = f"{row['school_key']}-d2-g2-request-row-fix-status-preview"
            preview["source_slug"] = "pre_ml_d2_g2_request_row_fix_status_preview"
        output.append(preview)
    return output


def main() -> None:
    queue_rows = read_csv(QUEUE)
    repair_rows = build_repair_rows()
    status_preview = build_status_preview(queue_rows)

    repair_fields = [
        "school_key",
        "school_name",
        "source_table",
        "source_kind",
        "year",
        "province",
        "type",
        "science_category",
        "major",
        "record_id",
        "source_url_original",
        "placeholder_detected",
        "official_page_url",
        "official_payload_url",
        "candidate_detail_url",
        "repair_status",
        "repair_confidence",
        "repair_note",
    ]
    write_csv(REPAIR_ROWS, repair_rows, repair_fields)
    write_csv(STATUS_PREVIEW, status_preview, list(queue_rows[0].keys()))

    counts = Counter(row["source_kind"] for row in repair_rows)
    placeholders = sum(1 for row in repair_rows if row["placeholder_detected"] == "true")
    official_payloads = sorted({str(row["official_payload_url"]) for row in repair_rows})
    summary_rows = [
        {
            "school_key": SCHOOL_KEY,
            "school_name": SCHOOL_NAME,
            "fix_status": "source_identity_fix_preview_ready",
            "plan_official_page": PLAN_PAGE,
            "plan_official_payload": PLAN_PAYLOAD,
            "score_official_page": SCORE_PAGE,
            "score_summary_official_payload": SCORE_SUMMARY_PAYLOAD,
            "score_major_official_payload": SCORE_MAJOR_PAYLOAD,
            "row_level_preview_rows": len(repair_rows),
            "placeholder_url_rows": placeholders,
            "plan_rows": counts["plan"],
            "score_summary_rows": counts["score_summary"],
            "score_major_rows": counts["score_major"],
            "repair_decision": "replace source evidence with official page/payload URLs; keep inferred detail URLs out of canonical until verified",
            "ml_boundary_note": "canonical/ML remain closed",
        }
    ]
    summary_fields = [
        "school_key",
        "school_name",
        "fix_status",
        "plan_official_page",
        "plan_official_payload",
        "score_official_page",
        "score_summary_official_payload",
        "score_major_official_payload",
        "row_level_preview_rows",
        "placeholder_url_rows",
        "plan_rows",
        "score_summary_rows",
        "score_major_rows",
        "repair_decision",
        "ml_boundary_note",
    ]
    write_csv(SCHOOL_SUMMARY, summary_rows, summary_fields)

    rollup_rows = [
        {"metric": "huabei_source_identity_fix_school_rows", "value": 1},
        {"metric": "row_level_repair_preview_rows", "value": len(repair_rows)},
        {"metric": "placeholder_url_rows", "value": placeholders},
        {"metric": "official_payload_urls_identified", "value": len(official_payloads)},
        {"metric": "plan_rows", "value": counts["plan"]},
        {"metric": "score_summary_rows", "value": counts["score_summary"]},
        {"metric": "score_major_rows", "value": counts["score_major"]},
        {"metric": "detail_urls_still_need_network_or_manual_verification", "value": "true"},
        {"metric": "ml_boundary_still_closed", "value": "true"},
    ]
    write_csv(ROLLUP, rollup_rows, ["metric", "value"])

    print(f"row_level_repair_preview_rows={len(repair_rows)}")
    print(f"placeholder_url_rows={placeholders}")


if __name__ == "__main__":
    main()
