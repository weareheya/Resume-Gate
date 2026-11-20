#!/usr/bin/env python3
"""Check that the en/ and zh-CN/ kits haven't drifted apart. For maintainers of this repo.

The two kits are translated by hand. This can't check that a translation is right, but it
catches the common slips:
  1. A file exists in one kit but not the other.
  2. A Markdown file mentions different IDs in each language (D-001, L-01, C-001, S1…).
  3. A Markdown file has a different number of headings (by level) or code blocks.
  4. A Python file's code differs. Only text in quotes may differ (messages, DEFAULT_LANG, the
     module docstring): fix the logic in one kit, then make the same change in the other.
  5. A kit file is matched by that kit's own .gitignore, so a user's Git would never pick it up.
     Templates need a `!` line; evidence/profile.md, INTAKE.md and CV-INDEX.md are meant to match.

Usage (from the repo root; on Windows use `python`):
  python3 tools/check_sync.py

Exit code: 0 = in sync, 1 = differences found.
"""
import ast
import re
import subprocess
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


IGNORED_ON_PURPOSE = {"evidence/profile.md", "evidence/INTAKE.md", "cv/CV-INDEX.md"}


def code_shape(path):
    """The file's syntax tree with every piece of quoted text blanked out, so two translations
    of the same script compare equal and any change to the logic doesn't."""
    tree = ast.parse(path.read_text(encoding="utf-8"))

    class Blank(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.Constant("") if isinstance(node.value, str) else node

        def visit_JoinedStr(self, node):
            # an f-string: keep only the values it formats, in a fixed order (a translation may reorder them)
            parts = sorted((self.visit(v) for v in node.values if isinstance(v, ast.FormattedValue)), key=ast.dump)
            return ast.JoinedStr(parts)

    return ast.dump(Blank().visit(tree), include_attributes=False)


def ignored(kit, names):
    """Files in names that the kit's own .gitignore matches (needs git; empty if git isn't there)."""
    try:
        p = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=ROOT / kit,
                           input="\n".join(names), capture_output=True, text=True)
    except OSError:
        return set()
    return set(p.stdout.split("\n")) - {""}


def main():
    problems = []
    a, b = (files(k) for k in KITS)
    for f in sorted(a - b):
        problems.append(f"only in {KITS[0]}/: {f}")
    for f in sorted(b - a):
        problems.append(f"only in {KITS[1]}/: {f}")

    for f in sorted(a & b):
        if f.endswith(".py"):
            try:
                if code_shape(ROOT / KITS[0] / f) != code_shape(ROOT / KITS[1] / f):
                    problems.append(f"{f}: code differs (only text in quotes may differ between the kits)")
            except SyntaxError as e:
                problems.append(f"{f}: can't parse ({e})")
            continue
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

    for kit in KITS:
        for f in sorted(ignored(kit, sorted(files(kit))) - IGNORED_ON_PURPOSE):
            problems.append(f"{kit}/{f}: matched by {kit}/.gitignore, so a user's Git won't keep it. Add a `!/{f}` line")

    for p in problems:
        print("DIFF  " + p)
    if problems:
        print(f"{len(problems)} difference(s) between {KITS[0]}/ and {KITS[1]}/")
        return 1
    print(f"OK: {len(a)} files, {KITS[0]}/ and {KITS[1]}/ match in files, IDs, headings, code blocks and script logic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
