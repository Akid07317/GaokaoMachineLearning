from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run baseline rank models.")
    parser.add_argument("--help-next", action="store_true", help="Show next steps.")
    return parser


def main() -> None:
    build_parser().parse_args()
    print("Baseline model scaffold is ready. Start with prior-year rank carry-forward.")


if __name__ == "__main__":
    main()
