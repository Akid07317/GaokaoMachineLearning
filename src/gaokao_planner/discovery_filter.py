from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import csv


HIGH_VALUE_TERMS = [
    "招生计划",
    "分省计划",
    "历年分数",
    "往年分数",
    "录取情况",
    "投档",
    "招生章程",
    "专业目录",
    "本科招生专业",
    "专业介绍",
    "广西",
]

NOISE_TERMS = [
    "高职高专",
    "征集",
    "专升本",
    "成人",
    "adultgk",
    "自考",
    "研究生",
    "教师资格",
    "社会考试",
    "艺术统考",
    "学业水平",
]

LOW_SIGNAL_TERMS = [
    "首页",
    "联系我们",
    "名单公示",
    "返回旧版",
    "上一页",
    "下一页",
    "尾页",
]

SPECIAL_TERMS = [
    "强基",
    "专项计划",
    "高校专项",
    "国家专项",
    "地方专项",
    "保送",
    "少年生",
    "港澳台",
    "香港",
    "澳门",
    "台湾",
    "第二学士",
    "艺术类",
    "中外合作",
]


@dataclass
class FilteredCandidate:
    seed_id: str
    source_name: str
    year_hint: str
    target_url: str
    target_domain: str
    link_text: str
    source_page_title: str
    score: int
    category: str
    matched_reason: str
    target_suffix: str
    notes: str


def read_candidates(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def categorize_candidate(row: dict[str, str]) -> FilteredCandidate:
    primary_text = " ".join(
        [
            row.get("link_text", ""),
            row.get("target_url", ""),
            row.get("matched_keywords", ""),
        ]
    )
    if not primary_text.strip():
        primary_text = row.get("source_page_title", "")
    combined = " ".join([primary_text, row.get("source_page_title", "")])
    reasons: list[str] = []
    lowered = combined.lower()
    link_text = row.get("link_text", "")

    if any(term.lower() in lowered for term in NOISE_TERMS):
        category = "noise"
        reasons = [term for term in NOISE_TERMS if term.lower() in lowered]
    elif any(term.lower() in lowered for term in SPECIAL_TERMS):
        category = "special_review"
        reasons = [term for term in SPECIAL_TERMS if term.lower() in lowered]
    else:
        hits = [term for term in HIGH_VALUE_TERMS if term.lower() in primary_text.lower()]
        low_signal_hits = [term for term in LOW_SIGNAL_TERMS if term in link_text]
        has_guangxi = "广西" in combined
        has_core = any(term in hits for term in HIGH_VALUE_TERMS[:-1])
        if has_guangxi and has_core:
            category = "priority_core"
            reasons = hits
        elif hits:
            category = "priority_secondary"
            reasons = hits
        elif low_signal_hits:
            category = "review"
            reasons = low_signal_hits
        else:
            category = "review"

    return FilteredCandidate(
        seed_id=row.get("seed_id", ""),
        source_name=row.get("source_name", ""),
        year_hint=row.get("year_hint", ""),
        target_url=row.get("target_url", ""),
        target_domain=row.get("target_domain", ""),
        link_text=row.get("link_text", ""),
        source_page_title=row.get("source_page_title", ""),
        score=int(row.get("score", "0") or "0"),
        category=category,
        matched_reason="|".join(reasons),
        target_suffix=row.get("target_suffix", ""),
        notes=row.get("notes", ""),
    )


def sort_candidates(rows: list[FilteredCandidate]) -> list[FilteredCandidate]:
    category_order = {
        "priority_core": 0,
        "priority_secondary": 1,
        "special_review": 2,
        "review": 3,
        "noise": 4,
    }
    return sorted(
        rows,
        key=lambda row: (
            category_order.get(row.category, 9),
            -row.score,
            row.source_name,
            row.target_url,
        ),
    )


def write_candidates(rows: list[FilteredCandidate], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "seed_id",
                "source_name",
                "year_hint",
                "target_url",
                "target_domain",
                "link_text",
                "source_page_title",
                "score",
                "category",
                "matched_reason",
                "target_suffix",
                "notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
