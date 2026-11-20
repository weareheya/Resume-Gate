#!/usr/bin/env python3
"""Prepare a blind A/B/C comparison of resume versions. Standard library only.

Strips what would give a version away (front matter, HTML comments such as Claim IDs and notes),
shuffles the versions, and writes them as A.md, B.md, C.md… plus a rating sheet. The key that
maps letters back to files goes in key.json: keep it closed until every rater has finished.

Usage (from the repo root):
  python3 evals/blind.py OUT_DIR old.md new.md other.md [--seed N]   prepare
  python3 evals/blind.py --reveal OUT_DIR                           print the key

Exit code: 0 = done, 2 = could not run.
"""
import argparse
import json
import random
import re
import string
import sys
from pathlib import Path

SHEET = """# Blind rating sheet

Job: (paste the job title, or point to jobs/<job-id>.md)
Rater:

Read the job first, then each version. Don't open key.json until you're done.

| Version | Fit to this job (1-5) | Strongest evidence up front (1-5) | Believable, nothing oversold (1-5) | Would you interview? (yes / no) | One-line reason |
|---|---|---|---|---|---|
{rows}
Rank, best first:
"""


def clean(text):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"[ \t]*<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Prepare a blind A/B/C comparison of resume versions.")
    ap.add_argument("out")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--reveal", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)

    if a.reveal:
        key = out / "key.json"
        if not key.is_file():
            print(f"No key in {out}", file=sys.stderr); return 2
        for letter, f in json.loads(key.read_text(encoding="utf-8")).items():
            print(f"{letter}: {f}")
        return 0

    if not 2 <= len(a.files) <= 26:
        print("Give 2 to 26 resume files", file=sys.stderr); return 2
    missing = [f for f in a.files if not Path(f).is_file()]
    if missing:
        print("File not found: " + ", ".join(missing), file=sys.stderr); return 2
    if out.exists() and any(out.iterdir()):
        print(f"{out} is not empty; use a new folder so an old key isn't mixed up", file=sys.stderr); return 2

    files = list(a.files)
    random.Random(a.seed).shuffle(files)
    out.mkdir(parents=True, exist_ok=True)
    key = {}
    for letter, f in zip(string.ascii_uppercase, files):
        (out / f"{letter}.md").write_text(clean(Path(f).read_text(encoding="utf-8")), encoding="utf-8")
        key[letter] = f
    (out / "key.json").write_text(json.dumps(key, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = "".join(f"| {letter} | | | | | |\n" for letter in key)
    (out / "rating-sheet.md").write_text(SHEET.format(rows=rows), encoding="utf-8")
    print(f"Wrote {', '.join(l + '.md' for l in key)} and rating-sheet.md to {out}. key.json holds the answer: don't open it until rating is done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
