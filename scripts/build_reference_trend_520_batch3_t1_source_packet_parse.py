#!/usr/bin/env python3
"""Parse locally cached batch3 T1 official sources into source-packet previews.

This script only writes non-baseline, non-canonical, non-ML preview artifacts.
It keeps every parsed row out of the trend pool until group-code alignment and
special-type QA are resolved.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch3_t1"

BATCH3_PREVIEW = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch3_preview.csv"
PARSE_PREVIEW = SEED_DIR / "reference_trend_520_batch3_t1_source_packet_parse_preview.csv"
ROLLUP = REPORT_DIR / "reference_trend_520_batch3_t1_source_packet_parse_rollup.csv"
QA = REPORT_DIR / "reference_trend_520_batch3_t1_source_packet_parse_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_520_batch3_t1_source_packet_parse_exclusion_log.csv"
DOC = DOC_DIR / "reference_trend_520_batch3_t1_source_packet_parse.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._in_row = False
        self._in_cell = False
        self._row: list[str] = []
        self._cell: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag == "tr":
            self._in_row = True
            self._row = []
        elif tag in {"td", "th"} and self._in_row:
            self._in_cell = True
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            value = re.sub(r"\s+", " ", data)
            if value.strip():
                self._cell.append(value.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._in_cell:
            cell = " ".join(self._cell).strip()
            self._row.append(unescape(cell))
            self._cell = []
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if any(cell.strip() for cell in self._row):
                self.rows.append(self._row)
            self._row = []
            self._in_row = False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def parse_html_rows(path: Path) -> list[list[str]]:
    parser = TableParser()
    parser.feed(path.read_text(encoding="utf-8-sig", errors="replace"))
    return parser.rows


def source_meta_by_school(rows: list[dict[str, str]], school: str) -> dict[str, str]:
    for row in rows:
        if row.get("university_name") == school:
            return row
    return {}


def base_packet(
    *,
    record_id: str,
    source: dict[str, str],
    raw_file_path: Path,
    parser_dataset: str,
    source_role: str,
    major_or_group: str = "",
    major_code: str = "",
    plan_nature: str = "",
    admission_type: str = "",
    subject_category: str = "",
    batch: str = "",
    plan_count: str | int = "",
    special_type_detected: str = "",
    qa_status: str,
    required_resolution: str,
    evidence_note: str,
    collector_confidence: str = "T1_official_cached_parse_preview",
) -> dict[str, object]:
    return {
        "record_id": record_id,
        "source_id": source.get("source_id", ""),
        "source_url": source.get("source_url", ""),
        "source_owner": source.get("source_owner", ""),
        "source_title": source.get("source_title", ""),
        "raw_file_path": str(raw_file_path.relative_to(ROOT)),
        "parser_dataset": parser_dataset,
        "university_code": source.get("university_code", ""),
        "university_name": source.get("university_name", ""),
        "year": source.get("year", "2025"),
        "province": "广西",
        "batch": batch or source.get("batch", "本科普通批"),
        "subject_category": subject_category or source.get("subject_category", ""),
        "round_type": source.get("round_type", ""),
        "source_role": source_role,
        "major_or_group": major_or_group,
        "major_code": major_code,
        "plan_nature": plan_nature,
        "admission_type": admission_type,
        "plan_count": plan_count,
        "source_contains_group_code": "false",
        "source_contains_plan_count": "true" if str(plan_count).strip() not in {"", "0"} else "unknown",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "special_type_detected": special_type_detected,
        "qa_status": qa_status,
        "collector_confidence": collector_confidence,
        "intended_layer": "reference_trend_source_packet_parse_preview_only",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "reference_trend_only_not_32_school_decision_pool",
        "required_resolution": required_resolution,
        "evidence_note": evidence_note,
    }


def normalize_int(value: str) -> int:
    value = re.sub(r"[^\d-]", "", value or "")
    if not value or value == "-":
        return 0
    return int(value)


def parse_hrbmu(source: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    path = RAW_DIR / "hrbmu_2025_plan.html"
    rows = parse_html_rows(path)
    packets: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    qa_rows: list[dict[str, object]] = []

    header = rows[0] if rows else []
    gx_ordinary_idx = header.index("广西") if "广西" in header else 26
    # In this table, the column after Guangxi is the Guangxi national-special plan column.
    gx_national_special_idx = gx_ordinary_idx + 1

    ordinary_total = 0
    national_special_total = 0
    ordinary_physics_candidates = 0
    hold_rows = 0

    for idx, row in enumerate(rows[2:], start=1):
        if len(row) <= gx_ordinary_idx:
            continue
        major = row[0].strip()
        subject = row[2].strip() if len(row) > 2 else ""
        ordinary = normalize_int(row[gx_ordinary_idx])
        national_special = normalize_int(row[gx_national_special_idx]) if len(row) > gx_national_special_idx else 0
        if ordinary == 0 and national_special == 0:
            continue
        ordinary_total += ordinary
        national_special_total += national_special

        if ordinary:
            if subject == "理":
                status = "source_packet_ready_group_mapping_needed_legacy_subject_label"
                required = "map legacy science label and missing Guangxi group code before any trend intake"
                subject_category = "物理类_candidate_from_legacy_li"
                ordinary_physics_candidates += 1
            else:
                status = "non_physics_or_legacy_wen_hold"
                required = "exclude legacy liberal-arts rows from physical reference trend intake"
                subject_category = "历史类_or_legacy_wen_hold"
                hold_rows += 1
            packet = base_packet(
                record_id=f"reference_trend_520_batch3_t1_hrbmu_parse_{idx:04d}",
                source=source,
                raw_file_path=path,
                parser_dataset="hrbmu_2025_guangxi_column",
                source_role="official_html_plan_row",
                major_or_group=major,
                plan_nature="ordinary_or_aggregate_guangxi_column",
                admission_type="ordinary_column",
                subject_category=subject_category,
                plan_count=ordinary,
                qa_status=status,
                required_resolution=required,
                evidence_note=f"HRBMU table Guangxi ordinary column count={ordinary}; source subject label={subject}; no Guangxi institution-major-group code.",
            )
            packets.append(packet)
            if status.endswith("_hold"):
                exclusions.append(packet)

        if national_special:
            packet = base_packet(
                record_id=f"reference_trend_520_batch3_t1_hrbmu_national_special_{idx:04d}",
                source=source,
                raw_file_path=path,
                parser_dataset="hrbmu_2025_guangxi_national_special_column",
                source_role="official_html_plan_row_special_hold",
                major_or_group=major,
                plan_nature="national_special",
                admission_type="国家专项",
                subject_category="物理类_candidate_from_legacy_li" if subject == "理" else "历史类_or_legacy_wen_hold",
                plan_count=national_special,
                special_type_detected="national_special",
                qa_status="special_type_hold_not_regular_batch",
                required_resolution="keep national-special plan rows isolated from undergraduate regular-batch trend pool",
                evidence_note=f"HRBMU adjacent Guangxi national-special column count={national_special}; source subject label={subject}.",
            )
            packets.append(packet)
            exclusions.append(packet)
            hold_rows += 1

    qa_rows.extend(
        [
            {
                "qa_check": "hrbmu_raw_file_present",
                "status": "pass" if path.exists() else "fail",
                "value": str(path.relative_to(ROOT)),
                "note": "Official HTML cached locally.",
            },
            {
                "qa_check": "hrbmu_guangxi_ordinary_total",
                "status": "pass" if ordinary_total == 37 else "review",
                "value": ordinary_total,
                "note": "Expected page-level Guangxi ordinary total is 37 in the table total row.",
            },
            {
                "qa_check": "hrbmu_guangxi_national_special_total",
                "status": "pass" if national_special_total == 13 else "review",
                "value": national_special_total,
                "note": "Expected adjacent Guangxi national-special total is 13 in the table total row.",
            },
            {
                "qa_check": "hrbmu_ordinary_physics_candidate_rows",
                "status": "info",
                "value": ordinary_physics_candidates,
                "note": "Rows still require missing Guangxi group-code mapping before intake.",
            },
        ]
    )
    metrics = {
        "hrbmu_html_table_rows": len(rows),
        "hrbmu_packet_rows": sum(1 for row in packets if row["parser_dataset"].startswith("hrbmu")),
        "hrbmu_ordinary_physics_candidate_rows": ordinary_physics_candidates,
        "hrbmu_hold_rows": hold_rows,
        "hrbmu_guangxi_ordinary_plan_total": ordinary_total,
        "hrbmu_guangxi_national_special_plan_total": national_special_total,
    }
    return packets, qa_rows, exclusions, metrics


def parse_gxnu(source: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    path = RAW_DIR / "gxnu_2025_guangxi_plan.html"
    rows = parse_html_rows(path)
    packets: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    qa_rows: list[dict[str, object]] = []

    data_rows = [row for row in rows if len(row) >= 9 and row[0].strip() == "2025"]
    ordinary_physics_count = 0
    ordinary_physics_plan_total = 0
    special_rows = 0

    for idx, row in enumerate(data_rows, start=1):
        year, major_code, major_name, plan_nature, admission_type, subject, batch, plan_count_raw, note = row[:9]
        plan_count = normalize_int(plan_count_raw)
        is_ordinary_physics = admission_type == "普通类" and subject == "物理类" and batch == "本科普通批"
        special = ""
        if admission_type in {"国家专项计划", "地方专项计划", "民族班"}:
            special = admission_type
        elif batch != "本科普通批" or subject != "物理类":
            special = "non_physics_or_non_regular_batch"

        if is_ordinary_physics:
            qa_status = "source_packet_ready_group_mapping_needed"
            required = "map missing Guangxi institution-major-group code before trend intake"
            ordinary_physics_count += 1
            ordinary_physics_plan_total += plan_count
        elif special in {"国家专项计划", "地方专项计划", "民族班"}:
            qa_status = "special_type_hold_not_regular_batch"
            required = "keep special-type plan rows isolated from regular-batch trend pool"
            special_rows += 1
        else:
            qa_status = "non_physics_or_non_regular_batch_hold"
            required = "exclude non-physical or non-regular-batch row from physical regular-batch trend pool"

        packet = base_packet(
            record_id=f"reference_trend_520_batch3_t1_gxnu_parse_{idx:04d}",
            source=source,
            raw_file_path=path,
            parser_dataset="gxnu_2025_guangxi_plan_table",
            source_role="official_html_plan_row",
            major_or_group=major_name,
            major_code=major_code,
            plan_nature=plan_nature,
            admission_type=admission_type,
            subject_category=subject,
            batch=batch,
            plan_count=plan_count,
            special_type_detected=special,
            qa_status=qa_status,
            required_resolution=required,
            evidence_note=f"GXNU official row: code={major_code}, type={admission_type}, subject={subject}, batch={batch}, plan={plan_count}, note={note}; no Guangxi group code.",
        )
        packets.append(packet)
        if qa_status != "source_packet_ready_group_mapping_needed":
            exclusions.append(packet)

    qa_rows.extend(
        [
            {
                "qa_check": "gxnu_raw_file_present",
                "status": "pass" if path.exists() else "fail",
                "value": str(path.relative_to(ROOT)),
                "note": "Official HTML cached locally.",
            },
            {
                "qa_check": "gxnu_2025_rows_parsed",
                "status": "info",
                "value": len(data_rows),
                "note": "Rows from official Guangxi 2025 plan table.",
            },
            {
                "qa_check": "gxnu_ordinary_physics_regular_rows",
                "status": "pass" if ordinary_physics_count == 53 else "review",
                "value": ordinary_physics_count,
                "note": "Expected previously observed ordinary physical regular-batch row count is 53.",
            },
            {
                "qa_check": "gxnu_ordinary_physics_regular_plan_total",
                "status": "pass" if ordinary_physics_plan_total == 2002 else "review",
                "value": ordinary_physics_plan_total,
                "note": "Expected previously observed ordinary physical regular-batch plan total is 2002.",
            },
        ]
    )
    metrics = {
        "gxnu_html_table_rows": len(rows),
        "gxnu_2025_rows_parsed": len(data_rows),
        "gxnu_packet_rows": len(packets),
        "gxnu_ordinary_physics_regular_rows": ordinary_physics_count,
        "gxnu_ordinary_physics_regular_plan_total": ordinary_physics_plan_total,
        "gxnu_special_hold_rows": special_rows,
    }
    return packets, qa_rows, exclusions, metrics


def extract_pdf_text(path: Path) -> tuple[str, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent.
        return "", f"pypdf_unavailable:{exc}"

    try:
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text, "pass"
    except Exception as exc:  # pragma: no cover - corrupt PDF dependent.
        return "", f"pdf_extract_failed:{exc}"


def parse_unnc(source: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    path = RAW_DIR / "unnc_2025_plan.pdf"
    text, status = extract_pdf_text(path)
    text_path = RAW_DIR / "unnc_2025_plan_text.txt"
    if text:
        text_path.write_text(text, encoding="utf-8")

    has_split_guangxi = bool(re.search(r"广\s*西", text))
    has_physics_rows = "理/物" in text
    packet = base_packet(
        record_id="reference_trend_520_batch3_t1_unnc_pdf_boundary_0001",
        source=source,
        raw_file_path=path,
        parser_dataset="unnc_2025_official_pdf_text_boundary",
        source_role="official_pdf_plan_table_boundary_hold",
        major_or_group="whole_pdf_table_boundary",
        admission_type="sino_foreign_university_boundary",
        subject_category="物理类_candidate_pdf_contains_liwu" if has_physics_rows else "unknown_pdf_text",
        plan_count="",
        special_type_detected="sino_foreign_university_boundary",
        qa_status="pdf_text_extracted_but_column_alignment_needed" if status == "pass" and text else "pdf_text_extract_failed_local_parser_hold",
        collector_confidence="T1_official_pdf_cached_text_boundary",
        required_resolution="manual PDF column alignment for Guangxi physics rows before source-packet row expansion",
        evidence_note=f"PDF text chars={len(text)}; Guangxi header detected={has_split_guangxi}; physics rows detected={has_physics_rows}; no direct Guangxi group code.",
    )
    qa_rows = [
        {
            "qa_check": "unnc_raw_pdf_present",
            "status": "pass" if path.exists() else "fail",
            "value": str(path.relative_to(ROOT)),
            "note": "Official PDF cached locally.",
        },
        {
            "qa_check": "unnc_pdf_text_extract",
            "status": status,
            "value": len(text),
            "note": f"Extracted text written to {text_path.relative_to(ROOT) if text else 'not_written'}",
        },
        {
            "qa_check": "unnc_pdf_guangxi_header_detected",
            "status": "pass" if has_split_guangxi else "review",
            "value": has_split_guangxi,
            "note": "pypdf extraction splits province names by line breaks, so detection uses a whitespace-tolerant pattern.",
        },
    ]
    metrics = {
        "unnc_pdf_text_chars": len(text),
        "unnc_pdf_guangxi_header_detected": int(has_split_guangxi),
        "unnc_pdf_physics_rows_detected": int(has_physics_rows),
        "unnc_packet_rows": 1,
        "unnc_manual_alignment_needed_rows": 1,
    }
    return [packet], qa_rows, [packet], metrics


def metric_rows(metrics: dict[str, object], packets: list[dict[str, object]], exclusions: list[dict[str, object]]) -> list[dict[str, object]]:
    status_counts = Counter(str(row["qa_status"]) for row in packets)
    out = [
        {"metric": key, "value": value, "note": ""}
        for key, value in sorted(metrics.items())
    ]
    out.extend(
        [
            {"metric": "parse_preview_rows", "value": len(packets), "note": "All rows are non-baseline source-packet parse preview rows."},
            {"metric": "exclusion_or_hold_rows", "value": len(exclusions), "note": "Rows kept out of reference trend pool pending exclusion, mapping, or manual alignment."},
            {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No parsed row opens trend pool intake without group-code alignment and QA."},
            {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan sources do not contain min score/rank and are not calibration records."},
            {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        ]
    )
    for status, count in sorted(status_counts.items()):
        out.append({"metric": f"qa_status::{status}", "value": count, "note": ""})
    return out


def append_handoff_once(section: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    marker = "## 19. 2026-05-16 batch3 T1 source packet parse"
    if marker in existing:
        updated = re.sub(r"## 19\. 2026-05-16 batch3 T1 source packet parse[\s\S]*$", section.strip() + "\n", existing)
    else:
        updated = existing.rstrip() + "\n\n" + section.strip() + "\n"
    HANDOFF.write_text(updated, encoding="utf-8")


def main() -> None:
    batch3_rows = read_csv(BATCH3_PREVIEW)
    packets: list[dict[str, object]] = []
    qa_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    metrics: dict[str, object] = {
        "batch3_source_candidates": len(batch3_rows),
        "run_timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    hrbmu_packets, hrbmu_qa, hrbmu_exclusions, hrbmu_metrics = parse_hrbmu(source_meta_by_school(batch3_rows, "哈尔滨医科大学"))
    gxnu_packets, gxnu_qa, gxnu_exclusions, gxnu_metrics = parse_gxnu(source_meta_by_school(batch3_rows, "广西师范大学"))
    unnc_packets, unnc_qa, unnc_exclusions, unnc_metrics = parse_unnc(source_meta_by_school(batch3_rows, "宁波诺丁汉大学"))

    for collection, extra in [
        (packets, hrbmu_packets + gxnu_packets + unnc_packets),
        (qa_rows, hrbmu_qa + gxnu_qa + unnc_qa),
        (exclusions, hrbmu_exclusions + gxnu_exclusions + unnc_exclusions),
    ]:
        collection.extend(extra)
    for extra in [hrbmu_metrics, gxnu_metrics, unnc_metrics]:
        metrics.update(extra)

    packet_fields = [
        "record_id",
        "source_id",
        "source_url",
        "source_owner",
        "source_title",
        "raw_file_path",
        "parser_dataset",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "round_type",
        "source_role",
        "major_or_group",
        "major_code",
        "plan_nature",
        "admission_type",
        "plan_count",
        "source_contains_group_code",
        "source_contains_plan_count",
        "source_contains_min_score",
        "source_contains_min_rank",
        "special_type_detected",
        "qa_status",
        "collector_confidence",
        "intended_layer",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]
    qa_fields = ["qa_check", "status", "value", "note"]

    write_csv(PARSE_PREVIEW, packets, packet_fields)
    write_csv(EXCLUSION, exclusions, packet_fields)
    write_csv(QA, qa_rows, qa_fields)
    write_csv(ROLLUP, metric_rows(metrics, packets, exclusions), ["metric", "value", "note"])

    ready_rows = sum(1 for row in packets if row["qa_status"] == "source_packet_ready_group_mapping_needed")
    legacy_ready_rows = sum(1 for row in packets if row["qa_status"] == "source_packet_ready_group_mapping_needed_legacy_subject_label")
    hold_rows = len(exclusions)
    doc = f"""# Reference Trend 520 Batch3 T1 Source Packet Parse

