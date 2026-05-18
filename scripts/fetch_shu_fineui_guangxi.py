#!/usr/bin/env python3
"""Fetch Guangxi-specific plan/score rows from Shanghai University FineUI pages."""

from __future__ import annotations

import argparse
import csv
import json
import re
import ssl
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path


PLANS_URL = "https://bks.shu.edu.cn/pub/plans.aspx"
SCORES_URL = "https://bks.shu.edu.cn/pub/scores.aspx"


def extract_hidden_fields(html: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for name, value in re.findall(
        r'<input type="hidden" name="([^"]+)" id="[^"]+" value="([^"]*)"', html
    ):
        fields[name] = value
    return fields


def extract_grid_state(html: str) -> dict:
    patterns = [
        r"var f2_state=(\{.*?\});var f2_columns=",
        r"var f1_state=(\{.*?\});var f1_columns=",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.S)
        if match:
            return json.loads(match.group(1))
    raise ValueError("Unable to find grid state payload in response.")


def extract_dropdown_options(html: str) -> dict[str, list[str]]:
    options: dict[str, list[str]] = {}
    for control, payload in re.findall(
        r"var (f\d+)_state=\{\"F_Items\":(\[.*?\]),\"SelectedValueArray\":\[.*?\]\};"
        r"var \1=new F\.DropDownList\(\{f_state:\1_state,id:'([^']+)',name:'([^']+)'",
        html,
        re.S,
    ):
        try:
            items = json.loads(payload)
        except json.JSONDecodeError:
            continue
        name = control  # placeholder to satisfy lint-like readability
        _ = name
        values = [item[0] for item in items if item]
        options[control] = values
    return options


def parse_rows(grid_state: dict, columns: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in grid_state.get("F_Rows", []):
        values = row.get("f0", [])
        rows.append(
            {
                column: str(values[idx]) if idx < len(values) else ""
                for idx, column in enumerate(columns)
            }
        )
    return rows


def build_opener() -> urllib.request.OpenerDirector:
    cookie_jar = CookieJar()
    context = ssl._create_unverified_context()
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=context),
        urllib.request.HTTPCookieProcessor(cookie_jar),
    )
    opener.addheaders = [
        (
            "User-Agent",
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36"
            ),
        ),
        ("Referer", "https://bks.shu.edu.cn/"),
    ]
    return opener


def fetch_page(opener: urllib.request.OpenerDirector, url: str, timeout: int) -> str:
    with opener.open(url, timeout=timeout) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(content_type, errors="ignore")


def query_page(
    opener: urllib.request.OpenerDirector,
    url: str,
    timeout: int,
    year: str,
    province: str,
    lei_xing: str,
    ke_mz: str,
) -> str:
    html = fetch_page(opener, url, timeout)
    hidden = extract_hidden_fields(html)
    payload = dict(hidden)
    payload.update(
        {
            "__EVENTTARGET": "Panel1$ctl00$btnOK",
            "__EVENTARGUMENT": "",
            "Panel1$ctl00$SC_Year": year,
            "Panel1$ctl00$SC_Year$Value": year,
            "Panel1$ctl00$SC_ShengYD": province,
            "Panel1$ctl00$SC_ShengYD$Value": province,
            "Panel1$ctl00$SC_LeiXing": lei_xing,
            "Panel1$ctl00$SC_LeiXing$Value": lei_xing,
            "Panel1$ctl00$SC_KeMZ": ke_mz,
            "Panel1$ctl00$SC_KeMZ$Value": ke_mz,
            "Panel1$ctl00$btnOK": "查询",
        }
    )
    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with opener.open(request, timeout=timeout) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(content_type, errors="ignore")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        fieldnames = ["status"]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"status": "empty"})
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument(
        "--out-dir",
        default="clean_data/shanghai_daxue_fineui",
        help="Output directory for extracted CSVs and HTML snapshots.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    raw_dir = Path("raw_data/shanghai_daxue_fineui")
    raw_dir.mkdir(parents=True, exist_ok=True)

    opener = build_opener()

    # Plans
    plans_html = query_page(
        opener,
        PLANS_URL,
        args.timeout,
        year="2025",
        province="广西",
        lei_xing="一本",
        ke_mz="理",
    )
    (raw_dir / "plans_guangxi_2025_yiben_li.html").write_text(
        plans_html, encoding="utf-8"
    )
    plans_grid = extract_grid_state(plans_html)
    plan_columns = ["录取类别", "科类/专业组", "专业名称", "计划人数", "所含专业", "培养学院", "备注"]
    plan_rows = parse_rows(plans_grid, plan_columns)
    for row in plan_rows:
        row.update({"school_key": "shanghai_daxue_211", "year": "2025", "province": "广西"})
    write_csv(out_dir / "shanghai_daxue_guangxi_plans_2025.csv", plan_rows)

    # Scores: try both 物理 and 物理化学, keep non-empty query with more rows.
    score_variants = []
    for ke_mz in ["物理", "物理化学", "理"]:
        score_html = query_page(
            opener,
            SCORES_URL,
            args.timeout,
            year="2025",
            province="广西",
            lei_xing="一本",
            ke_mz=ke_mz,
        )
        (raw_dir / f"scores_guangxi_2025_yiben_{ke_mz}.html").write_text(
            score_html, encoding="utf-8"
        )
        score_grid = extract_grid_state(score_html)
        score_columns = [
            "科类",
            "学院名称",
            "专业名称",
            "一本线",
            "录取最低分",
            "最低分排位",
            "录取平均分",
            "平均分排位",
        ]
        rows = parse_rows(score_grid, score_columns)
        for row in rows:
            row.update(
                {
                    "school_key": "shanghai_daxue_211",
                    "year": "2025",
                    "province": "广西",
                    "query_ke_mz": ke_mz,
                }
            )
        score_variants.append((ke_mz, rows))

    best_ke_mz, best_rows = max(score_variants, key=lambda item: len(item[1]))
    write_csv(out_dir / "shanghai_daxue_guangxi_scores_2025.csv", best_rows)

    summary_rows = [
        {
            "dataset": "plans",
            "query": "2025/广西/一本/理",
            "row_count": len(plan_rows),
        },
        {
            "dataset": "scores",
            "query": f"2025/广西/一本/{best_ke_mz}",
            "row_count": len(best_rows),
        },
    ]
    write_csv(out_dir / "shanghai_daxue_query_summary.csv", summary_rows)

    print(
        f"Wrote {len(plan_rows)} Shanghai plan rows and {len(best_rows)} score rows "
        f"for Guangxi 2025."
    )


if __name__ == "__main__":
    main()
