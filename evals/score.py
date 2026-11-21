#!/usr/bin/env python3
"""Score one tailored resume against an eval case. Standard library only.

A case folder holds job.md (the JD) and gold.json (what a good answer must and must not do).
This script copies the case's evidence bank to a temporary folder, drops the resume in as
cv/resumes/_eval.md, runs the kit's check_claims.py there, and then measures:

  integrity        errors from check_claims.py (must be 0)
  critical recall  share of must_use cards the resume cites (must be 100%). A card counts only when its
                   ID is tagged on a line a reader sees, not when it's named in a note or a comment block
  should recall    share of should_use cards cited (reported, not required)
  must-not-use     cards the resume must not cite (e.g. Needs review)
  forbidden        phrases that would oversell (regex, case-insensitive, comments stripped)
  gap kinds        with --changelog: share of requirements whose Coverage Report kind is one gold accepts
  evidence table   with --changelog: share of the bank's cards listed in the evidence table (D-019)

PASS needs: no integrity errors, full critical recall, no must-not-use card, no forbidden phrase,
and (with --changelog) every card in the evidence table. Gap-kind accuracy and should recall
are scores to compare runs, not gates: a reasonable reviewer can sort a gap differently.

Usage (from the repo root):
  python3 evals/score.py evals/cases/<case> path/to/resume.md [--changelog path/to/changelog.md] [--bank DIR] [--json]
  --bank scores against that folder's evidence bank, for a case whose session changes a card (fact-correction).

Exit code: 0 = PASS, 1 = FAIL, 2 = could not run (including check_claims.py crashing or not finishing:
a check that didn't run is never counted as a pass).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r"\bC-\d{3,}\b")
KINDS = {
    "direct": "Direct", "直接": "Direct",
    "transferable or combined": "Transferable or combined", "可迁移或组合": "Transferable or combined",
    "not found yet": "Not found yet", "还没找到": "Not found yet",
    "buildable": "Buildable", "可补足": "Buildable",
    "hard gap": "Hard gap", "硬缺口": "Hard gap",
}


def kind_of(cell):
    """The kind a Coverage Report cell starts with: "Direct (marketing only)" -> Direct."""
    low = cell.strip("* ").lower()
    for k in sorted(KINDS, key=len, reverse=True):
        if low.startswith(k):
            return KINDS[k]
    return cell.strip("* ")


def accepted(gold):
    """A gold gap kind, or a list of kinds a careful reviewer could defend."""
    return [gold] if isinstance(gold, str) else list(gold)


def strip(text):
    """Resume text a reader sees: no front matter, no HTML comments."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def cited(text):
    """Card IDs tagged on a visible resume line: `- Grew partners … <!-- C-001 -->`, or a tag alone on the
    line right under its text (a wrapped bullet). An ID in a note (`<!-- not used: C-003 -->` on its own,
    or a comment spanning lines) doesn't count."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"<!--(?:(?!-->)[^\n])*\n.*?-->", "", text, flags=re.S)  # multi-line comments are notes
    ids, waiting = set(), False  # waiting: the line above is a bullet with no tag yet (it wraps)
    for line in text.splitlines():
        visible = re.sub(r"<!--.*?-->", "", line).strip(" \t-*")
        tags = re.findall(r"<!--(.*?)-->", line)
        if tags and (visible or waiting):
            ids |= set(ID.findall(" ".join(tags)))
        waiting = bool(visible) and not tags and bool(re.match(r"\s*[-*] |\s{2,}\S", line))
    return ids


class CheckFailed(RuntimeError):
    """check_claims.py crashed or didn't finish."""


def tables(text):
    """Yield (header cells, rows) for each Markdown table."""
    block = []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            block.append([c.strip() for c in line.strip().strip("|").split("|")])
        else:
            if len(block) >= 2:
                yield [h.lower() for h in block[0]], [r for r in block[2:] if any(r)]
            block = []


def read_changelog(text):
    kinds, listed = {}, set()
    for head, rows in tables(text):
        if head and head[0] in ("card", "卡"):
            for r in rows:
                listed |= set(ID.findall(r[0]))
        if head and head[0] == "#":
            col = next((i for i, h in enumerate(head) if h in ("kind", "类别")), None)
            if col is None:
                continue
            for r in rows:
                if len(r) > col:
                    kinds[r[0]] = kind_of(r[col])
    return kinds, listed


