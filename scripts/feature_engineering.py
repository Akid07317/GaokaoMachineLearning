from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build model features.")
    parser.add_argument("--help-next", action="store_true", help="Show next steps.")
    return parser


def main() -> None:
    build_parser().parse_args()
    print("Feature engineering scaffold is ready. Implement after clean data exists.")


if __name__ == "__main__":
    main()
