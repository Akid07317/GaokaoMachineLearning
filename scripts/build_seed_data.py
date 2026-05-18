from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.seed_data import (
    build_admission_rows,
    build_rank_lookup,
    build_score_rank_rows,
    write_dict_rows,
)


def main() -> None:
    score_rank_rows_qg = build_score_rank_rows(
        PROJECT_ROOT / "outputs/extracted/2024/gx_2024_score_rank_physics_qg_table_01.csv",
        year=2024,
        score_type="总成绩+全国性加分",
        source_id="gx_2024_score_rank_physics_qg",
    )
    score_rank_rows_qn = build_score_rank_rows(
        PROJECT_ROOT / "outputs/extracted/2024/gx_2024_score_rank_physics_qn_table_01.csv",
        year=2024,
        score_type="总成绩+全国性加分和地方性加分最高分",
        source_id="gx_2024_score_rank_physics_qn",
    )
    score_rank_rows_2025_qg = build_score_rank_rows(
        PROJECT_ROOT / "outputs/extracted/2025/gx_2025_score_rank_physics_qg_table_01.csv",
        year=2025,
        score_type="总成绩+全国性加分",
        source_id="gx_2025_score_rank_physics_qg",
    )
    score_rank_rows = score_rank_rows_qg + score_rank_rows_qn + score_rank_rows_2025_qg

    rank_lookup_2024_qg = build_rank_lookup(score_rank_rows_qg)
    rank_lookup_2025_qg = build_rank_lookup(score_rank_rows_2025_qg)

    admission_rows_2024 = build_admission_rows(
        PROJECT_ROOT / "outputs/extracted/2024/gx_2024_admission_physics_main_table_01.csv",
        year=2024,
        source_id="gx_2024_admission_physics_main",
        rank_lookup=rank_lookup_2024_qg,
    )
    admission_rows_2025 = build_admission_rows(
        PROJECT_ROOT / "outputs/extracted/2025/gx_2025_admission_physics_main_table_01.csv",
        year=2025,
        source_id="gx_2025_admission_physics_main",
        rank_lookup=rank_lookup_2025_qg,
    )

    write_dict_rows(score_rank_rows, PROJECT_ROOT / "clean_data/score_rank_table_seed.csv")
    write_dict_rows(
        admission_rows_2024 + admission_rows_2025,
        PROJECT_ROOT / "clean_data/admission_line_table_seed.csv",
    )

    print(
        "Built seed datasets: "
        f"{len(score_rank_rows)} score-rank rows, "
        f"{len(admission_rows_2024) + len(admission_rows_2025)} admission rows."
    )


if __name__ == "__main__":
    main()
