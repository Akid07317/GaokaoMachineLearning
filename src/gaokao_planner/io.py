from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv(path: str | Path, dtype: str = "string") -> pd.DataFrame:
    """Read a UTF-8 CSV with conservative string defaults."""
    return pd.read_csv(path, dtype=dtype, encoding="utf-8")


def write_csv(data: pd.DataFrame, path: str | Path) -> None:
    """Write a UTF-8 CSV, creating parent directories if needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False, encoding="utf-8")
