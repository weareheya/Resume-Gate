#!/usr/bin/env python3
"""Make a before-and-after poster from two Resume-Gate reports.

Both reports are scored with the same formula as the template (scripts/report_score.py). The poster
shows the two scores and each dimension before and after, and nothing else from the reports: no name,
employer, job, bullet text or JD wording. It's safe to share as a file. If the two reports were made
in different modes, only the dimensions both share are compared, and the poster says so.
Standard library only.

Usage:  python3 scripts/report_compare.py reports/<before>.html reports/<after>.html [modules]
        [--out reports/<file>.html]
Modules are the same as in report_share.py (--name, --headline, --target, --tag, --highlight);
by default the poster shows only the scores.
Exit code: 0 = written, 2 = could not read a report.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_score import load, score  # noqa: E402
from report_share import BLOCK, add_module_args, apply_modules  # noqa: E402

ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "J1", "J2", "J3"]


def main():
    ap = argparse.ArgumentParser(description="Make a before-and-after poster from two reports.")
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--out", help="output file (default: <after>-compare.html)")
    add_module_args(ap)
    a = ap.parse_args()
    try:
        before, after = load(a.before), load(a.after)
    except (OSError, ValueError) as e:
        print(f"Could not read a report: {e}"); return 2

    sb, pb = score(before)
    sa, pa = score(after)
    shared = [i for i in ORDER if i in pb and i in pa]
    partial = set(shared) != set(pb) or set(shared) != set(pa)
    if partial:
        # Re-score both on the shared dimensions only, so the two totals are comparable.
        for d in (before, after):
            d["dims"] = {i: (i in shared) for i in ORDER}
        sb, _ = score(before)
        sa, _ = score(after)
    both_job = before.get("meta", {}).get("mode") == "job" and after.get("meta", {}).get("mode") == "job"

    meta = {"share_only": True, "mode": "job" if both_job else "checkup",
            "kit_version": after.get("meta", {}).get("kit_version", "")}
    apply_modules(meta, a)
    data = {"meta": meta, "bullets": [], "compare": {
        "before": {"date": before.get("meta", {}).get("date", ""), "score": sb, "dims": {i: pb[i][2] for i in shared}},
        "after": {"date": after.get("meta", {}).get("date", ""), "score": sa, "dims": {i: pa[i][2] for i in shared}},
        "dims": shared, "partial": partial}}

    template = Path(__file__).resolve().parent.parent / "report" / "template.html"
    html = template.read_text(encoding="utf-8")
    blob = json.dumps(data, ensure_ascii=False, indent=1)
    html = BLOCK.sub(lambda m: m.group(1) + "\n" + blob + "\n" + m.group(3), html, count=1)
    after_path = Path(a.after)
    dest = Path(a.out) if a.out else after_path.with_name(after_path.stem + "-compare" + after_path.suffix)
    dest.write_text(html, encoding="utf-8")
    print(f"Written: {dest}  ({sb} -> {sa})")
    print("Safe to share: the poster holds only scores, plus any modules you added.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
