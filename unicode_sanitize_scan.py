#!/usr/bin/env python3
"""Sanitize and scan files for hidden/bidirectional unicode/control separators."""

from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

EXPLICIT_FLAG_CHARS = {
    "\u2028",  # line separator
    "\u2029",  # paragraph separator
    "\u0085",  # next line
    "\ufeff",  # BOM / zero width no-break space
    "\u200b",  # zero width space
    "\u200c",  # zero width non-joiner
    "\u200d",  # zero width joiner
    "\u00a0",  # non-breaking space
    "\u202f",  # narrow no-break space
}
FLAG_CATEGORIES = {"Cf", "Zl", "Zp"}


def sanitize_text(text: str) -> str:
    text = text.replace("\u2028", "\n").replace("\u2029", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return text


def scan_text(text: str, path: Path) -> list[str]:
    issues: list[str] = []
    for idx, ch in enumerate(text):
        if unicodedata.category(ch) in FLAG_CATEGORIES or ch in EXPLICIT_FLAG_CHARS:
            line = text.count("\n", 0, idx) + 1
            col = idx - (text.rfind("\n", 0, idx) + 1) + 1
            issues.append(
                f"{path}:{line}:{col} U+{ord(ch):04X} {unicodedata.category(ch)} {unicodedata.name(ch, 'UNKNOWN')}"
            )
    return issues


def process_file(path: Path) -> list[str]:
    original = path.read_text(encoding="utf-8")
    sanitized = sanitize_text(original)
    path.write_text(sanitized, encoding="utf-8", newline="\n")
    return scan_text(sanitized, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    all_issues: list[str] = []
    for file_arg in args.files:
        path = Path(file_arg)
        all_issues.extend(process_file(path))

    if all_issues:
        print("Found disallowed characters:")
        for issue in all_issues:
            print(issue)
        return 1

    print("OK: no flagged unicode/control characters found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
