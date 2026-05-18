from __future__ import annotations

from urllib.parse import urlencode


def _target(
    source_id: str,
    source_name: str,
    segment: str,
    target_kind: str,
    url: str,
    *,
    method: str = "GET",
    request_body: str = "",
    target_slug: str,
    notes: str = "",
    file_suffix: str = ".json",
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "source_name": source_name,
        "segment": segment,
        "target_kind": target_kind,
        "url": url,
        "method": method,
        "request_body": request_body,
        "target_slug": target_slug,
        "file_suffix": file_suffix,
        "notes": notes,
    }


def build_engineering_api_targets() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    rows.extend(
        [
            _target(
                "huabei_dianli_211",
                "华北电力大学",
                "A1_core_complete",
                "plan_json",
                "https://goto.ncepu.edu.cn/common/plan_json.json",
                target_slug="plan_json",
                notes="Static plan payload linked from 招生计划 page.",
            ),
            _target(
                "huabei_dianli_211",
                "华北电力大学",
                "A1_core_complete",
                "score_summary_json",
                "https://goto.ncepu.edu.cn/common/aii_json.json",
                target_slug="score_summary_json",
                notes="Static overall score payload linked from 往年分数 page.",
            ),
            _target(
                "huabei_dianli_211",
                "华北电力大学",
                "A1_core_complete",
                "score_major_json",
                "https://goto.ncepu.edu.cn/common/major_json.json",
                target_slug="score_major_json",
                notes="Static major score payload linked from 往年分数 page.",
            ),
        ]
    )

    nuaa_base = "https://zsservice.nuaa.edu.cn/zsw-admin"
    rows.extend(
        [
            _target(
                "nanhang_211",
                "南京航空航天大学招生网",
                "A2_core_near_complete",
                "plan_years",
                f"{nuaa_base}/api/enrollmentPlan/years",
                target_slug="plan_years",
                notes="Dimension list for available enrollment years.",
            ),
            _target(
                "nanhang_211",
                "南京航空航天大学招生网",
                "A2_core_near_complete",
                "plan_provinces_2025",
                f"{nuaa_base}/api/enrollmentPlan/provinces?{urlencode({'year': '2025'})}",
                target_slug="plan_provinces_2025",
            ),
            _target(
                "nanhang_211",
                "南京航空航天大学招生网",
                "A2_core_near_complete",
                "plan_types_2025_guangxi",
                f"{nuaa_base}/api/enrollmentPlan/types?{urlencode({'year': '2025', 'province': '广西'})}",
                target_slug="plan_types_2025_guangxi",
            ),
        ]
    )
    for subject, subject_slug in [("物理类", "physics"), ("理工", "science")]:
        rows.append(
            _target(
                "nanhang_211",
                "南京航空航天大学招生网",
                "A2_core_near_complete",
                f"plan_subjects_2025_guangxi_{subject_slug}",
                f"{nuaa_base}/api/enrollmentPlan/subjects?{urlencode({'year': '2025', 'province': '广西', 'type': '普通类'})}",
                target_slug=f"plan_subjects_2025_guangxi_{subject_slug}",
                notes="Subject list endpoint; repeated slug pair keeps query family together.",
            )
        )
    for year in ["2024", "2025"]:
        for lx, lx_slug in [("普通类", "ordinary"), ("一批次", "firstbatch")]:
            for kl, kl_slug in [("物理类", "physics"), ("理工", "science")]:
                params = {
                    "sf": "广西",
                    "year": year,
                    "kl": kl,
                    "lx": lx,
                    "page": "1",
                    "limit": "10000",
                }
                rows.append(
                    _target(
                        "nanhang_211",
                        "南京航空航天大学招生网",
                        "A2_core_near_complete",
                        "plan_query",
                        f"{nuaa_base}/api/getEnrollmentPlan?{urlencode(params)}",
                        target_slug=f"plan_query_{year}_{lx_slug}_{kl_slug}",
                        notes="Direct Guangxi plan probe for likely batch/subject combinations.",
                    )
                )

    for source_id, source_name, segment, base in [
        ("hefei_gongda_211", "合肥工业大学本科招生", "A2_core_near_complete", "http://bkzs.hfut.edu.cn"),
        ("dalian_haishi_211", "大连海事大学", "A1_core_complete", "http://sjcx.dlmu.edu.cn"),
        ("beijing_keji_211", "北京科技大学本科招生网", "A1_core_complete", "https://zhaoshengyunzhi.ustb.edu.cn"),
        ("zhongguo_kuangye_211", "中国矿业大学", "B1_core_partial", "http://zs.cumt.edu.cn"),
        ("beijing_jiaotong_211", "北京交通大学招生与就业工作处", "A1_core_complete", "http://zsw.bjtu.edu.cn"),
        ("zhongguo_shiyou_beijing_211", "中国石油大学北京", "B1_core_partial", "http://bkzs.cup.edu.cn"),
        ("zhongguo_dizhi_beijing_211", "中国地质大学北京", "C2_support_partial", "https://zhsh.cugb.edu.cn"),
    ]:
        rows.extend(
            [
                _target(
                    source_id,
                    source_name,
                    segment,
                    "plan_param_probe",
                    f"{base}/f/ajax_zsjh_param",
                    method="POST",
                    request_body="",
                    target_slug="ajax_zsjh_param",
                    notes="Returns filter dimensions for plan ajax payload.",
                ),
                _target(
                    source_id,
                    source_name,
                    segment,
                    "score_param_probe",
                    f"{base}/f/ajax_lnfs_param",
                    method="POST",
                    request_body="",
                    target_slug="ajax_lnfs_param",
                    notes="Returns filter dimensions for score ajax payload.",
                ),
            ]
        )
        for year in ["2024", "2025"]:
            for klmc, klmc_slug in [("物理类", "physics"), ("理工", "science")]:
                request_body = urlencode(
                    {
                        "ssmc": "广西",
                        "zsnf": year,
                        "klmc": klmc,
                        "zslx": "普通类",
                    }
                )
                rows.extend(
                    [
                        _target(
                            source_id,
                            source_name,
                            segment,
                            "plan_probe",
                            f"{base}/f/ajax_zsjh",
                            method="POST",
                            request_body=request_body,
                            target_slug=f"ajax_zsjh_{year}_{klmc_slug}",
                            notes="Direct Guangxi plan probe with common new/old subject labels.",
                        ),
                        _target(
                            source_id,
                            source_name,
                            segment,
                            "score_probe",
                            f"{base}/f/ajax_lnfs",
                            method="POST",
                            request_body=request_body,
                            target_slug=f"ajax_lnfs_{year}_{klmc_slug}",
                            notes="Direct Guangxi score probe with common new/old subject labels.",
                        ),
                    ]
                )

    cugb_base = "https://zhsh.cugb.edu.cn"
    cugb_exact_probes = [
        (
            "plan_probe",
            "/f/ajax_zsjh",
            {
                "ssmc": "广西",
                "zsnf": "2024",
                "klmc": "物理类",
                "zslx": "普通考生",
            },
            "ajax_zsjh_2024_physics_ordinary_candidate",
            "CUGB exact Guangxi ordinary-physics plan probe for 2024.",
        ),
        (
            "plan_probe",
            "/f/ajax_zsjh",
            {
                "ssmc": "广西",
                "zsnf": "2025",
                "klmc": "物理类",
                "zslx": "普通考生",
            },
            "ajax_zsjh_2025_physics_ordinary_candidate",
            "CUGB exact Guangxi ordinary-physics plan probe for 2025.",
        ),
        (
            "score_probe",
            "/f/ajax_lnfs",
            {
                "ssmc": "广西",
                "zsnf": "2024",
                "klmc": "物理类",
                "zslx": "普通考生",
                "zyz": "物理",
            },
            "ajax_lnfs_2024_physics_ordinary_physicsreq_candidate",
            "CUGB exact Guangxi 2024 ordinary-physics score probe for 物理 group.",
        ),
        (
            "score_probe",
            "/f/ajax_lnfs",
            {
                "ssmc": "广西",
                "zsnf": "2024",
                "klmc": "物理类",
                "zslx": "普通考生",
                "zyz": "物理+化学",
            },
            "ajax_lnfs_2024_physics_ordinary_physchem_candidate",
            "CUGB exact Guangxi 2024 ordinary-physics score probe for 物理+化学 group.",
        ),
        (
            "score_probe",
            "/f/ajax_lnfs",
            {
                "ssmc": "广西",
                "zsnf": "2025",
                "klmc": "物理类",
                "zslx": "普通考生",
                "zyz": "不限",
            },
            "ajax_lnfs_2025_physics_ordinary_unlimited_candidate",
            "CUGB exact Guangxi 2025 ordinary-physics score probe for 不限 group.",
        ),
        (
            "score_probe",
            "/f/ajax_lnfs",
            {
                "ssmc": "广西",
                "zsnf": "2025",
                "klmc": "物理类",
                "zslx": "普通考生",
                "zyz": "物理+化学",
            },
            "ajax_lnfs_2025_physics_ordinary_physchem_candidate",
            "CUGB exact Guangxi 2025 ordinary-physics score probe for 物理+化学 group.",
        ),
    ]
    for target_kind, endpoint, params, target_slug, notes in cugb_exact_probes:
        rows.append(
            _target(
                "zhongguo_dizhi_beijing_211",
                "中国地质大学北京",
                "C2_support_partial",
                target_kind,
                f"{cugb_base}{endpoint}",
                method="POST",
                request_body=urlencode(params),
                target_slug=target_slug,
                notes=notes,
            )
        )

    return rows
