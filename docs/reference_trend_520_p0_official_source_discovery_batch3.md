# Reference Trend 520 P0 Official Source Discovery Batch 3

日期：2026-05-16

## 结论

本轮联网核验新增一批 P0/P1 官方来源候选，只写入 source discovery preview，不进入 intake、canonical、ML 或 32 所 decision pool。

## 覆盖

- candidate rows: 7
- universities covered: 6
- manual approval required rows: 3
- confidence tiers: {'T1_official_extractable_plan_candidate': 1, 'T2_official_image_page_needs_ocr': 2, 'T2_official_query_endpoint_needs_browser_or_form': 1, 'T1_official_pdf_landing_page': 1, 'T1_official_pdf_extractable_plan_candidate': 1, 'T1_official_html_extractable_plan_candidate': 1}
- source packet statuses: {'web_verified_candidate_not_parsed': 2, 'official_page_candidate_needs_image_ocr': 1, 'official_query_entry_not_structured': 1, 'official_pdf_landing_page_verified': 1, 'official_pdf_candidate_not_parsed': 1, 'official_page_candidate_needs_image_or_asset_extract': 1}

## 学校

- 哈尔滨医科大学
- 天津中医药大学
- 天津理工大学
- 宁波诺丁汉大学
- 安徽中医药大学
- 广西师范大学

## 下一步

1. 对 T1 official extractable candidates 优先写 source_packet parse preview。
2. 对 image/OCR 或 browser/form endpoint 候选，先等待人工批准。
3. 继续保持 canonical/ML 关闭，不扩 32 所 decision pool。
