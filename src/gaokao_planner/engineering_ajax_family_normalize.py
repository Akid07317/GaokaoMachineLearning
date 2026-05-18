from __future__ import annotations

from pathlib import Path
import csv
import json


def read_fetch_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _write_csv(path: str | Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dedupe(rows: list[dict[str, object]], keys: list[str]) -> list[dict[str, object]]:
    seen: set[tuple[object, ...]] = set()
    output: list[dict[str, object]] = []
    for row in rows:
        key = tuple(row.get(name, "") for name in keys)
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output


AJAX_SOURCES = {
    "beijing_jiaotong_211": {
        "prefix": "beijing_jiaotong",
    },
    "zhongguo_dizhi_beijing_211": {
        "prefix": "zhongguo_dizhi_beijing",
    },
}


def normalize_plan(
    rows: list[dict[str, str]],
    *,
    source_id: str,
    prefix: str,
    project_root: str | Path,
    output_dir: str | Path,
) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    project_root = Path(project_root)
    for row in rows:
        if row.get("source_id") != source_id or row.get("target_kind") != "plan_probe" or row.get("status") != "ok":
            continue
        payload = _load_json(project_root / row["output_path"])
        data = payload.get("data", {})
        for item in data.get("zsjhList", []):
            normalized.append(
                {
                    "year": item.get("nf", ""),
                    "province": item.get("ssmc", ""),
                    "type": item.get("zylx", ""),
                    "subject_type": item.get("klmc", ""),
                    "selection_group": item.get("zyzname", "") or item.get("zyz", ""),
                    "campus": item.get("campus", ""),
                    "specialty": item.get("zydhmc", ""),
                    "plan_count": item.get("zsjhs", ""),
                    "requirement": item.get("kskmyqmc", "") or item.get("xkkm", ""),
                    "remarks": item.get("remarks", ""),
                    "source_payload": Path(row["output_path"]).stem,
                }
            )
    normalized = _dedupe(
        normalized,
        ["year", "province", "type", "subject_type", "selection_group", "campus", "specialty", "plan_count", "requirement", "remarks"],
    )
    path = Path(output_dir) / f"{prefix}_plan_rows.csv"
    _write_csv(
        path,
        normalized,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "specialty",
            "plan_count",
            "requirement",
            "remarks",
            "source_payload",
        ],
    )
    return normalized


def normalize_score_summary(
    rows: list[dict[str, str]],
    *,
    source_id: str,
    prefix: str,
    project_root: str | Path,
    output_dir: str | Path,
) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    project_root = Path(project_root)
    for row in rows:
        if row.get("source_id") != source_id or row.get("target_kind") != "score_probe" or row.get("status") != "ok":
            continue
        payload = _load_json(project_root / row["output_path"])
        data = payload.get("data", {})
        for item in data.get("zsSsgradeList", []):
            normalized.append(
                {
                    "year": item.get("nf", ""),
                    "province": item.get("ssmc", ""),
                    "type": item.get("zylx", ""),
                    "subject_type": item.get("klmc", ""),
                    "campus": item.get("campus", ""),
                    "minimum_score": item.get("minScore", ""),
                    "minimum_rank": item.get("minOrder", "") or item.get("minRank", ""),
                    "average_score": item.get("avgScore", ""),
                    "maximum_score": item.get("maxScore", ""),
                    "source_payload": Path(row["output_path"]).stem,
                }
            )
    normalized = _dedupe(
        normalized,
        ["year", "province", "type", "subject_type", "campus", "minimum_score", "minimum_rank", "average_score", "maximum_score"],
    )
    path = Path(output_dir) / f"{prefix}_score_summary_rows.csv"
    _write_csv(
        path,
        normalized,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "campus",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "source_payload",
        ],
    )
    return normalized


def normalize_score_major(
    rows: list[dict[str, str]],
    *,
    source_id: str,
    prefix: str,
    project_root: str | Path,
    output_dir: str | Path,
) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    project_root = Path(project_root)
    for row in rows:
        if row.get("source_id") != source_id or row.get("target_kind") != "score_probe" or row.get("status") != "ok":
            continue
        payload = _load_json(project_root / row["output_path"])
        data = payload.get("data", {})
        for item in data.get("sszygradeList", []):
            normalized.append(
                {
                    "year": item.get("nf", ""),
                    "province": item.get("ssmc", ""),
                    "type": item.get("zylx", ""),
                    "subject_type": item.get("klmc", ""),
                    "selection_group": item.get("zyzname", ""),
                    "campus": item.get("campus", ""),
                    "major": item.get("zymc", ""),
                    "minimum_score": item.get("minScore", ""),
                    "minimum_rank": item.get("minOrder", "") or item.get("minRank", ""),
                    "average_score": item.get("avgScore", ""),
                    "maximum_score": item.get("maxScore", ""),
                    "remarks": item.get("remarks", ""),
                    "source_payload": Path(row["output_path"]).stem,
                }
            )
    normalized = _dedupe(
        normalized,
        ["year", "province", "type", "subject_type", "selection_group", "campus", "major", "minimum_score", "minimum_rank", "average_score", "maximum_score", "remarks"],
    )
    path = Path(output_dir) / f"{prefix}_score_major_rows.csv"
    _write_csv(
        path,
        normalized,
        [
            "year",
            "province",
            "type",
            "subject_type",
            "selection_group",
            "campus",
            "major",
            "minimum_score",
            "minimum_rank",
            "average_score",
            "maximum_score",
            "remarks",
            "source_payload",
        ],
    )
    return normalized


def normalize_ajax_family_payloads(
    fetch_log_path: str | Path,
    *,
    project_root: str | Path,
    output_dir: str | Path,
    summary_path: str | Path,
) -> list[dict[str, object]]:
    rows = read_fetch_rows(fetch_log_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    for source_id, config in AJAX_SOURCES.items():
        prefix = config["prefix"]
        plan_rows = normalize_plan(
            rows,
            source_id=source_id,
            prefix=prefix,
            project_root=project_root,
            output_dir=output_dir,
        )
        score_summary_rows = normalize_score_summary(
            rows,
            source_id=source_id,
            prefix=prefix,
            project_root=project_root,
            output_dir=output_dir,
        )
        score_major_rows = normalize_score_major(
            rows,
            source_id=source_id,
            prefix=prefix,
            project_root=project_root,
            output_dir=output_dir,
        )
        summary_rows.extend(
            [
                {
                    "dataset": f"{prefix}_plan_rows",
                    "rows": len(plan_rows),
                    "csv_path": str(output_dir / f"{prefix}_plan_rows.csv"),
                },
                {
                    "dataset": f"{prefix}_score_summary_rows",
                    "rows": len(score_summary_rows),
                    "csv_path": str(output_dir / f"{prefix}_score_summary_rows.csv"),
                },
                {
                    "dataset": f"{prefix}_score_major_rows",
                    "rows": len(score_major_rows),
                    "csv_path": str(output_dir / f"{prefix}_score_major_rows.csv"),
                },
            ]
        )
    _write_csv(summary_path, summary_rows, ["dataset", "rows", "csv_path"])
    return summary_rows
