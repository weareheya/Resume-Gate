#!/usr/bin/env python3
"""Check that the en/ and zh-CN/ kits haven't drifted apart. For maintainers of this repo.

The two kits are translated by hand. This can't check that a translation is right, but it
catches the common slips:
  1. A file exists in one kit but not the other.
  2. A Markdown file mentions different IDs in each language (D-001, L-01, C-001, S1…).
  3. A Markdown file has a different number of headings (by level) or code blocks.

Usage (from the repo root; on Windows use `python`):
  python3 tools/check_sync.py

Exit code: 0 = in sync, 1 = differences found.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ("en", "zh-CN")
IGNORE_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache"}
ID_RE = re.compile(r"\b(?:[DLC]-\d+|S\d)\b")
HEADING_RE = re.compile(r"^(#{1,6})\s")


def files(kit):
    base = ROOT / kit
    return {
        p.relative_to(base).as_posix()
        for p in base.rglob("*")
        if p.is_file() and not (set(p.parts) & IGNORE_PARTS)
    }


def shape(path):
    ids, headings, fences, in_fence = set(), Counter(), 0, False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.lstrip().startswith("```"):
            fences += 1
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            headings[len(m.group(1))] += 1
        ids.update(ID_RE.findall(line))
    return ids, headings, fences // 2


def main():
    problems = []
    a, b = (files(k) for k in KITS)
    for f in sorted(a - b):
        problems.append(f"only in {KITS[0]}/: {f}")
    for f in sorted(b - a):
        problems.append(f"only in {KITS[1]}/: {f}")

    for f in sorted(a & b):
        if not f.endswith(".md"):
            continue
        (ia, ha, ca), (ib, hb, cb) = (shape(ROOT / k / f) for k in KITS)
        if ia != ib:
            extra_a, extra_b = sorted(ia - ib), sorted(ib - ia)
            detail = []
            if extra_a:
                detail.append(f"only in {KITS[0]}: {', '.join(extra_a)}")
            if extra_b:
                detail.append(f"only in {KITS[1]}: {', '.join(extra_b)}")
            problems.append(f"{f}: IDs differ ({'; '.join(detail)})")
        if ha != hb:
            fmt = lambda h: " ".join(f"h{k}×{v}" for k, v in sorted(h.items())) or "none"
            problems.append(f"{f}: headings differ ({KITS[0]}: {fmt(ha)} | {KITS[1]}: {fmt(hb)})")
        if ca != cb:
            problems.append(f"{f}: code blocks differ ({KITS[0]}: {ca} | {KITS[1]}: {cb})")

    for p in problems:
        print("DIFF  " + p)
    if problems:
        print(f"{len(problems)} difference(s) between {KITS[0]}/ and {KITS[1]}/")
        return 1
    print(f"OK: {len(a)} files, {KITS[0]}/ and {KITS[1]}/ match in files, IDs, headings and code blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
