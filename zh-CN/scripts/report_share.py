#!/usr/bin/env python3
"""生成 Resume-Gate 报告的可分享副本，删掉所有隐私信息。

The full report file keeps all its data inside, even when it shows the share card, so it must never
be sent around. This script writes <report>-share.html next to it: the same score and dimension bars,
but no name, employer, job, file path, bullet text, strengths, fixes or JD wording. It opens straight
on the share card. Standard library only.

Usage:  python3 scripts/report_share.py reports/<file>.html [--name "Name to show on the card"]
Exit code: 0 = written, 2 = could not read the report.
"""
import argparse
import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(r'(<script type="application/json" id="report-data">)(.*?)(</script>)', re.S)


def strip(d, name=None):
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
    if name:
        out["meta"]["share_name"] = name
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
    ap.add_argument("--name", help="optional name to show on the card")
    a = ap.parse_args()
    src = Path(a.report)
    try:
        html = src.read_text(encoding="utf-8")
        m = BLOCK.search(html)
        data = json.loads(m.group(2)) if m else None
    except (OSError, ValueError):
        data = None
    if not data:
        print(f"读不了这份报告：{src}"); return 2
    clean = json.dumps(strip(data, a.name), ensure_ascii=False, indent=1)
    dest = src.with_name(src.stem + "-share" + src.suffix)
    dest.write_text(BLOCK.sub(lambda mm: mm.group(1) + "\n" + clean + "\n" + mm.group(3), html, count=1), encoding="utf-8")
    print(f"已生成：{dest}")
    print("分享这个文件或它的截图。不要发完整报告：里面有你的全部信息。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
