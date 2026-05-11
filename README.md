# 广西新高考院校专业组志愿预测项目

本仓库用于建设一套面向广西物理类、物化生考生的院校专业组志愿风险决策系统。

项目当前阶段先搭建数据和代码骨架，不编造任何真实投档数据。2026 年正式预测必须等官方招生计划和一分一档发布后再更新。

## 目录结构

```text
.
├── configs/          # 项目配置
├── docs/             # 项目文档、数据字典、模型说明
├── raw_data/         # 官方原始数据归档
├── clean_data/       # 清洗后的结构化数据
├── outputs/          # 模型输出、候选池、最终志愿表
├── reports/          # 回测报告、复盘报告
├── scripts/          # 命令行脚本入口
├── src/              # 可复用 Python 代码
└── templates/        # CSV 模板和登记表模板
```

## 当前可做

1. 查看 [source_list.csv](source_list.csv) 里已经确认的官方来源入口。
2. 用 `python3 scripts/fetch_public_sources.py --help` 检查抓取脚本参数。
3. 把 2024、2025 官方原始文件放入 `raw_data/2024/`、`raw_data/2025/`。
4. 按 `templates/*_template.csv` 建立清洗后 CSV。
5. 用 `scripts/data_cleaning.py` 和 `scripts/baseline_model.py` 逐步实现 2024 预测 2025 的回测。
6. 查看 [server_setup.md](docs/server_setup.md) 了解服务器初始化、SSH、防火墙、Docker 和代码同步状态。

## 数据原则

- 只用广西、物理类、本科普通批、普通类、第一次正式投档数据进入主模型。
- 一分一档、投档线、招生计划以官方来源为准。
- 中外合作、民族班、专项计划、预科、征集志愿等特殊类型单独标记或排除。
- 位次优先于分数；专业组优先于学校。

## 开发环境

建议使用 Python 3.11+。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

目前脚本多为骨架入口，下一阶段会先实现一分一档位次换算、投档线关联和基线回测。

## 数据获取现状

- 已确认一批官方来源入口，见 [source_list.csv](source_list.csv)。
- 已补充抓取脚本 [fetch_public_sources.py](scripts/fetch_public_sources.py)，用于批量尝试抓取公开来源并记录状态。
- 当前终端对 `gxeea.cn`、`zyfz.gxeea.cn` 的直连存在 SSL/反爬兼容问题；详见 [source_acquisition_status.md](reports/source_acquisition_status.md)。
