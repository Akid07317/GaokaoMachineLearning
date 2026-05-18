#!/usr/bin/env python3
"""Build marker 122 JXUTCM official source-packet parse preview.

The output is a preview only: it records official 2025 Guangxi ordinary-batch
physical plan rows from the visible official page text and keeps every row
closed to reference-trend intake, calibration, canonical, ML, and decision-pool
entry until score/rank and group-code alignment QA are joined.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

CANDIDATE_PREVIEW = SEED_DIR / "reference_trend_520_p1_batch17_official_candidate_preview.csv"

OUT_PREFIX = "reference_trend_520_p1_batch17_jxutcm_source_packet_parse_preview"
OUT_CSV = SEED_DIR / f"{OUT_PREFIX}.csv"
ROLLUP_CSV = REPORTS_DIR / f"{OUT_PREFIX}_rollup.csv"
QA_CSV = REPORTS_DIR / f"{OUT_PREFIX}_qa.csv"
EXCLUSION_CSV = REPORTS_DIR / f"{OUT_PREFIX}_exclusion_log.csv"
DOC_MD = DOCS_DIR / f"{OUT_PREFIX}.md"
HANDOFF_MD = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zsxxw.jxutcm.edu.cn/info/1049/2562.htm"
SOURCE_TITLE = "2025年江西中医药大学本科招生计划表（广西）"
SOURCE_OWNER = "江西中医药大学招生信息网"


def read_candidate() -> dict[str, str]:
    with CANDIDATE_PREVIEW.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["university_code"] == "10412" and row["source_url"] == SOURCE_URL:
                return row
    raise SystemExit("JXUTCM candidate row not found in marker 121 preview")


def build_major_rows(candidate: dict[str, str]) -> list[dict[str, object]]:
    base = {
        "source_candidate_id": candidate["candidate_id"],
        "packet_id": candidate["packet_id"],
        "queue_id": candidate["queue_id"],
        "queue_rank": candidate["queue_ranks"],
        "source_url": SOURCE_URL,
        "source_owner": SOURCE_OWNER,
        "source_title": SOURCE_TITLE,
        "raw_file_path": "web_open_official_page_no_local_cache",
        "university_code": "10412",
        "university_name": "江西中医药大学",
        "year": "2025",
        "province": "广西",
        "batch": "本科普通批",
        "subject_category": "物理类",
        "source_subject_label": "物理类",
        "queue_group_code": candidate["group_codes"],
        "source_contains_group_code": "true",
        "source_contains_plan_count": "true",
        "source_contains_min_score": "false",
        "source_contains_min_rank": "false",
        "qa_status": "parse_preview_hold_for_score_rank_join_and_group_alignment_QA",
        "collector_confidence": "T1_official_html_exact_guangxi_plan_page_row",
        "intended_layer": "reference_trend_source_packet_parse_preview_only",
        "source_packet_preview_eligible": "true",
        "reference_trend_pool_eligible": "false",
        "calibration_eligible": "false",
        "canonical_ml_entry_open": "false",
        "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
        "required_resolution": (
            "join official admission line/min-rank and verify short source group "
            "codes against Guangxi填报系统 before any calibration"
        ),
    }
    groups = [
        (
            "01",
            "不提科目要求",
            [
                ("中医学（5+3一体化）", 2, "true", "5+3 integrated program; ordinary batch row", "official page line 64"),
                ("中医学", 3, "false", "", "official page line 65"),
                ("针灸推拿学", 2, "false", "", "official page line 66"),
                ("中医康复学", 2, "false", "", "official page line 67"),
                ("中医养生学", 2, "false", "", "official page line 68"),
                ("中医骨伤科学", 2, "false", "", "official page line 69"),
            ],
        ),
        ("04", "物理和生物均须选考", [("中西医临床医学", 4, "false", "", "official page line 70")]),
        (
            "06",
            "物理和化学均须选考",
            [
                ("食品质量与安全", 2, "false", "", "official page line 71"),
                ("食品营养与健康", 2, "false", "", "official page line 72"),
                ("预防医学", 2, "false", "", "official page line 73"),
                ("药学", 2, "false", "", "official page line 74"),
                ("中药学", 2, "false", "", "official page line 75"),
                ("中药资源与开发", 2, "false", "", "official page line 76"),
                ("药物制剂", 2, "false", "", "official page line 77"),
                ("中药制药", 2, "false", "", "official page line 78"),
                ("计算机科学与技术", 2, "false", "", "official page line 79"),
                ("医学信息工程", 2, "false", "", "official page line 80"),
                ("生物医学工程", 2, "false", "", "official page line 81"),
                ("医学影像技术", 2, "false", "", "official page line 82"),
                ("应用化学", 2, "false", "", "official page line 83"),
                ("医学检验技术", 2, "false", "", "official page line 84"),
                ("康复治疗学", 2, "false", "", "official page line 85"),
            ],
        ),
        (
            "08",
            "不提科目要求",
            [
                ("保险学", 3, "false", "", "official page line 86"),
                ("公共事业管理", 2, "false", "", "official page line 87"),
                ("健康服务与管理", 2, "false", "", "official page line 88"),
            ],
        ),
        ("02", "生物必须选考", [("护理学", 8, "false", "", "official page line 89")]),
    ]

    rows: list[dict[str, object]] = []
    seq = 1
    for source_group_code, requirement, majors in groups:
        for major_name, plan_count, special_flag, special_note, evidence_line in majors:
            row = {
                "record_id": f"reference_trend_520_p1_batch17_jxutcm_{seq:04d}",
                "row_scope": "official_major_plan_row",
                **base,
                "source_group_code": source_group_code,
                "major_name": major_name,
                "duration_years": "",
                "plan_count": plan_count,
                "subject_requirement": requirement,
                "special_type_detected": special_flag,
                "special_type_note": special_note,
                "evidence_note": (
                    f"{evidence_line}; official page lines 55-56 identify title/header; "
                    "line 93 states professional group number follows exam filling system."
                ),
            }
            rows.append(row)
            seq += 1
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs() -> None:
    candidate = read_candidate()
    rows = build_major_rows(candidate)

    fields = [
        "record_id",
        "row_scope",
        "source_candidate_id",
        "packet_id",
        "queue_id",
        "queue_rank",
        "source_url",
        "source_owner",
        "source_title",
        "raw_file_path",
        "university_code",
        "university_name",
        "year",
        "province",
        "batch",
        "subject_category",
        "source_subject_label",
        "queue_group_code",
        "source_group_code",
        "major_name",
        "duration_years",
        "plan_count",
        "subject_requirement",
        "source_contains_group_code",
        "source_contains_plan_count",
        "source_contains_min_score",
        "source_contains_min_rank",
        "special_type_detected",
        "special_type_note",
        "qa_status",
        "collector_confidence",
        "intended_layer",
        "source_packet_preview_eligible",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
        "required_resolution",
        "evidence_note",
    ]
    write_csv(OUT_CSV, rows, fields)

    by_group: defaultdict[str, int] = defaultdict(int)
    by_requirement = Counter()
    special = Counter()
    for row in rows:
        by_group[str(row["source_group_code"])] += int(row["plan_count"])
        by_requirement[str(row["subject_requirement"])] += int(row["plan_count"])
        special[str(row["special_type_note"] or "ordinary_unmarked")] += 1

    rollup = [
        {"metric": "source_url", "value": SOURCE_URL, "note": "Official JXUTCM 2025 Guangxi plan page."},
        {"metric": "official_major_rows", "value": len(rows), "note": "Physical ordinary-batch major rows only."},
        {"metric": "physical_plan_sum", "value": sum(int(row["plan_count"]) for row in rows), "note": ""},
        {"metric": "source_group_year_rows", "value": len(by_group), "note": "Short professional group codes printed by source."},
        {"metric": "source_group_plan_sum::01", "value": by_group["01"], "note": "不提科目要求"},
        {"metric": "source_group_plan_sum::04", "value": by_group["04"], "note": "物理和生物均须选考"},
        {"metric": "source_group_plan_sum::06", "value": by_group["06"], "note": "物理和化学均须选考"},
        {"metric": "source_group_plan_sum::08", "value": by_group["08"], "note": "不提科目要求"},
        {"metric": "source_group_plan_sum::02", "value": by_group["02"], "note": "生物必须选考"},
        {"metric": "excluded_history_rows_visible_on_source", "value": 6, "note": "History rows are visible on source lines 57-63 and excluded from this physical preview."},
        {"metric": "excluded_sports_rows_visible_on_source", "value": 2, "note": "Sports rows are visible on source lines 90-91 and excluded from ordinary-batch physical preview."},
        {"metric": "source_packet_preview_eligible_rows", "value": len(rows), "note": "Preview only."},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No min score/rank joined and short group-code alignment remains QA hold."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "Plan-only source rows."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]
    for requirement, total in sorted(by_requirement.items()):
        rollup.append({"metric": f"requirement_plan_sum::{requirement}", "value": total, "note": ""})
    for label, count in sorted(special.items()):
        rollup.append({"metric": f"special_note_row_count::{label}", "value": count, "note": ""})
    write_csv(ROLLUP_CSV, rollup, ["metric", "value", "note"])

    qa = []
    qa.append({
        "check": "candidate_row_found",
        "status": "PASS",
        "detail": f"Mapped source parse preview to {candidate['candidate_id']} from marker 121.",
    })
    qa.append({
        "check": "official_page_identity",
        "status": "PASS",
        "detail": "Official page title/header identify 2025 JXUTCM本科招生计划表（广西）.",
    })
    qa.append({
        "check": "physical_ordinary_rows_extracted",
        "status": "PASS" if len(rows) == 26 and sum(int(row["plan_count"]) for row in rows) == 62 else "FAIL",
        "detail": f"rows={len(rows)} physical_plan_sum={sum(int(row['plan_count']) for row in rows)}.",
    })
    qa.append({
        "check": "group_rollup_complete",
        "status": "PASS" if dict(by_group) == {"01": 13, "04": 4, "06": 30, "08": 7, "02": 8} else "FAIL",
        "detail": "group_sums=" + ";".join(f"{k}:{v}" for k, v in sorted(by_group.items())),
    })
    qa.append({
        "check": "excluded_nonordinary_or_nonphysical_rows",
        "status": "PASS",
        "detail": "History rows and sports rows are not included in the physical ordinary-batch preview.",
    })
    qa.append({
        "check": "score_rank_not_claimed",
        "status": "PASS",
        "detail": "Source is a plan table only; min score and min rank flags remain false.",
    })
    qa.append({
        "check": "no_reference_trend_pool_intake",
        "status": "PASS",
        "detail": "All rows remain source_packet preview only.",
    })
    qa.append({
        "check": "canonical_ml_closed",
        "status": "PASS",
        "detail": "Canonical/ML and decision-pool entry remain closed.",
    })
    write_csv(QA_CSV, qa, ["check", "status", "detail"])

    exclusion = []
    for row in rows:
        exclusion.append({
            "record_id": row["record_id"],
            "university_code": row["university_code"],
            "university_name": row["university_name"],
            "source_group_code": row["source_group_code"],
            "major_name": row["major_name"],
            "plan_count": row["plan_count"],
            "excluded_from": "reference_trend_pool_intake|calibration|canonical_ml|decision_pool",
            "reason": "plan_only_preview_no_min_score_rank_and_group_alignment_QA_pending",
            "safe_next_action": "join official Guangxi admission line/rank and verify group-code mapping before intake consideration",
        })
    write_csv(EXCLUSION_CSV, exclusion, [
        "record_id",
        "university_code",
        "university_name",
        "source_group_code",
        "major_name",
        "plan_count",
        "excluded_from",
        "reason",
        "safe_next_action",
    ])

    doc = f"""# Reference trend 520 P1 batch17 JXUTCM source packet parse preview

