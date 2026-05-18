#!/usr/bin/env python3
"""Build SUES official form reachability preview without submitting forms.

上海工程技术大学官方招生系统首页 exposes plan and score forms with Guangxi,
undergraduate and physical-subject option IDs. Submitting those forms would be
form replay, so this script records the auditable parameters and keeps the item
in a manual-approval queue instead of fetching result rows.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "clean_data" / "engineering_guangxi_seed"
REPORT_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
RAW_DIR = ROOT / "raw_sources" / "reference_trend" / "p0_official_drilldown"

RAW_HTML = RAW_DIR / "sues_webrecruit_index.html"
OUT = SEED_DIR / "reference_trend_520_p0_sues_form_reachability_preview.csv"
ROLLUP_OUT = REPORT_DIR / "reference_trend_520_p0_sues_form_reachability_rollup.csv"
QA_OUT = REPORT_DIR / "reference_trend_520_p0_sues_form_reachability_qa.csv"
EXCLUSION_OUT = REPORT_DIR / "reference_trend_520_p0_sues_form_reachability_exclusion_log.csv"
DOC_OUT = DOCS_DIR / "reference_trend_520_p0_sues_form_reachability_preview.md"
HANDOFF = DOCS_DIR / "gpt54_reference_trend_pool_handoff.md"

SOURCE_URL = "https://zsb.sues.edu.cn/webrecruit/index.do"
SOURCE_ID = "reference_trend_520_web_candidate_0006"
QUEUE_RECORD_ID = "reference_trend_520_plan_source_queue_0001"

FIELDS = [
    "record_id",
    "source_id",
    "queue_record_id",
    "queue_rank",
    "university_code",
    "university_name",
    "year",
    "province",
    "batch",
    "subject_category",
    "source_url",
    "source_owner",
    "source_title",
    "raw_file_path",
    "form_role",
    "form_action",
    "form_method",
    "rand_session_present",
    "target_year_value",
    "target_province_option_value",
    "target_province_label",
    "target_level_option_value",
    "target_level_label",
    "target_subject_option_value",
    "target_subject_label",
    "available_years",
    "candidate_form_params",
    "source_contains_group_code",
    "source_contains_plan_count",
    "source_contains_min_score",
    "source_contains_min_rank",
    "source_packet_status",
    "collector_confidence",
    "requires_manual_approval",
    "approval_required_for",
    "eligible_for_intake_preview",
    "reference_trend_pool_eligible",
    "calibration_eligible",
    "canonical_ml_entry_open",
    "decision_pool_boundary",
    "next_action",
    "evidence_note",
]


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, object]] = []
        self.current_form: dict[str, object] | None = None
        self.current_select: dict[str, object] | None = None
        self.current_option: dict[str, str] | None = None
        self.current_option_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag == "form":
            self.current_form = {
                "action": attr.get("action", ""),
                "method": attr.get("method", "get").lower(),
                "inputs": {},
                "selects": {},
            }
        elif self.current_form is not None and tag == "input":
            name = attr.get("name", "")
            if name:
                self.current_form["inputs"][name] = attr.get("value", "")  # type: ignore[index]
        elif self.current_form is not None and tag == "select":
            self.current_select = {"name": attr.get("name", ""), "options": []}
        elif self.current_select is not None and tag == "option":
            self.current_option = {"value": attr.get("value", "")}
            self.current_option_text = []

    def handle_data(self, data: str) -> None:
        if self.current_option is not None:
            self.current_option_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self.current_option is not None and self.current_select is not None:
            self.current_option["label"] = " ".join("".join(self.current_option_text).split())
            self.current_select["options"].append(self.current_option)  # type: ignore[index]
            self.current_option = None
            self.current_option_text = []
        elif tag == "select" and self.current_select is not None and self.current_form is not None:
            name = str(self.current_select.get("name", ""))
            if name:
                self.current_form["selects"][name] = self.current_select["options"]  # type: ignore[index]
            self.current_select = None
        elif tag == "form" and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_handoff_once(marker: str, content: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
    if marker in text:
        return
    with HANDOFF.open("a", encoding="utf-8") as f:
        f.write(content)


def option_value(form: dict[str, object], select_name: str, label: str) -> str:
    options = (form.get("selects") or {}).get(select_name, [])  # type: ignore[union-attr]
    for option in options:
        if option.get("label") == label:
            return option.get("value", "")
    return ""


def select_labels(form: dict[str, object], select_name: str) -> list[str]:
    options = (form.get("selects") or {}).get(select_name, [])  # type: ignore[union-attr]
    return [option.get("label", "") for option in options if option.get("label")]


def absolute_action(action: str) -> str:
    if action.startswith("http"):
        return action
    return f"https://zsb.sues.edu.cn:443/webrecruit/{action.lstrip('/')}"


def parse_forms() -> list[dict[str, object]]:
    parser = FormParser()
    parser.feed(RAW_HTML.read_text(encoding="utf-8", errors="replace"))
    rows: list[dict[str, object]] = []
    for form in parser.forms:
        action = absolute_action(str(form.get("action", "")))
        if "getzslq.do" in action:
            role = "official_plan_form"
            record_suffix = "plan"
            target_params = {
                "id": "1",
                "YEAR": "2025",
                "SSID": option_value(form, "SSID", "广西"),
                "CCID": option_value(form, "CCID", "本科"),
                "KLID": option_value(form, "KLID", "物理类"),
                "ZYID": "",
            }
        elif "getzsfsx.do" in action:
            role = "official_score_rank_form"
            record_suffix = "score"
            target_params = {
                "id": "2",
                "YEAR": "2025",
                "SSID": option_value(form, "SSID", "广西"),
                "CCID": option_value(form, "CCID", "本科"),
                "KLID": option_value(form, "KLID", "物理类"),
                "ZYID": "",
            }
        else:
            continue
        inputs = form.get("inputs") or {}
        rand_session = str(inputs.get("randSesion", ""))  # type: ignore[union-attr]
        if rand_session:
            target_params["randSesion"] = rand_session
        available_years = [label for label in select_labels(form, "YEAR") if re.fullmatch(r"\d{4}", label)]
        rows.append(
            {
                "record_id": f"reference_trend_520_p0_sues_form_reachability_{record_suffix}",
                "source_id": SOURCE_ID,
                "queue_record_id": QUEUE_RECORD_ID,
                "queue_rank": "1",
                "university_code": "10856",
                "university_name": "上海工程技术大学",
                "year": "2025",
                "province": "广西",
                "batch": "本科普通批",
                "subject_category": "物理类",
                "source_url": SOURCE_URL,
                "source_owner": "上海工程技术大学招生网",
                "source_title": "上海工程技术大学官方招生系统首页",
                "raw_file_path": rel(RAW_HTML),
                "form_role": role,
                "form_action": action,
                "form_method": str(form.get("method", "post")).upper(),
                "rand_session_present": "true" if rand_session else "false",
                "target_year_value": target_params["YEAR"],
                "target_province_option_value": target_params["SSID"],
                "target_province_label": "广西",
                "target_level_option_value": target_params["CCID"],
                "target_level_label": "本科",
                "target_subject_option_value": target_params["KLID"],
                "target_subject_label": "物理类",
                "available_years": "|".join(available_years),
                "candidate_form_params": "&".join(f"{key}={value}" for key, value in target_params.items()),
                "source_contains_group_code": "unknown_until_approved_form_replay",
                "source_contains_plan_count": "unknown_until_approved_form_replay" if role == "official_plan_form" else "false",
                "source_contains_min_score": "unknown_until_approved_form_replay" if role == "official_score_rank_form" else "false",
                "source_contains_min_rank": "unknown_until_approved_form_replay" if role == "official_score_rank_form" else "false",
                "source_packet_status": "official_form_params_identified_hold_for_manual_approval",
                "collector_confidence": "T2_official_form_endpoint_identified_not_submitted",
                "requires_manual_approval": "true",
                "approval_required_for": "form_replay_or_browser_state_check",
                "eligible_for_intake_preview": "false_until_approved_form_result_cached_and_QA",
                "reference_trend_pool_eligible": "0",
                "calibration_eligible": "0",
                "canonical_ml_entry_open": "false",
                "decision_pool_boundary": "do_not_merge_with_32_school_decision_pool",
                "next_action": "ask_user_approval_for_audited_form_post_or_browser_check; otherwise keep as reachability evidence only",
                "evidence_note": "Official cached page exposes YEAR/SSID/CCID/KLID parameters for 2025 Guangxi undergraduate physical query, but result rows require submitting a form.",
            }
        )
    return rows


def build_rollup(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    roles = Counter(str(row["form_role"]) for row in rows)
    approval = Counter(str(row["requires_manual_approval"]) for row in rows)
    return [
        {"metric": "official_index_cached", "value": 1 if RAW_HTML.exists() else 0, "note": rel(RAW_HTML)},
        {"metric": "official_forms_identified", "value": len(rows), "note": dict(roles)},
        {"metric": "manual_approval_required_rows", "value": approval.get("true", 0), "note": "form replay/browser state check required before result rows"},
        {"metric": "target_year_available_rows", "value": sum(1 for row in rows if "2025" in str(row["available_years"])), "note": ""},
        {"metric": "guangxi_option_available_rows", "value": sum(1 for row in rows if row["target_province_option_value"]), "note": ""},
        {"metric": "physical_option_available_rows", "value": sum(1 for row in rows if row["target_subject_option_value"]), "note": ""},
        {"metric": "reference_trend_pool_eligible_rows", "value": 0, "note": "No result rows fetched."},
        {"metric": "calibration_eligible_rows", "value": 0, "note": "No score/rank rows fetched."},
        {"metric": "canonical_ml_entry_open_rows", "value": 0, "note": "Canonical/ML remains closed."},
    ]


def build_qa(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    roles = {row["form_role"] for row in rows}
    return [
        {"check": "official_index_cached", "status": "PASS" if RAW_HTML.exists() else "FAIL", "detail": rel(RAW_HTML)},
        {"check": "plan_form_identified", "status": "PASS" if "official_plan_form" in roles else "FAIL", "detail": ""},
        {"check": "score_form_identified", "status": "PASS" if "official_score_rank_form" in roles else "WARN", "detail": ""},
        {"check": "target_options_present", "status": "PASS" if all(row["target_province_option_value"] and row["target_level_option_value"] and row["target_subject_option_value"] for row in rows) else "FAIL", "detail": "广西/本科/物理类 option values present"},
        {"check": "form_replay_not_executed", "status": "PASS", "detail": "Only index page cached; no POST result fetch performed."},
        {"check": "manual_approval_gate", "status": "PASS", "detail": "Rows require manual approval before form replay/browser check."},
        {"check": "no_reference_trend_pool_or_canonical_ml", "status": "PASS", "detail": "No trend pool/canonical/ML writes."},
    ]


def build_exclusion(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "record_id": row["record_id"],
            "university_name": row["university_name"],
            "form_role": row["form_role"],
            "form_action": row["form_action"],
            "exclusion_reason": "hold_for_manual_approval_before_form_replay",
            "next_action": row["next_action"],
            "decision_pool_boundary": row["decision_pool_boundary"],
        }
        for row in rows
    ]


def write_doc(rows: list[dict[str, object]], rollup: list[dict[str, object]], qa: list[dict[str, object]]) -> None:
    DOC_OUT.write_text(
        "\n".join(
            [
                "# reference_trend_520 P0 SUES form reachability preview",
                "",
                f"Generated: {date.today().isoformat()}",
                "",
                "## Scope",
                "",
                "上海工程技术大学官方招生系统首页已缓存并解析出招生计划/历年分数表单参数。"
                "本轮不提交表单，只记录可审计参数和人工批准边界。",
                "",
                "## Result",
                "",
                f"- Official source URL: {SOURCE_URL}",
                f"- Cached HTML: `{rel(RAW_HTML)}`",
                f"- Forms identified: {len(rows)}",
                "- Target option set: 2025 / 广西 / 本科 / 物理类",
                "- Result fetch: not executed",
                "- Manual approval required: yes, for form replay or browser state check",
                "",
                "## Outputs",
                "",
                f"- `{rel(OUT)}`",
                f"- `{rel(ROLLUP_OUT)}`",
                f"- `{rel(QA_OUT)}`",
                f"- `{rel(EXCLUSION_OUT)}`",
                "",
                "## Gate Boundary",
                "",
                "所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、"
                "`canonical_ml_entry_open=false`。原因是目前只有官方表单入口与参数，尚未获得经批准缓存的结果行；"
                "提交表单属于 form replay/browser-state 检查，需要人工批准。",
                "",
                "## QA",
                "",
                *[f"- {row['check']}: {row['status']} - {row['detail']}" for row in qa],
                "",
                "## Rollup",
                "",
                *[f"- {row['metric']}: {row['value']} ({row['note']})" for row in rollup],
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    if not RAW_HTML.exists():
        raise FileNotFoundError(f"Missing cached HTML: {RAW_HTML}")
    rows = parse_forms()
    rollup = build_rollup(rows)
    qa = build_qa(rows)
    exclusion = build_exclusion(rows)

    write_csv(OUT, rows, FIELDS)
    write_csv(ROLLUP_OUT, rollup, ["metric", "value", "note"])
    write_csv(QA_OUT, qa, ["check", "status", "detail"])
    write_csv(EXCLUSION_OUT, exclusion, ["record_id", "university_name", "form_role", "form_action", "exclusion_reason", "next_action", "decision_pool_boundary"])
    write_doc(rows, rollup, qa)

    marker = "## 78. 2026-05-16 P0 上海工程技术大学 official form reachability preview"
    append_handoff_once(
        marker,
        f"""

{marker}

已新增上海工程技术大学 P0 official form reachability preview：

- `{OUT.relative_to(ROOT)}`
- `{ROLLUP_OUT.relative_to(ROOT)}`
- `{QA_OUT.relative_to(ROOT)}`
- `{EXCLUSION_OUT.relative_to(ROOT)}`
- `{DOC_OUT.relative_to(ROOT)}`

覆盖结果：官方招生系统首页已缓存，确认首页同时暴露招生计划 `getzslq.do` 与历年分数 `getzsfsx.do` 表单；2025 / 广西 / 本科 / 物理类 option 参数齐全。

准入边界：本轮没有执行 form replay/browser-state 检查，不获取结果行；所有行继续 `reference_trend_pool_eligible=0`、`calibration_eligible=0`、`canonical_ml_entry_open=false`，不进入 32 所 decision_pool。若用户批准，可下一轮用表单 POST 或浏览器态获取官方结果页并做 source-packet QA。
""",
    )


if __name__ == "__main__":
    main()
