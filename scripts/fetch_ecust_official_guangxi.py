from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


BASE_URL = "https://bkzsdata.ecust.edu.cn/lqxx/s"
RAW_SUBDIR = Path("raw_data") / "engineering_api_official" / "huadong_ligong_211"
NORMALIZED_SUBDIR = Path("clean_data") / "engineering_api_official"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch ECUST official Guangxi plan/score payloads and normalize them into CSV."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_SUBDIR,
        help="Directory to store raw ECUST payloads.",
    )
    parser.add_argument(
        "--normalized-dir",
        type=Path,
        default=NORMALIZED_SUBDIR,
        help="Directory to store normalized ECUST CSV files.",
    )
    parser.add_argument(
        "--years",
        nargs="+",
        default=["2024", "2025"],
        help="Years to fetch. Defaults to 2024 and 2025.",
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="Enable SSL verification. Disabled by default because the source is often fetched with verify=False on the server.",
    )
    return parser


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: object) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plan_payload(year: str) -> list[dict[str, str]]:
    return [
        {"field": "sf", "value": "广西"},
        {"field": "nf", "value": year},
        {"field": "klmc", "value": "全部"},
        {"field": "zslb", "value": "普通类"},
        {"field": "xkyq", "value": ""},
    ]


def score_payload(year: str) -> list[dict[str, str]]:
    return [
        {"field": "sf", "value": "广西"},
        {"field": "nf", "value": year},
        {"field": "klmc", "value": "全部"},
        {"field": "zslb", "value": "普通类"},
        {"field": "pcmc", "value": ""},
        {"field": "xkyq", "value": ""},
    ]


def normalize_plan_rows(rows: list[dict[str, object]], *, year: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows:
        normalized.append(
            {
                "year": str(row.get("nf", year) or year),
                "province": str(row.get("sf", "广西") or "广西"),
                "type": str(row.get("zslb", "普通类") or "普通类"),
                "subject_type": "物理类",
                "selection_group": str(row.get("xkyq", "") or ""),
                "campus": str(row.get("xqlx", "") or ""),
                "specialty": str(row.get("zymc", "") or ""),
                "plan_count": str(row.get("jhrs", "") or ""),
                "requirement": str(row.get("xkyq", "") or ""),
                "remarks": str(row.get("zybz", "") or ""),
                "source_payload": f"ecust_zsjh_{year}_guangxi",
            }
        )
    return normalized


def normalize_score_summary_rows(rows: list[dict[str, object]], *, year: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows:
        normalized.append(
            {
                "year": str(row.get("nf", year) or year),
                "province": str(row.get("sf", "广西") or "广西"),
                "type": str(row.get("zslb", "普通类") or "普通类"),
                "subject_type": "物理类",
                "campus": str(row.get("xqlx", "") or ""),
                "minimum_score": str(row.get("zdf", "") or ""),
                "minimum_rank": str(row.get("zdfwc", "") or ""),
                "average_score": str(row.get("pjf", "") or ""),
                "maximum_score": str(row.get("zgf", "") or ""),
                "remarks": str(row.get("pcmc", "") or ""),
                "source_payload": f"ecust_lnfs_{year}_guangxi",
            }
        )
    return normalized


def normalize_score_major_rows(rows: list[dict[str, object]], *, year: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows:
        normalized.append(
            {
                "year": str(row.get("nf", year) or year),
                "province": str(row.get("sf", "广西") or "广西"),
                "type": str(row.get("zslb", "普通类") or "普通类"),
                "subject_type": "物理类",
                "selection_group": str(row.get("xkyq", "") or ""),
                "campus": str(row.get("xqlx", "") or ""),
                "major": str(row.get("zymc", "") or ""),
                "minimum_score": str(row.get("zdf", "") or ""),
                "minimum_rank": str(row.get("zdfwc", "") or ""),
                "average_score": str(row.get("pjf", "") or ""),
                "maximum_score": str(row.get("zgf", "") or ""),
                "remarks": str(row.get("pcmc", "") or ""),
                "source_payload": f"ecust_lnfs_{year}_guangxi",
            }
        )
    return normalized


def main() -> None:
    args = build_parser().parse_args()
    requests = __import__("requests")

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://bkzsdata.ecust.edu.cn",
            "Referer": "https://bkzsdata.ecust.edu.cn/zsdata/lqxx/",
        }
    )

    config_response = session.post(
        f"{BASE_URL}/api/front/lqxx2/getFzcxpzList",
        json={},
        timeout=30,
        verify=args.verify_ssl,
    )
    config_response.raise_for_status()
    config_payload = config_response.json()
    write_json(args.raw_dir / "fzcxpz_list.json", config_payload)

    all_plan_rows: list[dict[str, str]] = []
    all_score_summary_rows: list[dict[str, str]] = []
    all_score_major_rows: list[dict[str, str]] = []

    for year in args.years:
        plan_response = session.post(
            f"{BASE_URL}/api/front/lqxx2/getList?type=zsjh",
            json=plan_payload(year),
            timeout=30,
            verify=args.verify_ssl,
        )
        plan_response.raise_for_status()
        plan_payload_json = plan_response.json()
        write_json(args.raw_dir / f"ecust_zsjh_{year}_guangxi.json", plan_payload_json)
        all_plan_rows.extend(normalize_plan_rows(plan_payload_json.get("list", []), year=year))

        score_response = session.post(
            f"{BASE_URL}/api/front/lqxx2/getList?type=lnfs",
            json=score_payload(year),
            timeout=30,
            verify=args.verify_ssl,
        )
        score_response.raise_for_status()
        score_payload_json = score_response.json()
        write_json(args.raw_dir / f"ecust_lnfs_{year}_guangxi.json", score_payload_json)
        all_score_summary_rows.extend(
            normalize_score_summary_rows(score_payload_json.get("sumList", []), year=year)
        )
        all_score_major_rows.extend(
            normalize_score_major_rows(score_payload_json.get("list", []), year=year)
        )

    write_csv(
        args.normalized_dir / "huadong_ligong_plan_rows.csv",
        all_plan_rows,
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
    write_csv(
        args.normalized_dir / "huadong_ligong_score_summary_rows.csv",
        all_score_summary_rows,
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
            "remarks",
            "source_payload",
        ],
    )
    write_csv(
        args.normalized_dir / "huadong_ligong_score_major_rows.csv",
        all_score_major_rows,
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

    print(
        "Fetched and normalized ECUST Guangxi payloads: "
        f"{len(all_plan_rows)} plan rows, "
        f"{len(all_score_summary_rows)} score summary rows, "
        f"{len(all_score_major_rows)} score major rows."
    )


if __name__ == "__main__":
    main()
