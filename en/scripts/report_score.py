#!/usr/bin/env python3
"""Print the score of a Resume-Gate report, using the same formula as report/template.html.

The AI fills only the marks in a report's data block; this script and the template do the maths,
so the score quoted in the chat always matches the one on the page. Standard library only.

Usage:  python3 scripts/report_score.py reports/<file>.html
Exit code: 0 = printed, 2 = could not read the report.
"""
import json
import math
import re
import sys
from pathlib import Path

WEIGHTS = {"R1": 25, "R2": 20, "R3": 15, "R4": 10, "R5": 15, "R6": 15, "J1": 30, "J2": 15, "J3": 10}
BANDS = [(85, "Strong"), (70, "Solid"), (55, "Usable, but losing points"), (0, "Needs a rewrite")]


def half_up(x):
    """Round like JavaScript's Math.round in the template (62.5 -> 63). Python's round() gives 62."""
    return int(math.floor(x + 0.5))


def load(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="report-data">(.*?)</script>', text, re.S)
    if not m:
        raise ValueError("no report-data block found")
    return json.loads(m.group(1))


def score(d):
    bullets = d.get("bullets", [])
    def frac(n, den):
        return (n, den, n / den if den else 0)
    def count(key):
        return frac(sum(1 for b in bullets if b.get(key)), len(bullets))
    def sourced(b):
        # A Safe to draft card covering the whole bullet counts 1; a card under review, or covering part of it, ½.
        v = b.get("sourced")
        return 0.5 if v == "partial" else 1 if v else 0
    jd = d.get("jd") or {}
    reqs = jd.get("requirements", [])
    covered = [r for r in reqs if r.get("coverage") != "none"]
    terms = jd.get("terms") or {"supported": [], "used": []}
    used = [t for t in terms.get("supported", []) if t in terms.get("used", [])]
    checks = d.get("structure", [])
    j1 = sum(1 for r in reqs if r.get("coverage") == "direct") + 0.5 * sum(1 for r in reqs if r.get("coverage") == "partial")
    r = {
        "R1": count("result"), "R2": count("number"), "R3": count("action"), "R4": count("specific"),
        "R5": frac(sum(1 for c in checks if c.get("pass")), len(checks)), "R6": frac(sum(sourced(b) for b in bullets), len(bullets)),
        "J1": frac(j1, len(reqs)), "J2": frac(sum(1 for x in covered if x.get("top")), len(covered)),
        "J3": frac(len(used), len(terms.get("supported", []))),
    }
    # R6 (evidence) is reported as interview readiness, not scored.
    ids = ["R1", "R2", "R3", "R4", "R5"] + (["J1", "J2", "J3"] if d.get("meta", {}).get("mode") == "job" else [])
    dims = d.get("dims") or {}
    # In job mode, JD coverage (J1) is always scored: a job-fit report with no requirements, or with J1
    # switched off, would otherwise drop it and renormalize the rest up to 100.
    job = d.get("meta", {}).get("mode") == "job"
    on = [i for i in ids if (job and i == "J1") or (dims.get(i, True) is not False and r[i][1] > 0)]
    wsum = sum(WEIGHTS[i] for i in on)
    total = half_up(sum(WEIGHTS[i] * r[i][2] for i in on) / wsum * 100) if wsum else 0
    return total, {i: r[i] for i in on}


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().split("\n\n")[-2]); return 2
    try:
        d = load(sys.argv[1])
    except (OSError, ValueError) as e:
        print(f"Could not read the report: {e}"); return 2
    total, parts = score(d)
    band = next(name for floor, name in BANDS if total >= floor)
    print(f"Score: {total} / 100 ({band})")
    for i, (n, den, p) in parts.items():
        n_txt = int(n) if float(n).is_integer() else round(n, 1)
        print(f"  {i}: {n_txt}/{den} = {half_up(p * 100)}%")
    if d.get("meta", {}).get("mode") == "job":
        reqs = (d.get("jd") or {}).get("requirements", [])
        if not reqs:
            print("WARNING: job-fit report with no JD requirements. JD coverage scores 0 until they are filled in.")
        else:
            met = sum(1 for x in reqs if x.get("coverage") == "direct")
            part = sum(1 for x in reqs if x.get("coverage") == "partial")
            print(f"JD requirements: {met} direct · {part} partial · {len(reqs) - met - part} none (of {len(reqs)})")
            gates = [x.get("req", "?") for x in reqs if x.get("gate") and x.get("coverage") != "direct"]
            if gates:
                print("Hard requirements not directly met: " + "; ".join(gates))
    b = d.get("bullets", [])
    if any(x.get("sourced") or x.get("claims") for x in b):
        ok = sum(1 for x in b if x.get("sourced") and x.get("sourced") != "partial")
        pend = sum(1 for x in b if x.get("sourced") == "partial")
        print(f"Interview readiness (not scored): confirmed {ok} · under review or partial {pend} · no card {len(b) - ok - pend}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
