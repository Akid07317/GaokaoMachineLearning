from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run auxiliary ML models.")
    parser.add_argument("--help-next", action="store_true", help="Show next steps.")
    return parser


def main() -> None:
    build_parser().parse_args()
    print("ML model scaffold is ready. Use only after baseline backtest exists.")


if __name__ == "__main__":
    main()
