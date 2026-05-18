from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import csv
from urllib.parse import urlparse


INCLUDE_PHRASES = [
    "招生计划",
    "分省计划",
    "历年分数",
    "往年分数",
    "录取情况",
    "录取最低分",
    "投档",
    "招生章程",
    "专业目录",
    "本科招生专业",
    "分省信息",
    "分批次、分科类招生计划",
    "分批次、分科类录取人数和录取最低分",
]

EXCLUDE_PHRASES = [
    "首页",
    "联系我们",
    "名单公示",
    "新闻",
    "校友",
    "学生奖励",
    "就业工作",
    "学校简介",
    "学院",
    "专业介绍",
    "视频",
    "宣传片",
    "高水平运动队",
    "保送生",
    "艺术类",
    "中外合作",
    "港澳台",
    "澳门",
    "香港",
    "台湾",
    "第二学士",
    "专项",
]


@dataclass
class SecondRoundTarget:
    seed_id: str
    source_name: str
    target_url: str
    target_domain: str
    link_text: str
    source_page_title: str
    category: str
    score: int
    matched_reason: str
    fetch_priority: int


def read_priority_candidates(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _contains_any(text: str, phrases: list[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase in text]


def select_second_round_targets(
    rows: list[dict[str, str]],
    *,
    max_per_seed: int = 8,
) -> list[SecondRoundTarget]:
    grouped: dict[str, list[SecondRoundTarget]] = {}
    seen_urls: set[str] = set()

    for row in rows:
        category = row.get("category", "")
        if category not in {"priority_core", "priority_secondary"}:
            continue

        combined = " ".join(
            [
                row.get("link_text", ""),
                row.get("source_page_title", ""),
                row.get("matched_reason", ""),
                row.get("target_url", ""),
            ]
        )
        include_hits = _contains_any(combined, INCLUDE_PHRASES)
        exclude_hits = _contains_any(combined, EXCLUDE_PHRASES)
        if not include_hits or exclude_hits:
            continue

        target_url = row.get("target_url", "")
        if not target_url or target_url in seen_urls:
            continue

        priority = len(include_hits) * 10 + int(row.get("score", "0") or "0")
        if "广西" in combined:
            priority += 5
        if "录取最低分" in combined or "历年分数" in combined or "往年分数" in combined:
            priority += 8
        if "招生计划" in combined:
            priority += 8

        target = SecondRoundTarget(
            seed_id=row.get("seed_id", ""),
            source_name=row.get("source_name", ""),
            target_url=target_url,
            target_domain=row.get("target_domain", urlparse(target_url).netloc.lower()),
            link_text=row.get("link_text", ""),
            source_page_title=row.get("source_page_title", ""),
            category=category,
            score=int(row.get("score", "0") or "0"),
            matched_reason="|".join(include_hits),
            fetch_priority=priority,
        )
        grouped.setdefault(target.seed_id, []).append(target)
        seen_urls.add(target_url)

    selected: list[SecondRoundTarget] = []
    for seed_id in sorted(grouped):
        rows_for_seed = sorted(
            grouped[seed_id],
            key=lambda item: (-item.fetch_priority, -item.score, item.target_url),
        )
        selected.extend(rows_for_seed[:max_per_seed])
    return selected


def write_second_round_targets(rows: list[SecondRoundTarget], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "seed_id",
                "source_name",
                "target_url",
                "target_domain",
                "link_text",
                "source_page_title",
                "category",
                "score",
                "matched_reason",
                "fetch_priority",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
