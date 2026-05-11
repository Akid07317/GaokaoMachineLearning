from __future__ import annotations

import pandas as pd


def add_rank_interval(
    score_rank: pd.DataFrame,
    count_col: str = "count_at_score",
    cum_col: str = "cum_count",
) -> pd.DataFrame:
    """Add same-score rank interval columns to a score-rank table."""
    required = {count_col, cum_col}
    missing = required - set(score_rank.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = score_rank.copy()
    result["rank_start"] = result[cum_col] - result[count_col] + 1
    result["rank_end"] = result[cum_col]
    return result


def attach_rank_to_admission_lines(
    admission_lines: pd.DataFrame,
    score_rank: pd.DataFrame,
    score_col: str = "min_score",
) -> pd.DataFrame:
    """Attach rank interval columns to admission lines by score."""
    required_admission = {"year", "subject_type", score_col}
    required_rank = {"year", "subject_type", "score", "rank_start", "rank_end"}
    missing_admission = required_admission - set(admission_lines.columns)
    missing_rank = required_rank - set(score_rank.columns)
    if missing_admission:
        raise ValueError(f"Admission table missing columns: {sorted(missing_admission)}")
    if missing_rank:
        raise ValueError(f"Score-rank table missing columns: {sorted(missing_rank)}")

    rank_lookup = score_rank[
        ["year", "subject_type", "score", "rank_start", "rank_end"]
    ].rename(
        columns={
            "score": score_col,
            "rank_start": "min_rank_low",
            "rank_end": "min_rank_high",
        }
    )
    result = admission_lines.merge(
        rank_lookup,
        on=["year", "subject_type", score_col],
        how="left",
        validate="many_to_one",
    )
    result["min_rank_est"] = result["min_rank_high"]
    return result
