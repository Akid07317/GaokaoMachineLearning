from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import re

from gaokao_planner.html_tables import extract_tables_from_file, summarize_tables, write_summary_csv, write_table_csv


@dataclass
class ExtractionTarget:
    seed_id: str
    source_name: str
    segment: str
    target_url: str
    output_path: str
    page_type: str
    link_text: str
    source_page_title: str


def read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_a1_a2_core_targets(
    segment_rows: list[dict[str, str]],
    target_rows: list[dict[str, str]],
    fetch_rows: list[dict[str, str]],
) -> list[ExtractionTarget]:
    allowed = {
        row["seed_id"]: row["second_round_segment"]
        for row in segment_rows
        if row.get("engineering_tier") == "core"
        and row.get("second_round_segment") in {"A1_core_complete", "A2_core_near_complete"}
    }
    fetch_by_url = {
        row["url"]: row
        for row in fetch_rows
        if row.get("status") == "ok"
    }

    targets: list[ExtractionTarget] = []
    seen: set[tuple[str, str]] = set()
    for row in target_rows:
        seed_id = row.get("seed_id", "")
        segment = allowed.get(seed_id)
        if not segment:
            continue
        url = row.get("target_url", "")
        fetch_row = fetch_by_url.get(url)
        if not fetch_row:
            continue
        key = (seed_id, url)
        if key in seen:
            continue
        seen.add(key)
        targets.append(
            ExtractionTarget(
                seed_id=seed_id,
                source_name=row.get("source_name", ""),
                segment=segment,
                target_url=url,
                output_path=fetch_row.get("output_path", ""),
                page_type=infer_page_type(
                    row.get("link_text", ""),
                    row.get("source_page_title", ""),
                    row.get("matched_reason", ""),
                    url,
                ),
                link_text=row.get("link_text", ""),
                source_page_title=row.get("source_page_title", ""),
            )
        )
    return sorted(targets, key=lambda item: (item.source_name, item.page_type, item.target_url))


def infer_page_type(link_text: str, page_title: str, matched_reason: str, url: str) -> str:
    combined = " ".join([link_text, page_title, matched_reason, url])
    if any(term in combined for term in ["招生计划", "分省计划", "zsjh"]):
        return "plan"
    if any(term in combined for term in ["历年分数", "往年分数", "录取情况", "录取最低分", "投档", "lnfs", "lqcx", "wnfs"]):
        return "score"
    if any(term in combined for term in ["招生章程", "zszc"]):
        return "rule"
    if any(term in combined for term in ["本科招生", "本科生招生", "招生信息", "招生就业", "bszn", "bkzn"]):
        return "entry"
    return "other"


def safe_slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")[:120] or "page"


def is_pdf_content(path: str | Path) -> bool:
    raw = Path(path).read_bytes()[:8]
    return raw.startswith(b"%PDF-")


def extract_target_tables(
    targets: list[ExtractionTarget],
    *,
    project_root: str | Path,
    output_dir: str | Path,
) -> list[dict[str, str | int]]:
    project_root = Path(project_root)
    output_dir = Path(output_dir)
    manifest: list[dict[str, str | int]] = []

    for target in targets:
        source_path = project_root / target.output_path
        if not source_path.exists():
            manifest.append(
                {
                    "seed_id": target.seed_id,
                    "source_name": target.source_name,
                    "segment": target.segment,
                    "page_type": target.page_type,
                    "target_url": target.target_url,
                    "source_path": str(source_path),
                    "status": "missing_source",
                    "table_count": 0,
                    "summary_path": "",
                    "notes": "source file missing",
                }
            )
            continue

        if is_pdf_content(source_path):
            manifest.append(
                {
                    "seed_id": target.seed_id,
                    "source_name": target.source_name,
                    "segment": target.segment,
                    "page_type": target.page_type,
                    "target_url": target.target_url,
                    "source_path": str(source_path),
                    "status": "pdf_skip",
                    "table_count": 0,
                    "summary_path": "",
                    "notes": "pdf content saved with html suffix",
                }
            )
            continue

        tables = extract_tables_from_file(source_path)
        summaries = summarize_tables(tables)
        seed_output_dir = output_dir / target.seed_id
        prefix = safe_slug(Path(target.output_path).stem)
        summary_path = seed_output_dir / f"{prefix}_table_summary.csv"
        write_summary_csv(summaries, summary_path)
        for index, table in enumerate(tables, start=1):
            write_table_csv(table, seed_output_dir / f"{prefix}_table_{index:02d}.csv")

        first_row_preview = ""
        if summaries:
            first_row_preview = " | ".join(summaries[0].first_row[:5])

        manifest.append(
            {
                "seed_id": target.seed_id,
                "source_name": target.source_name,
                "segment": target.segment,
                "page_type": target.page_type,
                "target_url": target.target_url,
                "source_path": str(source_path),
                "status": "ok",
                "table_count": len(tables),
                "summary_path": str(summary_path),
                "notes": first_row_preview,
            }
        )
    return manifest


def write_manifest(rows: list[dict[str, str | int]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "seed_id",
        "source_name",
        "segment",
        "page_type",
        "target_url",
        "source_path",
        "status",
        "table_count",
        "summary_path",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
