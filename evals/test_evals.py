#!/usr/bin/env python3
"""Tests for the eval set: every reference answer passes, known-bad answers fail. Standard library only."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = sorted(p for p in (HERE / "cases").iterdir() if (p / "gold.json").is_file())
sys.path.insert(0, str(HERE))
import score  # noqa: E402


def ref(case, name):
    return (case / "reference" / name).read_text(encoding="utf-8")


class Cases(unittest.TestCase):
    def test_cases_are_well_formed(self):
        self.assertGreaterEqual(len(CASES), 3)
        for case in CASES:
            gold = json.loads((case / "gold.json").read_text(encoding="utf-8"))
            self.assertTrue((ROOT / gold["bank"] / "evidence" / "claims").is_dir(), case.name)
            self.assertTrue((case / "job.md").is_file(), case.name)
            job = (case / "job.md").read_text(encoding="utf-8")
            for r in gold.get("gaps", {}):
                self.assertIn(f"| {r} |", job, f"{case.name}: {r} not in job.md")
            for kind in gold.get("gaps", {}).values():
                self.assertIn(kind, score.KINDS.values(), case.name)

    def test_reference_answers_pass(self):
        for case in CASES:
            r = score.score(case, ref(case, "resume.md"), ref(case, "changelog.md"))
            self.assertTrue(r["pass"], f"{case.name}: {score.report(r)}")
            self.assertEqual(r["gap_accuracy"], 1.0, case.name)


class Catches(unittest.TestCase):
    """Each kind of bad answer must lose points."""
    CASE = HERE / "cases" / "customer-success"

    def test_oversold_saving_is_caught(self):
        bad = ref(self.CASE, "resume.md").replace(
            "in one quarter. <!-- C-002 -->\n- Rebuilt",
            "in one quarter, cutting onboarding time in half. <!-- C-002 -->\n- Rebuilt")
        r = score.score(self.CASE, bad)
        self.assertFalse(r["pass"])
        self.assertTrue(r["forbidden_hits"])

    def test_missing_critical_card_is_caught(self):
        lines = [l for l in ref(self.CASE, "resume.md").splitlines() if "C-002" not in l]
        r = score.score(self.CASE, "\n".join(lines) + "\n")
        self.assertFalse(r["pass"])
        self.assertEqual(r["missing_critical"], ["C-002"])

    def test_wrong_gap_kind_and_skipped_card_are_caught(self):
        cl = ref(self.CASE, "changelog.md").replace("| Not found yet |", "| Hard gap |").replace("| C-005 | Low | No | Needs review |\n", "")
        r = score.score(self.CASE, ref(self.CASE, "resume.md"), cl)
        self.assertFalse(r["pass"])
        self.assertEqual(r["evidence_table_missing"], ["C-005"])
        self.assertEqual(r["gap_accuracy"], 0.75)

    def test_trap_resume_fails_integrity(self):
        trap = (ROOT / "en/examples/jordan-lee/cv/resumes/acme-pdm-with-traps.md").read_text(encoding="utf-8")
        r = score.score(HERE / "cases" / "channel-bd", trap)
        self.assertFalse(r["pass"])
        self.assertEqual(len(r["errors"]), 6)
        self.assertEqual(r["must_not_used"], ["C-005"])

    def test_chinese_gap_kinds_are_read(self):
        kinds, listed = score.read_changelog(
            "| 卡 | 相关度 | 用了吗 | 原因 |\n|---|---|---|---|\n| C-001 | 高 | 是 | |\n\n"
            "| # | JD 要求 | 门槛 | 类别 | 证据 | 下一步 |\n|---|---|---|---|---|---|\n| R1 | x | 是 | 硬缺口 | 无 | |\n")
        self.assertEqual(kinds, {"R1": "Hard gap"})
        self.assertEqual(listed, {"C-001"})


class Blind(unittest.TestCase):
    def test_blind_hides_ids_and_shuffles(self):
        files = [str(c / "reference" / "resume.md") for c in CASES[:3]]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "round1"
            p = subprocess.run([sys.executable, "-I", str(HERE / "blind.py"), str(out), *files, "--seed", "7"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            key = json.loads((out / "key.json").read_text(encoding="utf-8"))
            self.assertEqual(sorted(key.values()), sorted(files))
            for letter in "ABC":
                text = (out / f"{letter}.md").read_text(encoding="utf-8")
                self.assertNotIn("C-00", text)
                self.assertNotIn("base:", text)
            self.assertIn("| C |", (out / "rating-sheet.md").read_text(encoding="utf-8"))
            again = subprocess.run([sys.executable, "-I", str(HERE / "blind.py"), str(out), *files],
                                   capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)  # won't overwrite an old round's key


if __name__ == "__main__":
    unittest.main()
