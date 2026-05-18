from __future__ import annotations

import argparse
import csv
from pathlib import Path


try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "pypdf is required for this script. Run it with the bundled runtime Python from load_workspace_dependencies."
    ) from exc


def discover_pdfs(raw_root: Path) -> list[Path]:
    return sorted(raw_root.rglob("*.pdf.html"))


def safe_slug(path: Path) -> str:
    return path.stem.replace("/", "_")


def extract_text(reader: PdfReader) -> str:
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def infer_school_key(path: Path, raw_root: Path) -> str:
    rel = path.relative_to(raw_root)
    return rel.parts[1] if len(rel.parts) > 1 else "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract text and inventory metadata from cached PDF assets in raw_data."
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path("raw_data"),
        help="Root raw data directory.",
    )
    parser.add_argument(
        "--text-output-dir",
        type=Path,
        default=Path("clean_data") / "cached_pdf_text",
        help="Directory for extracted PDF text files.",
    )
    parser.add_argument(
        "--inventory-output",
        type=Path,
        default=Path("reports") / "cached_pdf_inventory.csv",
        help="CSV summary output path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    pdf_paths = discover_pdfs(args.raw_root)
    rows: list[dict[str, str | int]] = []
    for path in pdf_paths:
        school_key = infer_school_key(path, args.raw_root)
        rel = path.relative_to(args.raw_root)
        reader = PdfReader(str(path))
        text = extract_text(reader)
        out_dir = args.text_output_dir / school_key
        out_dir.mkdir(parents=True, exist_ok=True)
        text_path = out_dir / f"{safe_slug(path)}.txt"
        text_path.write_text(text, encoding="utf-8")
        rows.append(
            {
                "school_key": school_key,
                "source_bucket": rel.parts[0],
                "pdf_path": str(path),
                "text_path": str(text_path),
                "page_count": len(reader.pages),
                "char_count": len(text),
                "has_guangxi": str("广西" in text).lower(),
                "has_physics": str("物理" in text).lower(),
                "has_ordinary_batch": str("普通批" in text).lower(),
                "title_excerpt": text.splitlines()[0][:120] if text.splitlines() else "",
            }
        )

    args.inventory_output.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with args.inventory_output.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {len(rows)} PDF inventory rows to {args.inventory_output}.")


if __name__ == "__main__":
    main()