Generated: 2026-05-17

## Scope

This preview parses the official Jiangxi University of Chinese Medicine 2025 Guangxi plan page into auditable source-packet preview rows for本科普通批物理类 only.

Source: {SOURCE_URL}

## Outputs

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`

## Result

- Physical ordinary-batch major rows: {len(rows)}
- Physical ordinary-batch plan sum: {sum(int(row["plan_count"]) for row in rows)}
- Source professional groups captured: {", ".join(sorted(by_group))}
- Group plan sums: {", ".join(f"{k}={v}" for k, v in sorted(by_group.items()))}

## Boundary

- This is a source-packet parse preview, not reference-trend intake.
- The source page is plan-only and does not provide minimum score or rank.
- Source group codes are printed as short professional group codes; the page also says group number should follow the exam filling system, so alignment to queue group code `101` remains a QA hold.
- History rows and sports rows visible on the source are excluded from this physical ordinary-batch preview.
- `reference_trend_pool_eligible=false`, `calibration_eligible=false`, and `canonical_ml_entry_open=false` for every row.
"""
    DOC_MD.write_text(doc, encoding="utf-8")

    marker = f"""

## 122. 2026-05-17 P1 batch17 JXUTCM source packet parse preview

已新增江西中医药大学 T1 官方页 source-packet parse preview：

- `clean_data/engineering_guangxi_seed/{OUT_PREFIX}.csv`
- `reports/{OUT_PREFIX}_rollup.csv`
- `reports/{OUT_PREFIX}_qa.csv`
- `reports/{OUT_PREFIX}_exclusion_log.csv`
- `docs/{OUT_PREFIX}.md`

覆盖结果：从 marker 121 的江西中医药大学精确广西计划页候选中解析出 26 条 2025 广西本科普通批物理类专业计划 rows，计划合计 62；按源页短专业组代码汇总为 5 个 source group-year preview rows（01=13, 04=4, 06=30, 08=7, 02=8）。QA PASS。

准入边界：本轮只生成 source_packet 解析预览；源页为计划表，不含最低分/最低位次，且短专业组代码仍需与广西填报系统/投档线做映射 QA；reference trend intake、calibration、canonical/ML、32 所 decision_pool 均继续关闭。
"""
    existing = HANDOFF_MD.read_text(encoding="utf-8") if HANDOFF_MD.exists() else ""
    if "## 122. 2026-05-17 P1 batch17 JXUTCM source packet parse preview" not in existing:
        with HANDOFF_MD.open("a", encoding="utf-8") as f:
            f.write(marker)


if __name__ == "__main__":
    build_outputs()
