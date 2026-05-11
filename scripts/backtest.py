from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backtest prediction models.")
    parser.add_argument("--help-next", action="store_true", help="Show next steps.")
    return parser


def main() -> None:
    build_parser().parse_args()
    print("Backtest scaffold is ready. First target: use 2024 data to predict 2025.")


if __name__ == "__main__":
    main()
