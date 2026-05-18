from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
    "school_key",
    "school_name",
    "round_focus",
    "plan_source_url",
    "score_source_url",
    "source_basis",
    "remediation_status",
    "next_action",
    "notes",
]

TARGET_KEYS = [
    "hebei_gongye_211",
    "taiyuan_ligong_211",
    "beijing_keji_211",
    "zhongguo_shiyou_beijing_211",
    "zhongguo_kuangye_beijing_211",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    return str(value or "").strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a five-school score-source remediation round from fallback registry."
    )
    parser.add_argument(
        "--fallback-registry",
        type=Path,
        default=Path("configs") / "actionable_source_fallback_registry.csv",
        help="Fallback registry CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("clean_data") / "engineering_guangxi_seed" / "guangxi_score_source_remediation_round_merged.csv",
        help="Merged remediation round CSV.",
    )
    parser.add_argument(
        "--school-summary-output",
        type=Path,
        default=Path("reports") / "engineering_score_source_remediation_round_school_summary.csv",
        help="School summary CSV.",
    )
    parser.add_argument(
        "--coverage-output",
        type=Path,
        default=Path("reports") / "engineering_score_source_remediation_round_coverage_rollup.csv",
        help="Coverage rollup CSV.",
    )
    return parser


def classify_status(key: str) -> tuple[str, str]:
    if key in {"hebei_gongye_211", "taiyuan_ligong_211"}:
        return (
            "resolved_official_score_source",
            "可直接回填学校级分数来源并继续补最低分/位次",
        )
    if key in {"beijing_keji_211", "zhongguo_shiyou_beijing_211"}:
        return (
            "entry_fallback_ready_wait_unlock",
            "保留官方分数入口，待 headers/会话放行后继续取数",
        )
    return (
        "manual_fallback_entry_added",
        "保留官方招生录取入口作为人工与后续脚本双用回填点",
    )


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.fallback_registry)
    by_key = {normalize_text(row.get("school_key", "")): row for row in rows}

    merged_rows: list[dict[str, str]] = []
    for key in TARGET_KEYS:
        row = by_key.get(key, {})
        status, next_action = classify_status(key)
        merged_rows.append(
            {
                "school_key": key,
                "school_name": normalize_text(row.get("school_name", "")),
                "round_focus": "score_source_remediation",
                "plan_source_url": normalize_text(row.get("plan_source_url", "")),
                "score_source_url": normalize_text(row.get("score_source_url", "")),
                "source_basis": normalize_text(row.get("source_basis", "")),
                "remediation_status": status,
                "next_action": next_action,
                "notes": normalize_text(row.get("notes", "")),
            }
        )

    write_rows(args.output, merged_rows, FIELDS)

    summary_rows = [
        {
            "school_key": row["school_key"],
            "school_name": row["school_name"],
            "score_source_remediation_round_rows": "1",
            "remediation_status": row["remediation_status"],
        }
        for row in merged_rows
    ]
    write_rows(
        args.school_summary_output,
        summary_rows,
        ["school_key", "school_name", "score_source_remediation_round_rows", "remediation_status"],
    )

    coverage_rows = [
        {"metric": "score_source_remediation_round_schools", "value": str(len(merged_rows))},
        {
            "metric": "score_source_remediation_round_with_score_source",
            "value": str(sum(1 for row in merged_rows if normalize_text(row.get("score_source_url", "")))),
        },
        {
            "metric": "score_source_remediation_round_resolved_count",
            "value": str(
                sum(1 for row in merged_rows if row.get("remediation_status") == "resolved_official_score_source")
            ),
        },
    ]
    write_rows(args.coverage_output, coverage_rows, ["metric", "value"])
    print(
        "Wrote score-source remediation round for "
        f"{len(merged_rows)} schools "
        f"({sum(1 for row in merged_rows if normalize_text(row.get('score_source_url', '')))} with score source URLs)."
    )


if __name__ == "__main__":
    main()
