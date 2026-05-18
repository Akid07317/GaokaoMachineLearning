from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import csv


KEEP_PAGE_TERMS = [
    "本科招生",
    "本科生招生",
    "招生信息",
    "招生信息网",
    "招生就业",
    "招生计划",
    "分省计划",
    "历年分数",
    "往年分数",
    "录取情况",
    "录取最低分",
    "投档",
    "招生章程",
    "分省信息",
]


@dataclass
class EngineeringSchool:
    seed_id: str
    source_name: str
    engineering_tier: str
    focus_reason: str
    score_floor: int
    notes: str


@dataclass
class EngineeringTarget:
    seed_id: str
    source_name: str
    engineering_tier: str
    score_floor: int
    target_url: str
    link_text: str
    source_page_title: str
    matched_reason: str
    fetch_priority: int
    score_threshold_status: str


def read_engineering_schools(path: str | Path) -> dict[str, EngineeringSchool]:
    schools: dict[str, EngineeringSchool] = {}
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            schools[row["seed_id"]] = EngineeringSchool(
                seed_id=row["seed_id"],
                source_name=row["source_name"],
                engineering_tier=row["engineering_tier"],
                focus_reason=row["focus_reason"],
                score_floor=int(row["score_floor"]),
                notes=row.get("notes", ""),
            )
    return schools


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def filter_engineering_targets(
    target_rows: list[dict[str, str]],
    engineering_schools: dict[str, EngineeringSchool],
) -> list[EngineeringTarget]:
    filtered: list[EngineeringTarget] = []
    for row in target_rows:
        seed_id = row.get("seed_id", "")
        school = engineering_schools.get(seed_id)
        if school is None:
            continue
        combined = " ".join(
            [
                row.get("link_text", ""),
                row.get("source_page_title", ""),
                row.get("matched_reason", ""),
                row.get("target_url", ""),
            ]
        )
        if not any(term in combined for term in KEEP_PAGE_TERMS):
            continue
        filtered.append(
            EngineeringTarget(
                seed_id=seed_id,
                source_name=school.source_name,
                engineering_tier=school.engineering_tier,
                score_floor=school.score_floor,
                target_url=row.get("target_url", ""),
                link_text=row.get("link_text", ""),
                source_page_title=row.get("source_page_title", ""),
                matched_reason=row.get("matched_reason", ""),
                fetch_priority=int(row.get("fetch_priority", "0") or "0"),
                score_threshold_status="pending_score_extraction",
            )
        )
    return sorted(
        filtered,
        key=lambda row: (
            0 if row.engineering_tier == "core" else 1,
            -row.fetch_priority,
            row.source_name,
            row.target_url,
        ),
    )


def build_school_matrix(
    engineering_schools: dict[str, EngineeringSchool],
    targets: list[EngineeringTarget],
    fetch_rows: list[dict[str, str]],
) -> list[dict[str, str | int]]:
    fetch_map = {row["url"]: row for row in fetch_rows}
    grouped: dict[str, dict[str, str | int]] = {}
    for seed_id, school in engineering_schools.items():
        grouped[seed_id] = {
            "seed_id": seed_id,
            "source_name": school.source_name,
            "engineering_tier": school.engineering_tier,
            "score_floor": school.score_floor,
            "target_count": 0,
            "fetched_ok_count": 0,
            "has_plan_page": "false",
            "has_score_page": "false",
            "has_rule_page": "false",
            "score_threshold_status": "pending_score_extraction",
            "focus_reason": school.focus_reason,
            "notes": school.notes,
        }

    for target in targets:
        row = grouped[target.seed_id]
        row["target_count"] = int(row["target_count"]) + 1
        combined = " ".join([target.link_text, target.source_page_title, target.matched_reason])
        if "招生计划" in combined or "分省计划" in combined:
            row["has_plan_page"] = "true"
        if any(term in combined for term in ["历年分数", "往年分数", "录取情况", "录取最低分", "投档"]):
            row["has_score_page"] = "true"
        if "招生章程" in combined:
            row["has_rule_page"] = "true"
        fetch_row = fetch_map.get(target.target_url)
        if fetch_row and fetch_row.get("status") == "ok":
            row["fetched_ok_count"] = int(row["fetched_ok_count"]) + 1

    return sorted(
        grouped.values(),
        key=lambda row: (
            0 if row["engineering_tier"] == "core" else 1,
            -int(row["fetched_ok_count"]),
            row["source_name"],
        ),
    )


def write_dict_rows(rows: list[dict[str, str | int]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {output_path}")
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_target_rows(rows: list[EngineeringTarget], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "seed_id",
                "source_name",
                "engineering_tier",
                "score_floor",
                "target_url",
                "link_text",
                "source_page_title",
                "matched_reason",
                "fetch_priority",
                "score_threshold_status",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
