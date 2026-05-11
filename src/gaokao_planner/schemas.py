from __future__ import annotations

CORE_SCHEMAS: dict[str, list[str]] = {
    "score_rank_table": [
        "year",
        "province",
        "subject_type",
        "score_type",
        "score",
        "count_at_score",
        "cum_count",
        "rank_start",
        "rank_end",
        "rank_method",
        "source_id",
        "data_quality",
    ],
    "admission_line_table": [
        "year",
        "batch",
        "subject_type",
        "university_code",
        "university_name",
        "group_code",
        "min_score",
        "min_rank_est",
        "min_rank_low",
        "min_rank_high",
        "remark",
        "is_first_round",
        "source_id",
        "data_quality",
    ],
    "enrollment_plan_table": [
        "year",
        "batch",
        "subject_type",
        "university_code",
        "university_name",
        "group_code",
        "major_code",
        "major_name",
        "plan_count",
        "reselect_requirement",
        "tuition",
        "campus",
        "plan_nature",
        "plan_category",
        "remarks",
        "source_id",
        "data_quality",
    ],
}


def missing_columns(table_name: str, columns: list[str]) -> list[str]:
    """Return required columns missing from a table."""
    required = CORE_SCHEMAS[table_name]
    return [column for column in required if column not in columns]
