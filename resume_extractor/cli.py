"""Command-line interface for local resume extraction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extractor import extract_resume
from .parsers import ResumeParseError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume-extractor",
        description="Extract structured information from a PDF or DOCX resume locally.",
    )
    parser.add_argument("resume", type=Path, help="Path to a .pdf or .docx resume")
    parser.add_argument("-o", "--output", type=Path, help="Optional JSON output file")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation (default: 2)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = extract_resume(args.resume)
    except (FileNotFoundError, ResumeParseError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(result, indent=args.indent, ensure_ascii=False)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

