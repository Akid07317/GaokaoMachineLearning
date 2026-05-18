# D2/G2 华北电力大学 Source Identity Fix

生成时间：2026-05-14

## 结论

华北电力大学的 `P0_source_identity_fix` 已生成修复预览。现有行级 `source_url` 全部含 `http://www.yoursite.com/` 占位域名，但本地缓存页面已经能确认官方入口页与官方 JSON payload。

本轮不覆盖基线表，不写入 canonical，不打开 ML。

## 官方来源身份

| 类型 | 官方入口页 | 官方 payload |
|---|---|---|
| 招生计划 | `https://goto.ncepu.edu.cn/zsjh/index.htm` | `https://goto.ncepu.edu.cn/common/plan_json.json` |
| 往年分数总表 | `https://goto.ncepu.edu.cn/wnfs/index.htm` | `https://goto.ncepu.edu.cn/common/aii_json.json` |
| 往年分数专业表 | `https://goto.ncepu.edu.cn/wnfs/index.htm` | `https://goto.ncepu.edu.cn/common/major_json.json` |

## 行级预览

- 行级修复预览：107 行。
- 占位 URL 行：107 行。
- 计划行：67 行。
- 分数总表行：3 行。
- 分数专业表行：37 行。

处理方式：

- 复核材料优先引用官方入口页和官方 JSON payload。
- `http://www.yoursite.com/...` 到 `https://goto.ncepu.edu.cn/...` 的 detail URL 只作为候选推断。
- 若后续必须保留逐行 detail URL，应先人工或联网验证候选 detail URL 可达。

## 当前状态

华北电力大学已从 `source_reacquisition_required` 推进到 `source_identity_fix_preview_ready`。

仍需保留的 caution：

- detail URL 尚未逐条验证。
- `trend_missing_or_unverified` 仍未解决。
- canonical/ML 入口继续关闭。

## 本轮产物

- `scripts/build_engineering_pre_ml_d2_g2_huabei_source_identity_fix.py`
- `clean_data/engineering_guangxi_seed/huabei_dianli_source_identity_fix_row_preview.csv`
- `clean_data/engineering_guangxi_seed/guangxi_pre_ml_d2_g2_request_row_fix_status_preview_merged.csv`
- `reports/engineering_pre_ml_d2_g2_huabei_source_identity_fix_school_summary.csv`
- `reports/engineering_pre_ml_d2_g2_huabei_source_identity_fix_coverage_rollup.csv`
