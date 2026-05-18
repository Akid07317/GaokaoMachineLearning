#!/usr/bin/env python3
"""Probe Shanghai University FineUI form payload variants."""

from __future__ import annotations

import csv
import re
from itertools import product
from pathlib import Path

import requests


def main() -> None:
    requests.packages.urllib3.disable_warnings()

    url = "https://bks.shu.edu.cn/pub/plans.aspx"
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://bks.shu.edu.cn/",
        }
    )

    response = session.get(url, timeout=20, verify=False)
    response.raise_for_status()
    html = response.text
    hidden = dict(
        re.findall(
            r'<input type="hidden" name="([^"]+)" id="[^"]+" value="([^"]*)"', html
        )
    )
    base = {
        "__EVENTTARGET": "Panel1$ctl00$btnOK",
        "__EVENTARGUMENT": "",
        "Panel1$ctl00$btnOK": "查询",
    }
    variants: list[tuple[str, dict[str, str]]] = []

    for control_names, value_names in product([False, True], [False, True]):
        if not control_names and not value_names:
            continue
        payload = dict(hidden)
        payload.update(base)
        if control_names:
            payload.update(
                {
                    "Panel1$ctl00$SC_Year": "2025",
                    "Panel1$ctl00$SC_ShengYD": "广西",
                    "Panel1$ctl00$SC_LeiXing": "一本",
                    "Panel1$ctl00$SC_KeMZ": "理",
                }
            )
        if value_names:
            payload.update(
                {
                    "Panel1$ctl00$SC_Year$Value": "2025",
                    "Panel1$ctl00$SC_ShengYD$Value": "广西",
                    "Panel1$ctl00$SC_LeiXing$Value": "一本",
                    "Panel1$ctl00$SC_KeMZ$Value": "理",
                }
            )
        variants.append((f"control={control_names},value={value_names}", payload))

    for text_names in [False, True]:
        payload = dict(hidden)
        payload.update(base)
        payload.update(
            {
                "Panel1$ctl00$SC_Year$Value": "2025",
                "Panel1$ctl00$SC_ShengYD$Value": "广西",
                "Panel1$ctl00$SC_LeiXing$Value": "一本",
                "Panel1$ctl00$SC_KeMZ$Value": "理",
            }
        )
        if text_names:
            payload.update(
                {
                    "Panel1$ctl00$SC_Year$Text": "2025",
                    "Panel1$ctl00$SC_ShengYD$Text": "广西",
                    "Panel1$ctl00$SC_LeiXing$Text": "一本",
                    "Panel1$ctl00$SC_KeMZ$Text": "理",
                }
            )
        variants.append((f"value_only_text={text_names}", payload))

    rows = []
    for name, payload in variants:
        post = session.post(url, data=payload, timeout=20, verify=False)
        text = post.text
        year_ok = 'SelectedValueArray":["2025"]' in text
        province_ok = 'SelectedValueArray":["广西"]' in text
        type_ok = 'SelectedValueArray":["一本"]' in text
        rows_match = re.search(
            r'var f2_state=\{"RecordCount":(\d+),"F_Rows":(\[.*?\]),"IFrameAttributes":\{\}\};var f2_columns=',
            text,
            re.S,
        )
        if rows_match:
            record_count = int(rows_match.group(1))
        else:
            rows_match = re.search(r'var f1_state=\{"F_Rows":(\[.*?\])\};var f1_columns=', text, re.S)
            if rows_match:
                record_count = rows_match.group(1).count("frow")
            else:
                record_count = -1

        rows.append(
            {
                "variant": name,
                "status_code": post.status_code,
                "year_ok": str(year_ok).lower(),
                "province_ok": str(province_ok).lower(),
                "type_ok": str(type_ok).lower(),
                "record_count": record_count,
            }
        )

    out = Path("reports/shanghai_daxue_fineui_variant_probe.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)
    print(f"Wrote {len(rows)} probe variants to {out}.")


if __name__ == "__main__":
    main()
