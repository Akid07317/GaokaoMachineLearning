# 数据字典

本文档记录项目核心数据表、字段口径和清洗规则。当前为基础骨架，后续随真实数据接入持续补充。

## 通用字段约定

| 字段 | 说明 |
| --- | --- |
| `year` | 年份，例如 `2025` |
| `province` | 省份，固定为 `广西` |
| `batch` | 批次，主模型限定为 `本科普通批` |
| `subject_type` | 首选科目，主模型限定为 `物理类` |
| `university_code` | 院校代码，按官方原始数据保留为字符串 |
| `university_name` | 院校名称 |
| `group_code` | 院校专业组代码，按官方原始数据保留为字符串 |
| `group_id` | 自定义唯一键，建议格式为 `{year}_{university_code}_{group_code}` |
| `data_quality` | 数据质量状态，例如 `official`、`checked`、`third_party_pending_check` |

## 位次口径

一分一档换算同分区间：

```text
rank_start = cum_count - count_at_score + 1
rank_end = cum_count
```

若没有官方个人精确位次，使用保守位次：

```text
rank_method = conservative_end
candidate_rank = rank_end
```

## 主表

### `score_rank_table`

一分一档表。详见 `templates/score_rank_table_template.csv`。

### `admission_line_table`

院校专业组投档线表。主模型只使用第一次正式投档。详见 `templates/admission_line_table_template.csv`。

### `enrollment_plan_table`

招生计划明细表。粒度为专业。详见 `templates/enrollment_plan_table_template.csv`。

### `major_group_table`

专业组结构表。粒度为院校专业组。详见 `templates/major_group_table_template.csv`。

### `prediction_output_table`

模型预测输出表。详见 `templates/prediction_output_table_template.csv`。

## 特殊类型处理

以下类型默认不进入普通组主模型，应单独建模或标为不可比：

- 中外合作
- 民族班
- 预科
- 国家专项
- 地方专项
- 高校专项
- 定向
- 免费医学生
- 征集志愿

## 待补充

- 官方来源优先级。
- 章程限制字段细则。
- 城市热度字段口径。
- 专业热度标签规则。
- 专业组拆分/合并匹配规则。
