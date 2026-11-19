#!/usr/bin/env python3
"""Tests for check_claims.py. Standard library only.

Run:  python3 scripts/test_check_claims.py
"""
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_claims.py")

CARD = """\
---
id: {id}
status: {status}
protected: {protected}
role: Partnerships Manager, Northwind Labs (fictional)
period: 2022.03–2023.09
---

# {id} · Grew channel partners from 12 to 40

## Numbers and what they mean
| Number | Unit | Time window | Basis |
|---|---|---|---|
| 12 → 40 active partners | partners | 18 months | active in past 90 days |
| 18% → 34% | % of new leads | same | share of leads, not revenue |

## Don't rephrase as
- Don't write "drove $X in revenue."
"""


class CheckClaims(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "evidence/claims").mkdir(parents=True)
        (self.root / "cv/resumes").mkdir(parents=True)
        self.card("C-001", protected="true")
        self.card("C-002")
        self.card("C-003", status="Needs review")

    def tearDown(self):
        self.tmp.cleanup()

    def card(self, cid, status="Safe to draft", protected="false"):
        (self.root / f"evidence/claims/{cid}.md").write_text(
            CARD.format(id=cid, status=status, protected=protected), encoding="utf-8")

    def resume(self, name, body):
        p = self.root / f"cv/resumes/{name}.md"
        p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        return p

    def run_check(self, name, *extra):
        r = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), f"cv/resumes/{name}.md", "--lang", "en", *extra],
            cwd=self.root, capture_output=True, text=True)
        return r.returncode, r.stdout

    # --- normal paths -------------------------------------------------------

    def test_clean_resume_passes(self):
        self.resume("ok", """
            ---
            id: ok
            base:                      # empty for the first baseline
            ---
            ## Summary
            Partnerships lead who grew active partners from 12 to 40. <!-- C-001 -->
            ## Experience
            ### Partnerships Manager · Northwind · 2022–2023
            - Lifted partner-sourced leads from 18% to 34% of new pipeline. <!-- C-001 -->
            ## Education
            BA · Some University · 2015
            """)
        code, out = self.run_check("ok")
        self.assertEqual(code, 0, out)
        self.assertIn("OK: 2 lines checked", out)

    def test_template_front_matter_comment_is_not_a_base(self):
        # `base:   # comment` used to be read as base = "# comment" and look for that file
        self.resume("first", """
            ---
            id: first
            base:                      # id of the resume this was copied from
            ---
            ## Summary
            Partnerships lead. <!-- C-002 -->
            """)
        code, out = self.run_check("first")
        self.assertEqual(code, 0, out)
        self.assertNotIn("Baseline", out)

    def test_alias_headings_are_checked(self):
        self.resume("alias", """
            ## Professional Summary
            Partnerships lead. <!-- C-002 -->
            ## 工作经历
            - 重建了伙伴计划。 <!-- C-002 -->
            - 没有标签的一条。
            """)
        code, out = self.run_check("alias")
        self.assertEqual(code, 1, out)
        self.assertEqual(out.count("no Claim ID"), 1, out)

    # --- bypasses found in review ------------------------------------------

    def test_unrecognized_headings_fail_instead_of_passing(self):
        self.resume("renamed", """
            ## Highlights
            Led enterprise AI deployments for Fortune 500 clients.
            ## Career Story
            - Closed $10M in co-sell pipeline.
            """)
        code, out = self.run_check("renamed")
        self.assertEqual(code, 1, out)
        self.assertIn("no Summary or Experience section recognized", out)

    def test_empty_sections_fail(self):
        self.resume("empty", """
            ## Summary
            ## Experience
            ### Role · Company · 2022
            """)
        code, out = self.run_check("empty")
        self.assertEqual(code, 1, out)
        self.assertIn("no lines to check", out)

    def test_unverified_sections_are_reported(self):
        self.resume("skills", """
            ## Summary
            Partnerships lead. <!-- C-002 -->
            ## Skills
            co-sell, enterprise AI deployment
            """)
        code, out = self.run_check("skills")
        self.assertEqual(code, 0, out)
        self.assertIn('section "Skills" has 1 line(s) this script does not verify', out)

    def test_number_not_on_card_fails(self):
        self.resume("num", """
            ## Experience
            - Drove $5M revenue from partners. <!-- C-002 -->
            - Grew partners from 12 to 45. <!-- C-002 -->
            - Ran a 3-tier model and a 2x lift in leads. <!-- C-002 -->
            """)
        code, out = self.run_check("num")
        self.assertEqual(code, 1, out)
        self.assertIn('"5"', out)
        self.assertIn('"45"', out)
        self.assertIn('"2"', out)       # "2x" is a claim; "3-tier" alone is not checked
        self.assertNotIn('"3"', out)
        self.assertNotIn('"12"', out)

    def test_needs_review_and_unknown_ids_fail(self):
        self.resume("status", """
            ## Experience
            - Something. <!-- C-003 -->
            - Something else. <!-- C-999 -->
            """)
        code, out = self.run_check("status")
        self.assertEqual(code, 1, out)
        self.assertIn('C-003 has status "Needs review"', out)
        self.assertIn("C-999 does not match any Claim Card", out)

    def test_missing_baseline_fails(self):
        self.resume("v3", """
            ---
            base: does-not-exist
            ---
            ## Summary
            Partnerships lead. <!-- C-002 -->
            """)
        code, out = self.run_check("v3")
        self.assertEqual(code, 1, out)
        self.assertIn("Baseline file not found", out)

    def test_protected_claim_parked_in_skills_does_not_count(self):
        self.resume("base", """
            ## Summary
            Grew active partners from 12 to 40. <!-- C-001 -->
            """)
        self.resume("v2", """
            ---
            base: base
            ---
            ## Summary
            Partnerships lead. <!-- C-002 -->
            ## Skills
            Partner programs <!-- C-001 -->
            """)
        code, out = self.run_check("v2")
        self.assertEqual(code, 1, out)
        self.assertIn("Protected claim C-001", out)

    def test_protected_claim_kept_passes(self):
        self.resume("base", """
            ## Summary
            Grew active partners from 12 to 40. <!-- C-001 -->
            """)
        self.resume("v4", """
            ---
            base: base
            ---
            ## Experience
            - Grew active partners from 12 to 40 in 18 months. <!-- C-001 -->
            """)
        code, out = self.run_check("v4")
        self.assertEqual(code, 0, out)