Run time: {metrics['run_timestamp']}

This is a non-baseline, non-canonical and non-ML parse layer for the locally cached T1 official sources from batch 3.

## Outputs

- `{PARSE_PREVIEW.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{RAW_DIR.relative_to(ROOT) / 'unnc_2025_plan_text.txt'}`

## Result

- Parsed preview rows: {len(packets)}
- Source-packet rows ready for group-code mapping: {ready_rows}
- Legacy science-label rows needing group-code and subject-label mapping: {legacy_ready_rows}
- Hold / exclusion rows: {hold_rows}
- Reference trend pool eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry open rows: 0

## Source Notes

- 哈尔滨医科大学: Guangxi ordinary column total {metrics['hrbmu_guangxi_ordinary_plan_total']} and adjacent national-special total {metrics['hrbmu_guangxi_national_special_plan_total']}; ordinary science rows are parsed, but the table uses legacy `理/文` labels and has no Guangxi院校专业组 code.
- 广西师范大学: parsed {metrics['gxnu_2025_rows_parsed']} Guangxi 2025 rows; ordinary physical regular-batch rows {metrics['gxnu_ordinary_physics_regular_rows']} with plan total {metrics['gxnu_ordinary_physics_regular_plan_total']}; no Guangxi院校专业组 code, so rows remain mapping workbench only.
- 宁波诺丁汉大学: official PDF text extracted to local text, but column alignment is not safe enough for row expansion; kept as whole-school Sino-foreign boundary hold.

