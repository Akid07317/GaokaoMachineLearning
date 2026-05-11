from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calibrate admission probabilities.")
    parser.add_argument("--help-next", action="store_true", help="Show next steps.")
    return parser


def main() -> None:
    build_parser().parse_args()
    print("Calibration scaffold is ready. Calibrate after prediction intervals exist.")


if __name__ == "__main__":
    main()
