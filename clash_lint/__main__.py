"""python -m clash_lint config.yaml"""
from __future__ import annotations

import sys
from pathlib import Path

from clash_lint.lint import lint_text


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("用法: python -m clash_lint <config.yaml>", file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    findings = lint_text(text)
    for item in findings:
        print(item.format())
    if any(item.level == "error" for item in findings):
        return 1
    if not findings:
        print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
