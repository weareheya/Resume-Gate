#!/usr/bin/env python3
"""Freeze a sent resume: record the SHA-256 of its files, and check later that they haven't changed.
Standard library only.

The record lives in cv/frozen.txt, one "<sha256>  <path>" line per file, the same format as
`shasum -a 256`, so `shasum -a 256 -c cv/frozen.txt` (run from the kit folder) checks it too.
check_claims.py also reads it: a frozen resume that has been edited fails, because a sent version
is the record of what an employer saw (D-010). To change it, copy it into a new version.

Usage (from the kit folder):
  python3 scripts/freeze.py cv/resumes/<id>.md [exported.pdf ...]   record these files
  python3 scripts/freeze.py --check                                 check every frozen file

Exit code: 0 = done / all unchanged, 1 = a frozen file changed or is missing, 2 = could not run.
"""
import argparse
import hashlib
import sys
from pathlib import Path

DEFAULT_LANG = "en"
RECORD = Path("cv/frozen.txt")

T = {
    "en": {
        "no_file": "File not found: {p}",
        "added": "Frozen: {p} ({h})",
        "same": "Already frozen, unchanged: {p}",
        "refreeze": "{p} is already frozen with a different hash. A sent version can't be re-frozen; copy it into a new version instead",
        "changed": "CHANGED since it was frozen: {p}",
        "missing": "MISSING (frozen, but the file is gone): {p}",
        "ok": "OK: {n} frozen file(s), none changed",
        "none": "Nothing frozen yet ({r} doesn't exist)",
    },
    "zh": {
        "no_file": "找不到文件：{p}",
        "added": "已冻结：{p}（{h}）",
        "same": "已经冻结过，没有变化：{p}",
        "refreeze": "{p} 已经冻结过，但 hash 不同。已投递的版本不能重新冻结，请复制成一个新版本再改",
        "changed": "冻结后被改过：{p}",
        "missing": "文件不见了（冻结过，但文件已不存在）：{p}",
        "ok": "通过：{n} 个冻结文件，都没有变化",
        "none": "还没有冻结任何文件（{r} 不存在）",
    },
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_record(record):
    """{path: sha256} from a shasum-style file."""
    out = {}
    if record.is_file():
        for line in record.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) == 2 and len(parts[0]) == 64:
                out[parts[1].lstrip("*").strip()] = parts[0]
    return out


def main():
    ap = argparse.ArgumentParser(description="Freeze sent resume files, or check them.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--record", default=str(RECORD))
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]
    record = Path(a.record)
    known = read_record(record)

    if a.check or not a.files:
        if not known:
            print(t["none"].format(r=record)); return 0
        bad = 0
        for p, h in known.items():
            if not Path(p).is_file():
                print("ERROR " + t["missing"].format(p=p)); bad += 1
            elif sha256(p) != h:
                print("ERROR " + t["changed"].format(p=p)); bad += 1
        if not bad:
            print(t["ok"].format(n=len(known)))
        return 1 if bad else 0

    lines, bad = [], 0
    for f in a.files:
        p = Path(f)
        if not p.is_file():
            print(t["no_file"].format(p=f)); return 2
        key, h = p.as_posix(), sha256(p)
        if key in known:
            if known[key] == h:
                print(t["same"].format(p=key))
            else:
                print("ERROR " + t["refreeze"].format(p=key)); bad += 1
            continue
        lines.append(f"{h}  {key}\n")
        print(t["added"].format(p=key, h=h[:8]))
    if lines:
        record.parent.mkdir(parents=True, exist_ok=True)
        with open(record, "a", encoding="utf-8") as out:
            out.writelines(lines)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
