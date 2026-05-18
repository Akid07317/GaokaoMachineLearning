from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
ENDPOINT_RE = re.compile(r"url:\s*\$\.url\('([^']*ajax_[^']*)'\)")
OUT_FIELD_RE = re.compile(r"out\(\$value,'([^']+)'")
DATA_KEY_RE = re.compile(r"\$\.out\(res,'data\.([^']+)'\)")
CONFIG_BLOCK_RE = re.compile(
    r"name:\s*'([^']+)'\s*,\s*nameCa:\s*'([^']+)'",
    re.DOTALL,
)


@dataclass
class StaticAjaxPageRecord:
    school_key: str
    source_bucket: str
    file_path: str
    page_kind: str
    page_title: str
    param_endpoints: str
    data_endpoints: str
    config_names: str
    config_labels: str
    response_keys: str
    template_fields: str
    has_guangxi_literal: str
    has_physics_literal: str
    has_with_sex_toggle: str
    has_with_campus_toggle: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def infer_page_kind(path: Path) -> str:
    name = path.name.lower()
    if "zsjh" in name:
        return "plan"
    if "lnfs" in name:
        return "score"
    if "lqcx" in name:
        return "admission"
    return "other"


def sorted_pipe(values: set[str]) -> str:
    return "|".join(sorted(value for value in values if value))


def build_page_record(path: Path, raw_root: Path) -> StaticAjaxPageRecord:
    text = read_text(path)
    title_match = TITLE_RE.search(text)
    endpoints = set(ENDPOINT_RE.findall(text))
    param_endpoints = {value for value in endpoints if value.endswith("_param")}
    data_endpoints = endpoints - param_endpoints
    config_pairs = CONFIG_BLOCK_RE.findall(text)
    config_names = [name for name, _ in config_pairs]
    config_labels = [label for _, label in config_pairs]
    response_keys = set(DATA_KEY_RE.findall(text))
    template_fields = set(OUT_FIELD_RE.findall(text))

    return StaticAjaxPageRecord(
        school_key=path.parent.name,
        source_bucket=str(path.relative_to(raw_root).parts[0]),
        file_path=str(path),
        page_kind=infer_page_kind(path),
        page_title=title_match.group(1).strip() if title_match else "",
        param_endpoints=sorted_pipe(param_endpoints),
        data_endpoints=sorted_pipe(data_endpoints),
        config_names="|".join(config_names),
        config_labels="|".join(config_labels),
        response_keys=sorted_pipe(response_keys),
        template_fields=sorted_pipe(template_fields),
        has_guangxi_literal=str("广西" in text).lower(),
        has_physics_literal=str("物理" in text).lower(),
        has_with_sex_toggle=str("withSex" in text).lower(),
        has_with_campus_toggle=str("withCampus" in text).lower(),
    )


def discover_static_ajax_pages(raw_root: Path) -> list[Path]:
    pages: list[Path] = []
    for path in raw_root.rglob("*.html"):
        name = path.name.lower()
        if "static_front" not in name:
            continue
        if not any(token in name for token in ("zsjh", "lnfs", "lqcx")):
            continue
        pages.append(path)
    return sorted(pages)


def build_school_summary(records: list[StaticAjaxPageRecord]) -> list[dict[str, str | int]]:
    grouped: dict[str, list[StaticAjaxPageRecord]] = defaultdict(list)
    for record in records:
        grouped[record.school_key].append(record)

    summary_rows: list[dict[str, str | int]] = []
    for school_key, items in sorted(grouped.items()):
        param_endpoints: set[str] = set()
        data_endpoints: set[str] = set()
        config_signatures: set[str] = set()
        response_keys: set[str] = set()
        template_fields: set[str] = set()
        source_buckets: set[str] = set()
        for item in items:
            param_endpoints.update(filter(None, item.param_endpoints.split("|")))
            data_endpoints.update(filter(None, item.data_endpoints.split("|")))
            if item.config_names:
                config_signatures.add(item.config_names)
            response_keys.update(filter(None, item.response_keys.split("|")))
            template_fields.update(filter(None, item.template_fields.split("|")))
            source_buckets.add(item.source_bucket)
        unique_signatures = sorted(config_signatures)
        summary_rows.append(
            {
                "school_key": school_key,
                "page_count": len(items),
                "plan_page_count": sum(1 for item in items if item.page_kind == "plan"),
                "score_page_count": sum(1 for item in items if item.page_kind == "score"),
                "admission_page_count": sum(1 for item in items if item.page_kind == "admission"),
                "source_buckets": sorted_pipe(source_buckets),
                "param_endpoints": sorted_pipe(param_endpoints),
                "data_endpoints": sorted_pipe(data_endpoints),
                "config_name_signature": unique_signatures[0] if unique_signatures else "",
                "response_keys": sorted_pipe(response_keys),
                "template_fields": sorted_pipe(template_fields),
                "has_guangxi_literal_any": str(any(item.has_guangxi_literal == "true" for item in items)).lower(),
                "has_physics_literal_any": str(any(item.has_physics_literal == "true" for item in items)).lower(),
                "has_with_sex_toggle_any": str(any(item.has_with_sex_toggle == "true" for item in items)).lower(),
                "has_with_campus_toggle_any": str(any(item.has_with_campus_toggle == "true" for item in items)).lower(),
            }
        )
    return summary_rows


def write_page_records(rows: list[StaticAjaxPageRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "school_key",
                "source_bucket",
                "file_path",
                "page_kind",
                "page_title",
                "param_endpoints",
                "data_endpoints",
                "config_names",
                "config_labels",
                "response_keys",
                "template_fields",
                "has_guangxi_literal",
                "has_physics_literal",
                "has_with_sex_toggle",
                "has_with_campus_toggle",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_summary_rows(rows: list[dict[str, str | int]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