## Next Step

The safe next automated step is to process the next P0/P1 official source candidates from `reference_trend_520_plan_discovery_query_pack.csv` / `reference_trend_520_plan_source_packet_queue.csv`, or, if the user approves browser/OCR/form work, unblock the three batch3 T2 candidates.
"""
    DOC.write_text(doc, encoding="utf-8")

    handoff = f"""## 19. 2026-05-16 batch3 T1 source packet parse

已新增 batch3 T1 官方来源解析层：

- `{PARSE_PREVIEW.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：共生成 source-packet parse preview {len(packets)} 行，其中广西师范大学普通类/物理类/本科普通批行 {metrics['gxnu_ordinary_physics_regular_rows']} 行、计划合计 {metrics['gxnu_ordinary_physics_regular_plan_total']}；哈尔滨医科大学广西普通列合计 {metrics['hrbmu_guangxi_ordinary_plan_total']}、国家专项列合计 {metrics['hrbmu_guangxi_national_special_plan_total']}；宁波诺丁汉 PDF 已抽出文本但仍需人工列对齐。

准入边界：本轮 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。原因是这三类官方计划源均未给广西院校专业组代码，且 UNNC PDF 仍需人工列对齐；它们只进入 source_packet / mapping / QA 层，不进入 canonical、ML 或 32 所 decision_pool。

下一轮优先级：若无人工新增 intake，继续处理 P0/P1 官方计划来源发现队列；若用户批准浏览器/OCR/form，再处理天津中医药、天津理工、安徽中医药三条 batch3 T2 候选。
"""
    append_handoff_once(handoff)

    print(f"wrote {PARSE_PREVIEW}")
    print(f"wrote {ROLLUP}")
    print(f"wrote {QA}")
    print(f"wrote {EXCLUSION}")
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
