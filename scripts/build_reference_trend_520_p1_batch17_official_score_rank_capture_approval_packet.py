#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

INPUT = SEED_DIR / "reference_trend_520_p1_batch17_official_score_rank_lookup_targets.csv"

PACKET = SEED_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.csv"
ROLLUP = REPORTS_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_rollup.csv"
QA = REPORTS_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_qa.csv"
EXCLUSION = REPORTS_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_exclusion_log.csv"
DOC = DOCS_DIR / "reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

OFFICIAL_SCORE_RANK_SCOPE = "广西招生考试院 2025 一分一档表 首选物理科目组"
PROHIBITED_METHODS = (
    "do_not_repeat_terminal_curl_qg_qn;"
    "do_not_use_third_party_mirror_rank;"
    "do_not_infer_rank_from_line_score"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def qa_row(check: str, status: bool, detail: str) -> dict[str, str]:
    return {"check": check, "status": "PASS" if status else "FAIL", "detail": detail}


def main() -> None:
    targets = read_rows(INPUT)
    packet_rows: list[dict[str, str]] = []

    for index, target in enumerate(targets, start=1):
        packet_rows.append(
            {
                "approval_packet_id": f"reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_{index:04d}",
                "lookup_target_id": target["score_rank_lookup_target_id"],
                "year": target["year"],
                "province": target["province"],
                "subject_category": target["subject_category"],
                "min_score": target["min_score"],
                "consumer_group_pair_keys": target["consumer_group_pair_keys"],
                "consumer_group_year_count": target["consumer_group_year_count"],
                "official_source_scope": OFFICIAL_SCORE_RANK_SCOPE,
                "approval_needed_for": (
                    "browser_state_or_user_provided_official_raw_cache_for_2025_physics_score_rank"
                ),
                "acceptable_artifact_types": "official_raw_html|official_pdf|official_xls_xlsx|browser_saved_page_with_url_timestamp",
                "required_artifact_fields": "raw_file_path|source_url|retrieved_at|score_column|rank_column|total_score_policy_note",
                "blocked_terminal_boundary": target["official_rank_source_status"],
                "prohibited_methods": PROHIBITED_METHODS,
                "rank_selection_policy": (
                    "Select min_rank only after official raw artifact is cached and score/rank/total-score policy QA passes."
                ),
                "fanout_policy": target["rank_lookup_policy"],
                "approval_decision": "",
                "approved_by": "",
                "approval_timestamp": "",
                "raw_file_path": "",
                "review_status": "pending_user_approval_or_official_raw_cache",
                "stop_condition": target["stop_condition"],
                "reference_trend_pool_eligible": "false",
                "calibration_eligible": "false",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
            }
        )

    packet_fields = [
        "approval_packet_id",
        "lookup_target_id",
        "year",
        "province",
        "subject_category",
        "min_score",
        "consumer_group_pair_keys",
        "consumer_group_year_count",
        "official_source_scope",
        "approval_needed_for",
        "acceptable_artifact_types",
        "required_artifact_fields",
        "blocked_terminal_boundary",
        "prohibited_methods",
        "rank_selection_policy",
        "fanout_policy",
        "approval_decision",
        "approved_by",
        "approval_timestamp",
        "raw_file_path",
        "review_status",
        "stop_condition",
        "reference_trend_pool_eligible",
        "calibration_eligible",
        "canonical_ml_entry_open",
        "decision_pool_boundary",
    ]
    write_csv(PACKET, packet_fields, packet_rows)

    duplicate_fanout_rows = [
        row for row in packet_rows if int(row["consumer_group_year_count"]) > 1
    ]
    rollup_rows = [
        {"metric": "approval_packet_rows", "value": str(len(packet_rows)), "note": "One row per unique official score-rank lookup target."},
        {"metric": "consumer_group_year_rows", "value": str(sum(int(row["consumer_group_year_count"]) for row in packet_rows)), "note": "Total group-year rows covered after fanout."},
        {"metric": "duplicate_fanout_score_rows", "value": str(len(duplicate_fanout_rows)), "note": "Scores serving more than one group-year consumer."},
        {"metric": "official_raw_artifact_rows", "value": "0", "note": "No official raw score-rank artifact is present yet."},
        {"metric": "approval_decision_rows", "value": "0", "note": "No browser/cache approval has been recorded."},
        {"metric": "reference_trend_pool_eligible_rows", "value": "0", "note": "Rank source not captured."},
        {"metric": "calibration_eligible_rows", "value": "0", "note": "No official min_rank selected."},
        {"metric": "canonical_ml_entry_open_rows", "value": "0", "note": "Canonical/ML remains closed."},
    ]
    for row in packet_rows:
        rollup_rows.append(
            {
                "metric": f"approval_score::{row['min_score']}",
                "value": row["consumer_group_year_count"],
                "note": row["consumer_group_pair_keys"],
            }
        )
    write_csv(ROLLUP, ["metric", "value", "note"], rollup_rows)

    exclusion_rows = [
        {
            "excluded_from": "official_score_rank_capture_approval_packet",
            "reason": "no_lookup_targets_excluded",
            "detail": "All marker 135 lookup targets require the same official raw-cache or browser approval boundary.",
        }
    ]
    write_csv(EXCLUSION, ["excluded_from", "reason", "detail"], exclusion_rows)

    qa_rows = [
        qa_row("approval_packet_row_count", len(packet_rows) == 5, f"{len(packet_rows)} approval rows generated."),
        qa_row("consumer_fanout_preserved", sum(int(row["consumer_group_year_count"]) for row in packet_rows) == 6, "6 group-year consumers preserved."),
        qa_row("duplicate_fanout_marked", any(row["min_score"] == "490" and row["consumer_group_year_count"] == "2" for row in packet_rows), "Score 490 fanout is preserved."),
        qa_row("approval_fields_blank", all(not row["approval_decision"] and not row["raw_file_path"] for row in packet_rows), "No approval or raw artifact is falsely recorded."),
        qa_row("prohibited_methods_marked", all("do_not_repeat_terminal_curl_qg_qn" in row["prohibited_methods"] and "do_not_use_third_party_mirror_rank" in row["prohibited_methods"] for row in packet_rows), "Blocked methods are explicit."),
        qa_row("intake_and_canonical_closed", all(row["reference_trend_pool_eligible"] == "false" and row["canonical_ml_entry_open"] == "false" for row in packet_rows), "Intake, calibration, canonical, and ML remain closed."),
    ]
    write_csv(QA, ["check", "status", "detail"], qa_rows)

    score_lines = "\n".join(
        f"- {row['min_score']}: {row['consumer_group_year_count']} consumer(s) -> {row['consumer_group_pair_keys']}"
        for row in packet_rows
    )
    DOC.write_text(
        f"""# P1 Batch17 Official Score-Rank Capture Approval Packet

日期：2026-05-17

## 结果

从 marker 135 的 5 个 official score-rank lookup targets 生成浏览器态/官方 raw cache 批准包。该包用于明确：只有在用户批准浏览器态/可审计替代抓取，或提供官方 2025 广西物理类一分一档 raw artifact 后，后续模型才能选择 `min_rank`。

{score_lines}

## 需要批准或人工提供的内容

- 官方来源范围：{OFFICIAL_SCORE_RANK_SCOPE}
- 可接受 artifact：官方 raw HTML、PDF、XLS/XLSX，或带 URL 与时间戳的 browser saved page
- 必填 artifact 字段：`raw_file_path`、`source_url`、`retrieved_at`、`score_column`、`rank_column`、`total_score_policy_note`

## 禁止动作

- 不重复终端 curl 已阻塞的 `qg/qn` 细分页路径
- 不使用第三方镜像位次
- 不从投档最低分推断位次
- 不打开 reference trend intake、calibration、canonical/ML 或 32 所 decision_pool

## 下一步

等待用户批准浏览器态/官方 raw cache 捕获，或用户直接提供官方一分一档 raw 文件。之后才能生成 score-rank parse preview。
""",
        encoding="utf-8",
    )

    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(
            f"""

## 136. 2026-05-17 P1 batch17 official score-rank capture approval packet

已新增 P1 batch17 official score-rank capture approval packet：

- `clean_data/engineering_guangxi_seed/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_rollup.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_qa.csv`
- `reports/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet_exclusion_log.csv`
- `docs/reference_trend_520_p1_batch17_official_score_rank_capture_approval_packet.md`

覆盖结果：将 marker 135 的 5 个 official score-rank lookup targets 转成浏览器态/官方 raw cache 批准包，覆盖 6 条 group-year consumers；`490` 继续保持一次 lookup 服务 2 条 group-year 的 fanout。QA PASS。

准入边界：本轮只生成批准包/QA/rollup，不抓取一分一档细页、不重复已阻塞终端 curl、不采用第三方镜像位次、不选择或推断 min_rank；等待用户批准浏览器态/可审计替代抓取或提供官方 raw artifact 后才能继续。
"""
        )


if __name__ == "__main__":
    main()
