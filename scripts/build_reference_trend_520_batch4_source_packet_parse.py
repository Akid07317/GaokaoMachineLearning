#!/usr/bin/env python3
"""Parse cached batch4 official sources into source-packet preview rows."""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOC_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "batch4_official"

BATCH4_PREVIEW = SEED_DIR / "reference_trend_520_p0_official_source_discovery_batch4_preview.csv"
OUT = SEED_DIR / "reference_trend_520_batch4_source_packet_parse_preview.csv"
ROLLUP = REPORT_DIR / "reference_trend_520_batch4_source_packet_parse_rollup.csv"
QA = REPORT_DIR / "reference_trend_520_batch4_source_packet_parse_qa.csv"
EXCLUSION = REPORT_DIR / "reference_trend_520_batch4_source_packet_parse_exclusion_log.csv"
DOC = DOC_DIR / "reference_trend_520_batch4_source_packet_parse.md"
HANDOFF = DOC_DIR / "gpt54_reference_trend_pool_handoff.md"


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []

    def handle_data(self, data: str) -> None:
        value = re.sub(r"\s+", " ", data).strip()
        if value:
            self.text.append(unescape(value))


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


def pdf_text(path: Path) -> tuple[str, int, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover
        return "", 0, f"pypdf_unavailable:{exc}"

    try:
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        text_path = path.with_suffix(".txt")
        text_path.write_text(text, encoding="utf-8")
        return text, len(reader.pages), "pass"
    except Exception as exc:  # pragma: no cover
        return "", 0, f"pdf_extract_failed:{exc}"


def meta(rows: list[dict[str, str]], *, university: str, role: str | None = None, source_id: str | None = None) -> dict[str, str]:
    for row in rows:
        if source_id and row.get("source_id") == source_id:
            return row
        if row.get("university_name") == university and (role is None or row.get("source_role") == role):
            return row
    return {}


def packet(
    *,
    record_id: str,
    source: dict[str, str],
    raw_file_path: Path,
    parser_dataset: str,
    source_role: str,
    university_group_code: str = "",
    major_or_group: str = "",
    subject_category: str = "",
    batch: str = "",
    plan_count: str | int = "",
    admission_count: str | int = "",
    min_score: str | int = "",
    min_rank: str | int = "",
    max_score: str | int = "",
    max_rank: str | int = "",
    elective_requirement: str = "",
    special_type_detected: str = "",
    qa_status: str,
    collector_confidence: str,
    required_resolution: str,
    evidence_note: str,
) -> dict[str, object]:
    has_group = bool(university_group_code)
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
        "university_group_code": university_group_code,
        "source_role": source_role,
        "major_or_group": major_or_group,
        "elective_requirement": elective_requirement,
        "plan_count": plan_count,
        "admission_count": admission_count,
        "min_score": min_score,
        "min_rank": min_rank,
        "max_score": max_score,
        "max_rank": max_rank,
        "source_contains_group_code": "true" if has_group else "false",
        "source_contains_plan_count": "true" if str(plan_count).strip() else "false",
        "source_contains_min_score": "true" if str(min_score).strip() else "false",
        "source_contains_min_rank": "true" if str(min_rank).strip() else "false",
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


def parse_gxust(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    source = meta(rows, university="广西科技大学", role="official_group_structure_pdf_candidate")
    path = RAW_DIR / "gxust_2025_group_structure.pdf"
    text, pages, status = pdf_text(path)
    group_map = [
        ("111", "历史类", "历史+不限", "社会工作|汉语国际教育|英语|工商管理|财务管理", "history_non_physics_hold"),
        ("151", "物理类", "物理+不限", "经济学|国际经济与贸易|英语|工商管理|财务管理|物流管理|工程管理|工业工程", ""),
        ("152", "物理类", "物理+化学", "数学与应用数学|应用统计学|计算机科学与技术|软件工程|物联网工程|数据科学与大数据技术|网络空间安全", ""),
        ("153", "物理类", "物理+化学", "电子信息工程|电子科学与技术|通信工程", ""),
        ("154", "物理类", "物理+化学", "土木工程", ""),
        ("161", "物理类", "物理+化学", "化学工程与工艺|纺织工程|食品科学与工程|生物工程", ""),
        ("162", "物理类", "物理+化学+生物", "预防医学|药学|医学检验技术|护理学", ""),
        ("163", "物理类", "物理+化学+生物", "临床医学", ""),
        ("171", "物理类", "物理+化学", "工程力学|机械工程(应用本科)|机械电子工程|车辆工程|智能制造工程|新能源汽车工程|交通运输(应用本科)|测控技术与仪器|电气工程及其自动化|自动化|机器人工程", ""),
        ("351", "物理类", "物理+化学", "机械工程(中外合作办学)|软件工程(中外合作办学)", "sino_foreign_boundary_hold"),
        ("719", "历史类", "历史+不限", "少数民族预科班", "ethnic_preparatory_hold"),
        ("759", "物理类", "物理+化学", "少数民族预科班", "ethnic_preparatory_hold"),
    ]
    packets: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, (group, subject, req, majors, special) in enumerate(group_map, start=1):
        is_ready = subject == "物理类" and not special
        row = packet(
            record_id=f"reference_trend_520_batch4_gxust_group_parse_{idx:04d}",
            source=source,
            raw_file_path=path,
            parser_dataset="gxust_2025_group_structure_pdf",
            source_role="official_group_structure_pdf_row",
            university_group_code=group,
            major_or_group=majors,
            subject_category=subject,
            elective_requirement=req,
            special_type_detected=special,
            qa_status="group_structure_ready_exam_line_mapping_needed" if is_ready else "non_physics_or_special_group_hold",
            collector_confidence="T1_official_group_structure_extracted",
            required_resolution="join with Guangxi exam-authority group score/rank line and plan count source before trend intake" if is_ready else "keep non-physics or special/boundary groups isolated",
            evidence_note="GXUST official group-structure PDF gives Guangxi group code and major structure, but no plan count or score/rank.",
        )
        packets.append(row)
        if not is_ready:
            exclusions.append(row)
    qa = [
        {"qa_check": "gxust_pdf_text_extract", "status": status, "value": len(text), "note": f"pages={pages}; text file={path.with_suffix('.txt').relative_to(ROOT)}"},
        {"qa_check": "gxust_group_codes_extracted", "status": "pass", "value": len(group_map), "note": "Manual map derived from single-page official PDF text extraction."},
        {"qa_check": "gxust_regular_physics_group_rows", "status": "pass", "value": sum(1 for _, subject, _, _, special in group_map if subject == "物理类" and not special), "note": "These rows still need exam-authority lines and plan counts."},
    ]
    metrics = {
        "gxust_group_structure_rows": len(packets),
        "gxust_regular_physics_group_rows": sum(1 for row in packets if row["qa_status"] == "group_structure_ready_exam_line_mapping_needed"),
        "gxust_hold_rows": len(exclusions),
    }
    return packets, qa, exclusions, metrics


def parse_kmust(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    plan_source = meta(rows, university="昆明理工大学", role="official_plan_pdf_candidate")
    score_source = meta(rows, university="昆明理工大学", role="official_score_rank_pdf_candidate")
    plan_path = RAW_DIR / "kmust_2025_plan_source.pdf"
    score_path = RAW_DIR / "kmust_2025_score_rank.pdf"
    plan_text, plan_pages, plan_status = pdf_text(plan_path)
    score_text, score_pages, score_status = pdf_text(score_path)

    packets: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    plan_boundary = packet(
        record_id="reference_trend_520_batch4_kmust_plan_pdf_boundary_0001",
        source=plan_source,
        raw_file_path=plan_path,
        parser_dataset="kmust_2025_plan_pdf_text_boundary",
        source_role="official_plan_pdf_boundary_hold",
        subject_category="unknown_plan_pdf_column_layout",
        qa_status="pdf_text_extracted_but_guangxi_column_alignment_needed" if plan_status == "pass" else "pdf_text_extract_failed_hold",
        collector_confidence="T1_official_plan_pdf_text_boundary",
        required_resolution="manual or table-aware column alignment for Guangxi plan counts before row expansion",
        evidence_note=f"KMUST plan PDF text chars={len(plan_text)}; pages={plan_pages}; province column names are split by PDF extraction and are not safely row-aligned.",
    )
    packets.append(plan_boundary)
    exclusions.append(plan_boundary)

    pattern = re.compile(
        r"^广西\s+本科批\s+(?P<college>.*?)\s+(?P<subject>历史类|物理类)\s+"
        r"(?P<major>.*?)\s+(?P<req>不提科目要求|.*?报考\))\s+"
        r"(?P<min_score>\d{3})\s+(?P<min_rank>\d+)\s+(?P<max_score>\d{3})\s+(?P<max_rank>\d+)$"
    )
    matched = []
    missed = []
    for line in [line.strip() for line in score_text.splitlines() if line.strip()]:
        if not line.startswith("广西 "):
            continue
        m = pattern.match(line)
        if m:
            matched.append(m.groupdict())
        else:
            missed.append(line)
    for idx, row in enumerate(matched, start=1):
        is_physics = row["subject"] == "物理类"
        parsed = packet(
            record_id=f"reference_trend_520_batch4_kmust_score_rank_parse_{idx:04d}",
            source=score_source,
            raw_file_path=score_path,
            parser_dataset="kmust_2025_score_rank_pdf_guangxi_rows",
            source_role="official_major_score_rank_pdf_row",
            major_or_group=f"{row['college']}|{row['major']}",
            subject_category=row["subject"],
            batch="本科批",
            min_score=row["min_score"],
            min_rank=row["min_rank"],
            max_score=row["max_score"],
            max_rank=row["max_rank"],
            elective_requirement=row["req"],
            special_type_detected="" if is_physics else "history_non_physics_hold",
            qa_status="score_rank_reference_ready_group_mapping_needed" if is_physics else "non_physics_score_row_hold",
            collector_confidence="T1_official_score_rank_pdf_row_extracted",
            required_resolution="map score/rank row to Guangxi institution-major-group code before trend/calibration intake" if is_physics else "exclude history rows from physical reference trend intake",
            evidence_note="KMUST official score/rank PDF gives major-level min score/rank, but no Guangxi institution-major-group code.",
        )
        packets.append(parsed)
        if not is_physics:
            exclusions.append(parsed)
    qa = [
        {"qa_check": "kmust_plan_pdf_text_extract", "status": plan_status, "value": len(plan_text), "note": f"pages={plan_pages}; text file={plan_path.with_suffix('.txt').relative_to(ROOT)}"},
        {"qa_check": "kmust_score_pdf_text_extract", "status": score_status, "value": len(score_text), "note": f"pages={score_pages}; text file={score_path.with_suffix('.txt').relative_to(ROOT)}"},
        {"qa_check": "kmust_score_guangxi_rows_regex_matched", "status": "pass" if not missed else "review", "value": len(matched), "note": f"missed={len(missed)}"},
        {"qa_check": "kmust_score_guangxi_physics_rows", "status": "pass", "value": sum(1 for row in matched if row["subject"] == "物理类"), "note": "Rows have score/rank but no group code."},
    ]
    metrics = {
        "kmust_score_guangxi_rows": len(matched),
        "kmust_score_guangxi_physics_rows": sum(1 for row in matched if row["subject"] == "物理类"),
        "kmust_score_guangxi_history_hold_rows": sum(1 for row in matched if row["subject"] != "物理类"),
        "kmust_score_regex_missed_rows": len(missed),
        "kmust_plan_boundary_hold_rows": 1,
    }
    return packets, qa, exclusions, metrics


def parse_ujs(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    source = meta(rows, university="江苏大学", role="official_score_reference_html_candidate")
    path = RAW_DIR / "ujs_2025_guangxi_score.html"
    parser = TextParser()
    parser.feed(path.read_text(encoding="utf-8-sig", errors="replace"))
    text = parser.text
    start = text.index("录取类型") + 7 if "录取类型" in text else 0
    data = []
    i = start
    while i < len(text):
        if text[i] not in {"普通类", "国家专项"}:
            i += 1
            continue
        if i + 6 >= len(text):
            break
        typ, subject, major, count, high, low, avg = text[i : i + 7]
        j = i + 7
        control_line = ""
        if j < len(text) and re.fullmatch(r"\d{3}", text[j]) and (j + 1 >= len(text) or text[j + 1] not in {"普通类", "国家专项"}):
            control_line = text[j]
            j += 1
        data.append((typ, subject, major, count, high, low, avg, control_line))
        i = j

    packets: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for idx, (typ, subject, major, count, high, low, avg, control_line) in enumerate(data, start=1):
        is_physics_ordinary = typ == "普通类" and subject.startswith("物理")
        special = ""
        if typ == "国家专项":
            special = "national_special_hold"
        elif not subject.startswith("物理"):
            special = "history_non_physics_hold"
        row = packet(
            record_id=f"reference_trend_520_batch4_ujs_score_parse_{idx:04d}",
            source=source,
            raw_file_path=path,
            parser_dataset="ujs_2025_guangxi_score_html_table",
            source_role="official_major_score_html_row",
            major_or_group=major,
            subject_category="物理类" if subject.startswith("物理") else "历史类",
            batch="本科普通批" if typ == "普通类" else "国家专项",
            admission_count=count,
            min_score=low,
            max_score=high,
            elective_requirement=subject,
            special_type_detected=special,
            qa_status="score_reference_no_rank_group_mapping_needed" if is_physics_ordinary else "non_physics_or_special_score_hold",
            collector_confidence="T1_official_score_html_row_extracted",
            required_resolution="derive/verify rank and map to Guangxi group code before trend/calibration intake" if is_physics_ordinary else "keep non-physics or national-special rows isolated",
            evidence_note=f"UJS official Guangxi admission page gives admission_count={count}, min_score={low}, max_score={high}, avg={avg}, province_control_line={control_line}; no min rank or group code.",
        )
        packets.append(row)
        if not is_physics_ordinary:
            exclusions.append(row)
    qa = [
        {"qa_check": "ujs_html_file_present", "status": "pass" if path.exists() else "fail", "value": str(path.relative_to(ROOT)), "note": ""},
        {"qa_check": "ujs_rows_parsed", "status": "pass", "value": len(data), "note": "Rows parsed from text tokens under official HTML table."},
        {"qa_check": "ujs_ordinary_physics_rows", "status": "pass", "value": sum(1 for row in data if row[0] == "普通类" and row[1].startswith("物理")), "note": "Rows still lack rank and group code."},
    ]
    metrics = {
        "ujs_score_rows": len(data),
        "ujs_ordinary_physics_score_rows": sum(1 for row in data if row[0] == "普通类" and row[1].startswith("物理")),
        "ujs_hold_rows": len(exclusions),
    }
    return packets, qa, exclusions, metrics


def append_handoff(section: str) -> None:
    existing = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    marker = "## 21. 2026-05-16 batch4 source packet parse"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip()
    HANDOFF.write_text(existing.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")


def main() -> None:
    rows = read_csv(BATCH4_PREVIEW)
    packets: list[dict[str, object]] = []
    qa_rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    metrics: dict[str, object] = {"run_timestamp": datetime.now().isoformat(timespec="seconds")}

    for parse_fn in (parse_gxust, parse_kmust, parse_ujs):
        parsed, qa, excl, m = parse_fn(rows)
        packets.extend(parsed)
        qa_rows.extend(qa)
        exclusions.extend(excl)
        metrics.update(m)

    status_counts = Counter(str(row["qa_status"]) for row in packets)
    rollup = [{"metric": key, "value": value, "note": ""} for key, value in sorted(metrics.items())]
    rollup.extend(
        [
            {"metric": "parse_preview_rows", "value": len(packets), "note": "Non-baseline source-packet parse preview rows."},
            {"metric": "hold_or_exclusion_rows", "value": len(exclusions), "note": "Rows withheld from trend pool pending mapping, rank derivation, or special-type isolation."},
            {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No row has the complete group-year score/rank/plan-count QA package yet."},
            {"metric": "calibration_eligible_rows", "value": 0, "note": "No parsed row is accepted into calibration without group-code QA."},
            {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
        ]
    )
    for status, count in sorted(status_counts.items()):
        rollup.append({"metric": f"qa_status::{status}", "value": count, "note": ""})

    fields = [
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
        "university_group_code",
        "source_role",
        "major_or_group",
        "elective_requirement",
        "plan_count",
        "admission_count",
        "min_score",
        "min_rank",
        "max_score",
        "max_rank",
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
    write_csv(OUT, packets, fields)
    write_csv(EXCLUSION, exclusions, fields)
    write_csv(ROLLUP, rollup, ["metric", "value", "note"])
    write_csv(QA, qa_rows, ["qa_check", "status", "value", "note"])

    doc = f"""# Reference Trend 520 Batch4 Source Packet Parse

Run time: {metrics['run_timestamp']}

## Result

- Parse preview rows: {len(packets)}
- GXUST group-structure rows: {metrics['gxust_group_structure_rows']} ({metrics['gxust_regular_physics_group_rows']} regular physical groups)
- KMUST Guangxi score/rank rows: {metrics['kmust_score_guangxi_rows']} ({metrics['kmust_score_guangxi_physics_rows']} physical)
- UJS Guangxi score rows: {metrics['ujs_score_rows']} ({metrics['ujs_ordinary_physics_score_rows']} ordinary physical)
- Hold / exclusion rows: {len(exclusions)}
- Reference trend eligible rows: 0
- Calibration eligible rows: 0
- Canonical / ML entry: closed

## Boundary

GXUST has official group structure but no score/rank or plan counts. KMUST has official score/rank by major but no Guangxi group code; its plan PDF needs column alignment before plan-count rows can be expanded. UJS has official major-level scores and admission counts but no rank or group code. These are useful source-packet/mapping assets, not final group-year records.

## Next Step

Next automation should join GXUST group codes with Guangxi exam-authority 2025 group lines, then use KMUST/UJS score rows as mapping QA evidence. If no safe local join exists, continue P0/P1 official source discovery.
"""
    DOC.write_text(doc, encoding="utf-8")

    handoff = f"""## 21. 2026-05-16 batch4 source packet parse

已新增 batch4 官方来源解析层：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP.relative_to(ROOT)}`
- `{QA.relative_to(ROOT)}`
- `{EXCLUSION.relative_to(ROOT)}`
- `{DOC.relative_to(ROOT)}`

覆盖结果：parse preview {len(packets)} 行。广西科技大学官方专业组 PDF 解析出 {metrics['gxust_group_structure_rows']} 个组，其中普通物理组 {metrics['gxust_regular_physics_group_rows']} 个；昆明理工大学官方分专业分数/位次 PDF 解析出广西行 {metrics['kmust_score_guangxi_rows']} 行，其中物理类 {metrics['kmust_score_guangxi_physics_rows']} 行；江苏大学官方广西录取 HTML 解析出 {metrics['ujs_score_rows']} 行，其中普通物理类 {metrics['ujs_ordinary_physics_score_rows']} 行。

准入边界：本轮 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`。GXUST 有组结构但缺分数/位次/计划数；KMUST 有专业分/位次但缺组代码；UJS 有专业分和录取人数但缺位次/组代码。全部只进入 source_packet / mapping / QA 层。

下一轮优先级：先把广西科技大学 2025 组代码与考试院投档线 join 成 group-line workbench；再用 KMUST/UJS 专业分数行做 group mapping QA。若本地考试院行不可用，则继续 P0/P1 官方来源发现。
"""
    append_handoff(handoff)

    print(f"wrote {OUT}")
    print(f"wrote {ROLLUP}")
    print(f"wrote {QA}")
    print(f"wrote {EXCLUSION}")
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
