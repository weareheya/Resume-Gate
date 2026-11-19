#!/usr/bin/env python3
"""Make a shareable copy of a Resume-Gate report, with every private detail removed.

The full report file keeps all its data inside, even when it shows the share card, so it must never
be sent around. This script writes <report>-share.html next to it: the same score and dimension bars,
but no name, employer, job, file path, bullet text, strengths, fixes or JD wording. It opens straight
on the share card. Standard library only.

Usage:  python3 scripts/report_share.py reports/<file>.html [modules]

By default the card shows only the score and the dimension bars. Add only the modules the user ticked:
  --name "…"          a name on the card
  --headline "…"      a one-line positioning
  --target "…"        the kind of role, never an employer (e.g. "Channel BD")
  --tag "…"           a keyword tag; repeat, up to 5
  --highlight "…"     a de-identified strength; repeat, up to 2
Exit code: 0 = written, 2 = could not read the report.
"""
import argparse
import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(r'(<script type="application/json" id="report-data">)(.*?)(</script>)', re.S)


def add_module_args(ap):
    ap.add_argument("--name", help="optional name on the card")
    ap.add_argument("--headline", help="optional one-line positioning")
    ap.add_argument("--target", help="optional kind of role (never an employer)")
    ap.add_argument("--tag", action="append", default=[], help="optional keyword tag (repeat, up to 5)")
    ap.add_argument("--highlight", action="append", default=[], help="optional de-identified strength (repeat, up to 2)")


def apply_modules(meta, a):
    if a.name:
        meta["share_name"] = a.name
    if a.headline:
        meta["share_headline"] = a.headline
    if a.target:
        meta["share_target"] = a.target
    if a.tag:
        meta["share_tags"] = a.tag[:5]
    if a.highlight:
        meta["share_highlights"] = a.highlight[:2]
    return meta


def strip(d):
    meta = d.get("meta", {})
    out = {
        "meta": {"name": "", "title": "", "date": "", "mode": meta.get("mode", "checkup"), "target": "", "file": "",
                 "kit_version": meta.get("kit_version", ""), "share_only": True},
        "dims": d.get("dims", {}),
        "summary": [], "strengths": [], "fixes": [],
        "bullets": [{k: bool(b.get(k)) for k in ("result", "number", "action", "specific", "sourced")} | {"where": "", "text": ""}
                    for b in d.get("bullets", [])],
        "structure": [{"check": "", "pass": bool(c.get("pass"))} for c in d.get("structure", [])],
    }
    jd = d.get("jd")
    if jd:
        supported = jd.get("terms", {}).get("supported", [])
        used = set(jd.get("terms", {}).get("used", []))
        labels = {t: f"t{i + 1}" for i, t in enumerate(supported)}
        out["jd"] = {
            "requirements": [{"req": "", "coverage": r.get("coverage", "none"), "top": bool(r.get("top")), "evidence": ""}
                             for r in jd.get("requirements", [])],
            "terms": {"supported": list(labels.values()), "used": [labels[t] for t in supported if t in used]},
        }
    return out


def main():
    ap = argparse.ArgumentParser(description="Make a shareable copy of a Resume-Gate report.")
    ap.add_argument("report")
    add_module_args(ap)
    a = ap.parse_args()
    src = Path(a.report)
    try:
        html = src.read_text(encoding="utf-8")
        m = BLOCK.search(html)
        data = json.loads(m.group(2)) if m else None
    except (OSError, ValueError):
        data = None
    if not data:
        print(f"Could not read the report: {src}"); return 2
    stripped = strip(data)
    apply_modules(stripped["meta"], a)
    clean = json.dumps(stripped, ensure_ascii=False, indent=1)
    dest = src.with_name(src.stem + "-share" + src.suffix)
    dest.write_text(BLOCK.sub(lambda mm: mm.group(1) + "\n" + clean + "\n" + mm.group(3), html, count=1), encoding="utf-8")
    print(f"Written: {dest}")
    print("Share this file or a screenshot of it. Never send the full report: it holds all your details.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
