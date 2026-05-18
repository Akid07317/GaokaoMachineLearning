from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a prioritized probe backlog for engineering target schools."
    )
    parser.add_argument(
        "--pipeline-status",
        type=Path,
        default=Path("reports") / "engineering_pipeline_status.csv",
        help="Pipeline status CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "engineering_probe_backlog.csv",
        help="Output backlog CSV.",
    )
    return parser


def classify_probe_priority(row: dict[str, str]) -> tuple[str, str]:
    status = row.get("pipeline_status", "")
    tier = row.get("engineering_tier", "")
    static_pages = int(row.get("static_ajax_page_count", "0") or 0)
    ajax_403 = int(row.get("ajax_403", "0") or 0)
    same_family_403 = int(row.get("same_family_403", "0") or 0)
    same_family_url_error = int(row.get("same_family_url_error", "0") or 0)
    same_family_page_ok = int(row.get("same_family_page_ok", "0") or 0)
    cached_pdf_guangxi = int(row.get("cached_pdf_guangxi_count", "0") or 0)
    cached_pdf_count = int(row.get("cached_pdf_count", "0") or 0)
    pdf_structured_guangxi_rows = int(row.get("pdf_structured_guangxi_rows", "0") or 0)
    form_replay_variants = int(row.get("form_replay_variants_tested", "0") or 0)
    form_replay_success = int(row.get("form_replay_success_count", "0") or 0)
    signature = row.get("static_ajax_config_signature", "")
    has_signature = signature == "ssmc|zsnf|klmc|sex|campus|zslx"

    if status in {"seeded_plan_and_score", "seeded_plan_only", "seeded_score_only"}:
        return "P5_hold", "当前学校已进入结构化种子层，后续优先做校验或扩展，不再作为补抓阻塞项排在前面"
    if tier == "core" and same_family_page_ok >= 2 and same_family_403 >= 2:
        return "P1_same_family_403_after_page", "页面已打开且同家族接口复现 403，下一步更适合换 cookie/会话来源而不是再猜参数"
    if tier == "core" and same_family_url_error >= 2:
        return "P1_network_blocked", "服务器到目标站点链路不通，优先换出口或改抓取位置"
    if tier == "core" and status == "ajax_family_page_only" and has_signature and static_pages >= 2:
        return "P1_same_family_unlock", "页面与已打通学校同签名，优先补 cookie / 反爬绕过"
    if tier == "core" and status == "ajax_blocked_403" and ajax_403 > 0:
        return "P1_403_blocked", "已有明确接口，但被 403 阻塞，适合继续服务器侧会话/请求头试探"
    if tier == "core" and pdf_structured_guangxi_rows > 0:
        return "P2_pdf_structured_ready", "已从官方 PDF 抽出广西结构化计划行，可直接并入历史计划层"
    if tier == "core" and cached_pdf_guangxi > 0:
        return "P2_pdf_guangxi_extract", "已缓存到含广西的官方计划 PDF，可优先从附件侧抽结构化信息"
    if tier == "core" and cached_pdf_count > 0:
        return "P2_pdf_extract", "已有官方 PDF 缓存，可继续从附件侧提取结构化线索"
    if tier == "core" and status == "page_only" and static_pages >= 2:
        return "P2_page_parse_or_unlock", "已有计划/分数页面，可继续抽静态信息或找接口入口"
    if tier == "core" and status == "needs_discovery":
        return "P3_discovery", "核心校仍需补入口和有效页面"
    if tier == "support" and status == "form_replay_blocked" and form_replay_variants > 0 and form_replay_success == 0:
        return "P4_support_form_replay_blocked", "页面可打开但 FineUI 表单回放未命中，先记为协议型阻塞，放在核心校之后"
    if tier == "support" and status in {"ajax_family_page_only", "ajax_blocked_403", "page_only"}:
        return "P4_support_followup", "支持池有可用线索，放在核心校之后推进"
    return "P5_hold", "暂缓，等待前序学校推进后再处理"


def main() -> None:
    args = build_parser().parse_args()
    rows = read_rows(args.pipeline_status)
    backlog: list[dict[str, str]] = []
    for row in rows:
        priority_bucket, rationale = classify_probe_priority(row)
        backlog.append(
            {
                "school_key": row["school_key"],
                "school_name": row["school_name"],
                "engineering_tier": row["engineering_tier"],
                "pipeline_status": row["pipeline_status"],
                "static_ajax_page_count": row.get("static_ajax_page_count", "0"),
                "static_ajax_param_endpoints": row.get("static_ajax_param_endpoints", ""),
                "static_ajax_data_endpoints": row.get("static_ajax_data_endpoints", ""),
                "static_ajax_config_signature": row.get("static_ajax_config_signature", ""),
                "ajax_403": row.get("ajax_403", "0"),
                "ajax_timeout_like": row.get("ajax_timeout_like", "0"),
                "same_family_page_ok": row.get("same_family_page_ok", "0"),
                "same_family_403": row.get("same_family_403", "0"),
                "same_family_url_error": row.get("same_family_url_error", "0"),
                "cached_pdf_count": row.get("cached_pdf_count", "0"),
                "cached_pdf_guangxi_count": row.get("cached_pdf_guangxi_count", "0"),
                "pdf_structured_guangxi_rows": row.get("pdf_structured_guangxi_rows", "0"),
                "form_replay_variants_tested": row.get("form_replay_variants_tested", "0"),
                "form_replay_success_count": row.get("form_replay_success_count", "0"),
                "form_replay_record_count_max": row.get("form_replay_record_count_max", "0"),
                "probe_priority_bucket": priority_bucket,
                "probe_rationale": rationale,
            }
        )

    bucket_order = {
        "P1_same_family_403_after_page": 1,
        "P1_network_blocked": 2,
        "P1_same_family_unlock": 3,
        "P1_403_blocked": 4,
        "P2_pdf_structured_ready": 5,
        "P2_pdf_guangxi_extract": 6,
        "P2_pdf_extract": 7,
        "P2_page_parse_or_unlock": 8,
        "P3_discovery": 9,
        "P4_support_form_replay_blocked": 10,
        "P4_support_followup": 11,
        "P5_hold": 12,
    }
    backlog.sort(
        key=lambda row: (
            bucket_order.get(row["probe_priority_bucket"], 99),
            0 if row["engineering_tier"] == "core" else 1,
            row["school_name"],
        )
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(backlog[0].keys()))
        writer.writeheader()
        writer.writerows(backlog)

    print(f"Wrote engineering probe backlog to {args.output}.")


if __name__ == "__main__":
    main()