class WorkedExample(unittest.TestCase):
    """examples/jordan-lee must behave the way its README says."""
    EXAMPLE = SCRIPT.parent.parent / "examples" / "jordan-lee"

    def run_check(self, name):
        r = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), f"cv/resumes/{name}.md", "--lang", "en"],
            cwd=self.EXAMPLE, capture_output=True, text=True)
        return r.returncode, r.stdout

    def test_baseline_passes(self):
        code, out = self.run_check("channel-baseline")
        self.assertEqual(code, 0, out)

    def test_new_version_passes_with_note(self):
        code, out = self.run_check("acme-pdm")
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE  C-002", out)

    def test_traps_fail_with_five_errors(self):
        code, out = self.run_check("acme-pdm-with-traps")
        self.assertEqual(code, 1, out)
        self.assertIn("FAILED: 5 error(s)", out)
        for snippet in ("no Claim ID", "C-005 has status", '"420"', "C-009 does not match",
                        "Protected claim C-001"):
            self.assertIn(snippet, out)


class ReportScore(unittest.TestCase):
    """report_score.py must agree with the sample in report/template.html (34, as the page shows)."""

    def test_sample_report_score(self):
        root = SCRIPT.parent.parent
        r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("report_score.py")), str(root / "report" / "template.html")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("34 / 100", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
