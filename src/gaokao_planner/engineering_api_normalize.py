from __future__ import annotations

from pathlib import Path
import csv
import json


def read_api_fetch_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def load_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_csv(path: str | Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_huabei_plan_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        props = item.get("properties", {})
        rows.append(
            {
                "year": props.get("year", ""),
                "province": props.get("province", ""),
                "type": props.get("type", ""),
                "science_category": props.get("scienceCategory", ""),
                "major": props.get("major", ""),
                "planned_quantity": props.get("plannedQuantity", ""),
                "requirement": props.get("requirement", ""),
                "record_id": item.get("id", ""),
                "source_url": item.get("url", ""),
            }
        )
    return rows


def normalize_huabei_score_summary_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        props = item.get("properties", {})
        rows.append(
            {
                "year": props.get("year", ""),
                "province": props.get("province", ""),
                "type": props.get("type", ""),
                "science_category": props.get("scienceCategory", ""),
                "highest_score": props.get("highestScore", ""),
                "minimum_score": props.get("minimumScore", ""),
                "lowest_score_ranking": props.get("lowestScoreRanking", ""),
                "record_id": item.get("id", ""),
                "source_url": item.get("url", ""),
            }
        )
    return rows


def normalize_huabei_score_major_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        props = item.get("properties", {})
        rows.append(
            {
                "year": props.get("year", ""),
                "province": props.get("province", ""),
                "type": props.get("type", ""),
                "science_category": props.get("scienceCategory", ""),
                "major": props.get("major", ""),
                "requirement": props.get("requirement", ""),
                "highest_score": props.get("highestScore", ""),
                "minimum_score": props.get("minimumScore", ""),
                "lowest_score_ranking": props.get("lowestScoreRanking", ""),
                "record_id": item.get("id", ""),
                "source_url": item.get("url", ""),
            }
        )
    return rows


def normalize_nanhang_plan_items(items: list[dict[str, object]], source_slug: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        rows.append(
            {
                "year": item.get("year", ""),
                "province": item.get("province", ""),
                "type": item.get("type", ""),
                "subject": item.get("subject", ""),
                "college": item.get("college", ""),
                "specialty": item.get("specialty", ""),
                "plan_number": item.get("planNumber", ""),
                "weight": item.get("weight", ""),
                "record_id": item.get("id", ""),
                "introduction_link": item.get("introductionLink", ""),
                "source_slug": source_slug,
            }
        )
    return rows


def normalize_api_payloads(
    fetch_rows: list[dict[str, str]],
    *,
    project_root: str | Path,
    output_dir: str | Path,
    summary_path: str | Path,
) -> list[dict[str, object]]:
    project_root = Path(project_root)
    output_dir = Path(output_dir)
    summary_rows: list[dict[str, object]] = []
    nanhang_rows: list[dict[str, object]] = []

    for row in fetch_rows:
        if row.get("status") != "ok":
            continue
        source_id = row.get("source_id", "")
        target_kind = row.get("target_kind", "")
        source_path = project_root / row.get("output_path", "")
        payload = load_json(source_path)
        data = payload.get("data", []) if isinstance(payload, dict) else []

        output_csv = ""
        normalized_rows: list[dict[str, object]] = []
        fieldnames: list[str] = []

        if source_id == "huabei_dianli_211" and target_kind == "plan_json":
            normalized_rows = normalize_huabei_plan_items(data)
            fieldnames = [
                "year",
                "province",
                "type",
                "science_category",
                "major",
                "planned_quantity",
                "requirement",
                "record_id",
                "source_url",
            ]
            output_csv = str(output_dir / "huabei_dianli_plan_rows.csv")
            _write_csv(output_csv, normalized_rows, fieldnames)
        elif source_id == "huabei_dianli_211" and target_kind == "score_summary_json":
            normalized_rows = normalize_huabei_score_summary_items(data)
            fieldnames = [
                "year",
                "province",
                "type",
                "science_category",
                "highest_score",
                "minimum_score",
                "lowest_score_ranking",
                "record_id",
                "source_url",
            ]
            output_csv = str(output_dir / "huabei_dianli_score_summary_rows.csv")
            _write_csv(output_csv, normalized_rows, fieldnames)
        elif source_id == "huabei_dianli_211" and target_kind == "score_major_json":
            normalized_rows = normalize_huabei_score_major_items(data)
            fieldnames = [
                "year",
                "province",
                "type",
                "science_category",
                "major",
                "requirement",
                "highest_score",
                "minimum_score",
                "lowest_score_ranking",
                "record_id",
                "source_url",
            ]
            output_csv = str(output_dir / "huabei_dianli_score_major_rows.csv")
            _write_csv(output_csv, normalized_rows, fieldnames)
        elif source_id == "nanhang_211" and target_kind == "plan_query":
            source_slug = Path(row.get("output_path", "")).stem
            normalized_rows = normalize_nanhang_plan_items(data, source_slug)
            nanhang_rows.extend(normalized_rows)

        summary_rows.append(
            {
                "source_id": source_id,
                "source_name": row.get("source_name", ""),
                "target_kind": target_kind,
                "status": row.get("status", ""),
                "output_path": row.get("output_path", ""),
                "normalized_rows": len(normalized_rows) if normalized_rows else len(data) if isinstance(data, list) else 0,
                "normalized_csv": output_csv,
            }
        )

    if nanhang_rows:
        fieldnames = [
            "year",
            "province",
            "type",
            "subject",
            "college",
            "specialty",
            "plan_number",
            "weight",
            "record_id",
            "introduction_link",
            "source_slug",
        ]
        output_csv = output_dir / "nanhang_plan_query_rows.csv"
        _write_csv(output_csv, nanhang_rows, fieldnames)
        summary_rows.append(
            {
                "source_id": "nanhang_211",
                "source_name": "南京航空航天大学招生网",
                "target_kind": "plan_query_merged",
                "status": "ok",
                "output_path": "",
                "normalized_rows": len(nanhang_rows),
                "normalized_csv": str(output_csv),
            }
        )

    _write_csv(
        summary_path,
        summary_rows,
        [
            "source_id",
            "source_name",
            "target_kind",
            "status",
            "output_path",
            "normalized_rows",
            "normalized_csv",
        ],
    )
    return summary_rows
