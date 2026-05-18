from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gaokao_planner.source_fetch import (
    fetch_single_url,
    load_json_headers,
    load_text_file,
    write_fetch_log,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch a logged-in page using a copied Cookie header or extra headers."
    )
    parser.add_argument("--url", required=True, help="Target URL to fetch.")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML file path.")
    parser.add_argument(
        "--cookie-file",
        type=Path,
        help="Text file containing the full Cookie header value.",
    )
    parser.add_argument(
        "--headers-json",
        type=Path,
        help="JSON file containing extra request headers such as Referer or X-Requested-With.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("reports") / "session_fetch_status.csv",
        help="CSV path for a one-row fetch log.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification for this request.",
    )
    parser.add_argument(
        "--source-id",
        default="manual_session_fetch",
        help="Source identifier written to the fetch log.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    cookie_header = load_text_file(args.cookie_file) if args.cookie_file else ""
    extra_headers = load_json_headers(args.headers_json) if args.headers_json else None

    result = fetch_single_url(
        url=args.url,
        output_path=args.output,
        timeout=args.timeout,
        verify_ssl=not args.insecure,
        cookie_header=cookie_header,
        extra_headers=extra_headers,
        source_id=args.source_id,
    )
    write_fetch_log([result], args.log_path)
    print(
        f"status={result.status} bytes={result.bytes_written} "
        f"output={result.output_path} log={args.log_path}"
    )
    if result.error_message:
        print(f"error={result.error_message}")


if __name__ == "__main__":
    main()