def run_check(bank, resume_text, overlay=None):
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "bank"
        shutil.copytree(bank, work)
        if overlay is not None:
            shutil.copytree(overlay, work, dirs_exist_ok=True)
        (work / "cv" / "resumes").mkdir(parents=True, exist_ok=True)
        (work / "cv" / "resumes" / "_eval.md").write_text(resume_text, encoding="utf-8")
        kit = bank
        while kit != kit.parent and not (kit / "scripts" / "check_claims.py").is_file():
            kit = kit.parent
        script = kit / "scripts" / "check_claims.py"
        if not script.is_file():
            script = ROOT / "en" / "scripts" / "check_claims.py"
        if not script.is_file():
            raise FileNotFoundError("check_claims.py not found above " + str(bank))
        p = subprocess.run([sys.executable, "-I", str(script), "cv/resumes/_eval.md"],
                           cwd=work, capture_output=True, text=True)
        lines = p.stdout.splitlines()
        errors = [l for l in lines if l.startswith("ERROR")]
        # Fail closed: only a run that ended with its verdict line counts, and its exit code must agree.
        verdict = any(re.match(r"(OK|FAILED|通过|未通过)[:：]", l) for l in lines)
        if not verdict or p.returncode not in (0, 1) or (p.returncode == 1) != bool(errors):
            tail = (p.stderr.strip().splitlines() or lines or ["no output"])[-1]
            raise CheckFailed(f"check_claims.py exited {p.returncode} without a verdict: {tail}")
        return errors, [l for l in lines if l.startswith("WARN")]


def score(case, resume_text, changelog_text=None, bank=None):
    """bank: score against this evidence bank instead of the case's (the workspace after a run, for a
    case where the session itself changes a card, like fact-correction)."""
    gold = json.loads((case / "gold.json").read_text(encoding="utf-8"))
    overlay = None
    if bank is not None:
        bank = Path(bank).resolve()
    else:
        bank = (ROOT / gold["bank"]).resolve()
        overlay = (ROOT / gold["overlay"]).resolve() if gold.get("overlay") else None
    errors, warns = run_check(bank, resume_text, overlay)
    ids = cited(resume_text)
    body = strip(resume_text)
    must, should = gold.get("must_use", []), gold.get("should_use", [])
    r = {
        "case": gold.get("case", case.name),
        "errors": errors,
        "warns": warns,
        "critical_recall": sum(c in ids for c in must) / len(must) if must else 1.0,
        "missing_critical": [c for c in must if c not in ids],
        "should_recall": sum(c in ids for c in should) / len(should) if should else None,
        "must_not_used": [c for c in gold.get("must_not_use", []) if c in ids],
        "forbidden_hits": [p for p in gold.get("forbidden", []) if re.search(p, body, re.I)],
    }
    if changelog_text is not None:
        kinds, listed = read_changelog(changelog_text)
        want = gold.get("gaps", {})
        r["gap_kinds"] = {k: {"gold": v, "got": kinds.get(k)} for k, v in want.items()}
        r["gap_accuracy"] = sum(kinds.get(k) in accepted(v) for k, v in want.items()) / len(want) if want else None
        cards = sorted({p.stem for p in (bank / "evidence" / "claims").glob("C-*.md")}
                       | ({p.stem for p in (overlay / "evidence" / "claims").glob("C-*.md")} if overlay else set()))
        r["evidence_table_missing"] = [c for c in cards if c not in listed]
    r["pass"] = (not errors and r["critical_recall"] == 1.0 and not r["must_not_used"]
                 and not r["forbidden_hits"] and not r.get("evidence_table_missing"))
    return r


def pct(x):
    return "n/a" if x is None else f"{x:.0%}"


def report(r):
    out = [f"Case: {r['case']}  ->  {'PASS' if r['pass'] else 'FAIL'}",
           f"  integrity        {len(r['errors'])} error(s), {len(r['warns'])} warning(s)"]
    out += ["    " + e for e in r["errors"]]
    out.append(f"  critical recall  {pct(r['critical_recall'])}"
               + (f"  missing: {', '.join(r['missing_critical'])}" if r["missing_critical"] else ""))
    out.append(f"  should recall    {pct(r['should_recall'])}")
    out.append(f"  must-not-use     {', '.join(r['must_not_used']) or 'none'}")
    out.append(f"  forbidden        {', '.join(r['forbidden_hits']) or 'none'}")
    if "gap_accuracy" in r:
        out.append(f"  gap kinds        {pct(r['gap_accuracy'])}")
        for k, v in r["gap_kinds"].items():
            if v["got"] not in accepted(v["gold"]):
                out.append(f"    {k}: expected {' or '.join(accepted(v['gold']))}, got {v['got'] or '(missing)'}")
        out.append(f"  evidence table   {'complete' if not r['evidence_table_missing'] else 'missing ' + ', '.join(r['evidence_table_missing'])}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Score a tailored resume against an eval case.")
    ap.add_argument("case")
    ap.add_argument("resume")
    ap.add_argument("--changelog")
    ap.add_argument("--bank", help="score against this evidence bank (the workspace after the run) instead of the case's")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    case = Path(a.case)
    try:
        r = score(case, Path(a.resume).read_text(encoding="utf-8"),
                  Path(a.changelog).read_text(encoding="utf-8") if a.changelog else None, a.bank)
    except (OSError, ValueError, KeyError, CheckFailed) as e:
        print(f"Could not score: {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else report(r))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
