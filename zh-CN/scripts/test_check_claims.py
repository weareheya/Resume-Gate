#!/usr/bin/env python3
"""Tests for check_claims.py. Standard library only.

Run:  python3 scripts/test_check_claims.py
"""
import os
import subprocess
import sys
import tempfile
import textwrap
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

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


PROFILE = """\
## Roles
| Title | Company | Start | End |
|---|---|---|---|
| Partnerships Manager | Northwind | 2022.03 | 2023.09 |

## Education
| Degree | School | Year |
|---|---|---|
| BA | Some University | 2015 |
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
        (self.root / "evidence/profile.md").write_text(PROFILE, encoding="utf-8")

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

    def evidence_table(self, rows, name="ok"):
        (self.root / "cv/changelogs").mkdir(exist_ok=True)
        (self.root / "cv/changelogs/JOB-1.md").write_text(
            f"---\nresume: {name}\n---\n## Evidence table (every card)\n\n| Card | Used? |\n|---|---|\n{rows}\n## Delta\n\nC-003 named here doesn't count.\n",
            encoding="utf-8")

    def test_evidence_table_gap_is_a_warning(self):
        self.test_clean_resume_passes()
        self.evidence_table("| C-001 | Yes |\n| C-002 | No |\n")
        code, out = self.run_check("ok")
        self.assertEqual(code, 0, out)  # a reminder, never an error (D-017)
        self.assertIn("doesn't mention C-003", out)

    def test_unused_cards_can_share_one_line(self):
        self.test_clean_resume_passes()
        self.evidence_table("| C-001 | Yes |\n| Low: C-002, C-003 | No, unrelated |\n")
        code, out = self.run_check("ok")
        self.assertNotIn("doesn't mention", out)

    def test_no_evidence_table_or_frozen_version_is_not_checked(self):
        self.test_clean_resume_passes()
        (self.root / "cv/changelogs").mkdir(exist_ok=True)
        (self.root / "cv/changelogs/OLD.md").write_text("---\nresume: ok\n---\n## Delta\nC-001\n", encoding="utf-8")
        self.assertNotIn("doesn't mention", self.run_check("ok")[1])
        self.evidence_table("| C-001 | Yes |\n")
        (self.root / "cv/changelogs/OLD.md").unlink()
        import hashlib
        h = hashlib.sha256((self.root / "cv/resumes/ok.md").read_bytes()).hexdigest()
        (self.root / "cv/frozen.txt").write_text(f"{h}  cv/resumes/ok.md\n", encoding="utf-8")
        self.assertNotIn("doesn't mention", self.run_check("ok")[1])

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
            ## What I do
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
        self.assertIn('"$5M"', out)
        self.assertIn('"45"', out)
        self.assertIn('"2x"', out)
        self.assertIn('"3"', out)       # single digits are claims too
        self.assertNotIn('"12"', out)

    def test_number_marked_to_verify_fails(self):
        (self.root / "evidence/claims/C-004.md").write_text(CARD.format(id="C-004", status="Safe to draft", protected="false")
            .replace("| Number | Unit | Time window | Basis |\n|---|---|---|---|", "| Number | Unit | Time window | Basis | Verified |\n|---|---|---|---|---|")
            .replace("| active in past 90 days |", "| active in past 90 days | ✓ |")
            .replace("| share of leads, not revenue |", "| share of leads, not revenue | to verify |"), encoding="utf-8")
        self.resume("pend", """
            ## Experience
            - Grew active partners from 12 to 40. <!-- C-004 -->
            - Partner leads rose from 18% to 34%. <!-- C-004 -->
            """)
        code, out = self.run_check("pend")
        self.assertEqual(code, 1, out)
        self.assertIn('"34%" is not marked ✓ on C-004', out)
        self.assertIn('"18%" is not marked ✓', out)
        self.assertNotIn('"40"', out)    # confirmed numbers on the same card still pass

    def test_interview_only_fails(self):
        self.card("C-005", status="Interview only")
        self.resume("io", """
            ## Experience
            - Something. <!-- C-005 -->
            """)
        code, out = self.run_check("io")
        self.assertEqual(code, 1, out)
        self.assertIn('C-005 is "Interview only"', out)

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


PIPELINE = """\
---
id: {id}
status: Safe to draft
protected: false
period: FY2023
---

# {id} · Partner-sourced pipeline reached US$2.1M

## What happened (raw, unpolished)
Set up deal registration with three partner tiers.

## Numbers and what they mean
| Number | Unit / currency | Time window | Basis | Verified |
|---|---|---|---|---|
| US$2.1M partner-sourced pipeline | USD | FY2023 | Pipeline, not revenue | {verified} |
| 64 registered deals | deals | FY2023 | Open and closed | ✓ |

## Approved wording
> Set up partner deal registration; partner-sourced pipeline reached US$2.1M in FY2023.

## Don't rephrase as
- Banned words: revenue, closed
- Don't round up to "US$5M+ in sales".

## Notes
Expect 7 follow-up questions.
"""


class AuditBypasses(unittest.TestCase):
    """Every bypass reproduced in the 2026-11 audit must now fail (and the honest versions pass)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "evidence/claims").mkdir(parents=True)
        (self.root / "cv/resumes").mkdir(parents=True)
        (self.root / "evidence/profile.md").write_text(PROFILE, encoding="utf-8")
        (self.root / "evidence/claims/C-001.md").write_text(
            CARD.format(id="C-001", status="Safe to draft", protected="true"), encoding="utf-8")
        self.pipeline("C-007")

    def tearDown(self):
        self.tmp.cleanup()

    def pipeline(self, cid, verified="✓", name=None):
        (self.root / f"evidence/claims/{name or cid}.md").write_text(
            PIPELINE.format(id=cid, verified=verified), encoding="utf-8")

    def check(self, body, name="r", *extra):
        (self.root / f"cv/resumes/{name}.md").write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), f"cv/resumes/{name}.md", "--lang", "en", *extra],
                           cwd=self.root, capture_output=True, text=True)
        return r.returncode, r.stdout

    def line(self, text):
        return self.check("## Experience\n" + text + "\n")

    # numbers keep their meaning
    def test_honest_and_equivalent_amounts_pass(self):
        for text in ("- Partner-sourced pipeline reached US$2.1M in FY2023. <!-- C-007 -->",
                     "- Partner-sourced pipeline reached US$2,100,000 across 64 deals. <!-- C-007 -->",
                     "- Ran deal registration across three tiers. <!-- C-007 -->"):
            code, out = self.line(text)
            self.assertEqual(code, 0, text + "\n" + out)

    def test_banned_word_fails(self):
        code, out = self.line("- Closed US$2.1M in revenue. <!-- C-007 -->")
        self.assertEqual(code, 1, out)
        self.assertIn('"revenue" is a banned word on C-007', out)
        self.assertIn('"closed" is a banned word on C-007', out)

    def test_scale_and_currency_must_match(self):
        code, out = self.line("- Pipeline reached EUR 2.1B. <!-- C-007 -->")
        self.assertIn('"EUR 2.1B" doesn\'t appear', out)
        code, out = self.line("- Pipeline reached EUR 2.1M. <!-- C-007 -->")
        self.assertIn('"EUR 2.1M" is in EUR, but C-007 gives it in USD', out)
        code, out = self.line("- Pipeline reached US$2M+. <!-- C-007 -->")
        self.assertIn('"US$2M" doesn\'t appear', out)
        self.assertEqual(code, 1, out)

    def test_numbers_outside_source_sections_do_not_count(self):
        # 19 is only in the Claim ID, 5M only in "Don't rephrase as"; 7 in Notes is a fair source
        self.pipeline("C-019")
        code, out = self.line("- Logged 019 deals worth 5M and prepared 7 answers. <!-- C-019 -->")
        self.assertIn('"019"', out)
        self.assertIn('"5M"', out)
        self.assertNotIn('"7"', out)

    def test_single_digits_and_number_words_are_warnings(self):
        # often just wording ("two teams", "3-tier"), so they're flagged, not failed
        code, out = self.line("- Signed 9 partners and eleven resellers. <!-- C-007 -->")
        self.assertEqual(code, 0, out)
        self.assertIn('WARN  r.md:2: "9"', out)
        self.assertIn('"eleven"', out)

    # the card bank itself
    def test_duplicate_id_fails(self):
        self.pipeline("C-007", name="Z-copy")
        code, out = self.line("- Pipeline reached US$2.1M. <!-- C-007 -->")
        self.assertEqual(code, 1, out)
        self.assertIn("C-007 is defined by more than one card (C-007.md, Z-copy.md)", out)

    def test_blank_verified_counts_as_confirmed(self):
        # the user gave the number; validate_evidence.py reminds them to tick it
        self.pipeline("C-007", verified="")
        code, out = self.line("- Pipeline reached US$2.1M. <!-- C-007 -->")
        self.assertEqual(code, 0, out)

    def test_other_verified_values_are_not_confirmed(self):
        for v in ("tbd", "cofnirmed", "to verify"):
            self.pipeline("C-007", verified=v)
            code, out = self.line("- Pipeline reached US$2.1M. <!-- C-007 -->")
            self.assertIn('"US$2.1M" is not marked ✓ on C-007', out, repr(v))

    # structure
    def test_continuation_and_plain_lines_are_checked(self):
        code, out = self.check("""
            ## Experience
            - Pipeline reached US$2.1M. <!-- C-007 -->
              Also tripled company revenue to US$90M.
            Raised a US$50M Series B.
            """)
        self.assertIn('"US$90M" doesn\'t appear', out)
        self.assertIn("no Claim ID on this line: Raised a US$50M", out)

    def test_wrapped_bullet_with_tag_on_second_line_passes(self):
        code, out = self.check("""
            ## Experience
            - Set up partner deal registration;
              pipeline reached US$2.1M in FY2023. <!-- C-007 -->
            """)
        self.assertEqual(code, 0, out)

    def test_roles_and_education_must_match_profile(self):
        code, out = self.check("""
            ## Experience
            ### VP of AI · Google · 2018–2023
            - Pipeline reached US$2.1M. <!-- C-007 -->
            ### Partnerships Manager · Northwind · 2022–2023
            - Pipeline reached US$2.1M. <!-- C-007 -->
            ## Education
            PhD · Stanford · 2019
            BA · Some University · 2015
            """)
        self.assertEqual(out.count("role heading doesn't match"), 1, out)
        self.assertIn("VP of AI", out)
        self.assertEqual(out.count("Education line doesn't match"), 1, out)
        self.assertIn("PhD", out)

    def test_missing_profile_is_a_warning(self):
        (self.root / "evidence/profile.md").unlink()
        code, out = self.check("""
            ## Experience
            ### VP of AI · Google · 2018–2023
            - Pipeline reached US$2.1M. <!-- C-007 -->
            """)
        self.assertEqual(code, 0, out)
        self.assertIn("WARN", out)
        self.assertIn("profile.md is missing or empty", out)

    def test_other_sections(self):
        code, out = self.check("""
            ## Experience
            - Pipeline reached US$2.1M. <!-- C-007 -->
            ## Achievements
            Tripled revenue.
            ## Awards & Interests
            Tripled revenue to US$90M.
            Chess, hiking
            """)
        self.assertIn("no Claim ID on this line: Tripled revenue.", out)   # Achievements is checked like Experience
        self.assertIn('"Awards & Interests", line 6 has a number no card backs: Tripled revenue to US$90M.', out)
        self.assertIn('section "Awards & Interests" has 2 line(s)', out)

    # baseline
    def test_base_required_when_index_has_a_starting_point(self):
        (self.root / "cv/CV-INDEX.md").write_text(
            "## Current starting point for each type\n| Type | Current starting point | Status |\n|---|---|---|\n"
            "| 01 | base (2026-05-10) | Approved |\n\n## Resume list\n| File | Type |\n|---|---|\n| base.md | 01 |\n",
            encoding="utf-8")
        self.check("---\nid: base\ntype: 01\nbase:\n---\n## Summary\nGrew partners from 12 to 40. <!-- C-001 -->\n", "base")
        code, out = self.check("---\nid: v2\ntype: 01\n---\n## Summary\nDeal person. <!-- C-007 -->\n", "v2")
        self.assertEqual(code, 1, out)
        self.assertIn("no `base:`, but CV-INDEX already has a starting point for type 01", out)
        code, out = self.check("---\nid: base\ntype: 01\nbase:\n---\n## Summary\nGrew partners from 12 to 40. <!-- C-001 -->\n", "base")
        self.assertEqual(code, 0, out)  # the listed baseline itself is fine

    def test_plain_experience_line_without_number_is_listed_not_failed(self):
        code, out = self.check("""
            ## Experience
            ### Partnerships Manager · Northwind · 2022–2023
            B2B SaaS company, partner channel team.
            - Pipeline reached US$2.1M. <!-- C-007 -->
            """)
        self.assertEqual(code, 0, out)
        self.assertIn('section "Experience" has 1 line(s)', out)

    def test_profile_matching_tolerates_punctuation_and_variants(self):
        (self.root / "evidence/profile.md").write_text(PROFILE.replace("| Partnerships Manager |", "| Partnerships Manager; 合作伙伴经理 |"), encoding="utf-8")
        code, out = self.check("""
            ## Experience
            ### 合作伙伴经理 · Northwind · 2022–2023
            - Pipeline reached US$2.1M. <!-- C-007 -->
            ## Education
            B.A. · Some University · 2015
            """)
        self.assertEqual(code, 0, out)

    def test_protected_drop_approved_in_front_matter(self):
        self.check("## Summary\nGrew active partners from 12 to 40. <!-- C-001 -->\n", "base")
        code, out = self.check("---\nbase: base\nprotected-ok: C-001\n---\n## Summary\nDeal person. <!-- C-007 -->\n", "v2")
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE  C-001: dropped or shortened with the user's approval", out)

    def test_protected_keep_for_other_type_may_be_left_out(self):
        (self.root / "evidence/claims/C-001.md").write_text(
            CARD.format(id="C-001", status="Safe to draft", protected="true").replace("protected: true", "protected: true\nkeep-for: 01"),
            encoding="utf-8")
        self.check("## Summary\nGrew active partners from 12 to 40. <!-- C-001 -->\n", "base")
        code, out = self.check("---\nbase: base\ntype: 02\n---\n## Summary\nDeal person. <!-- C-007 -->\n", "pm")
        self.assertEqual(code, 0, out)
        self.assertIn("kept for type(s) 01; this resume is type 02", out)
        code, out = self.check("---\nbase: base\ntype: 01\n---\n## Summary\nDeal person. <!-- C-007 -->\n", "ch")
        self.assertEqual(code, 1, out)
        self.assertIn("Protected claim C-001 is used in the baseline", out)

    def test_protected_claim_weakened_fails(self):
        self.check("## Summary\nGrew active partners from 12 to 40. <!-- C-001 -->\n", "base")
        code, out = self.check("---\nbase: base\n---\n## Summary\nManaged partner relationships. <!-- C-001 -->\n", "v2")
        self.assertEqual(code, 1, out)
        self.assertIn("Protected claim C-001: the baseline (base.md) states 12, 40", out)


class ValidateEvidence(unittest.TestCase):
    def run_v(self, root):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("validate_evidence.py")), "--lang", "en"],
                           cwd=root, capture_output=True, text=True)
        return r.returncode, r.stdout

    def test_example_bank_is_valid(self):
        code, out = self.run_v(SCRIPT.parent.parent / "examples" / "jordan-lee")
        self.assertEqual(code, 0, out)

    def test_bad_bank_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "evidence/claims").mkdir(parents=True)
            (root / "evidence/claims/a.md").write_text(PIPELINE.format(id="C-001", verified="tbd"), encoding="utf-8")
            (root / "evidence/claims/b.md").write_text(PIPELINE.format(id="C-001", verified="✓")
                                                       .replace("status: Safe to draft", "status: Safe"), encoding="utf-8")
            code, out = self.run_v(root)
            self.assertEqual(code, 1, out)
            for snippet in ('"tbd"', "C-001 is used by more than one card: a.md, b.md", 'status "Safe"', "profile.md is missing"):
                self.assertIn(snippet, out)


class ScoreFormula(unittest.TestCase):
    """The audit's score cases: a job-fit score can no longer reach 100 by leaving out the JD."""

    def score(self, d):
        spec = importlib.util.spec_from_file_location("report_score", SCRIPT.with_name("report_score.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.score(d)[0]

    def report(self, reqs, dims=None):
        bullets = [{"result": 1, "number": 1, "action": 1, "specific": 1, "sourced": True}] * 4
        return {"meta": {"mode": "job"}, "bullets": bullets, "structure": [{"pass": 1}] * 5, "dims": dims or {},
                "jd": {"requirements": reqs, "terms": {"supported": ["a"], "used": ["a"]}}}

    def test_job_fit_without_requirements_is_not_100(self):
        self.assertLess(self.score(self.report([])), 100)

    def test_switching_off_jd_coverage_does_not_help(self):
        one_of_three = [{"coverage": "direct", "top": True}, {"coverage": "none"}, {"coverage": "none"}]
        self.assertEqual(self.score(self.report(one_of_three)), 86)
        self.assertEqual(self.score(self.report(one_of_three, dims={"J1": False})), 86)


class HonestResume(unittest.TestCase):
    """D-017: an honest resume with ordinary gaps must pass. If a new rule breaks this, it's too strict."""

    def test_ordinary_gaps_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "evidence/claims").mkdir(parents=True)
            (root / "cv/resumes").mkdir(parents=True)
            # self-stated card, blank Verified cells, no evidence/profile.md yet
            (root / "evidence/claims/C-001.md").write_text(PIPELINE.format(id="C-001", verified="")
                .replace("evidence: on record", "evidence: can explain"), encoding="utf-8")
            (root / "cv/resumes/r.md").write_text(textwrap.dedent("""
                ---
                id: r
                base:
                ---
                ## Summary
                Partnerships manager who works across two teams. <!-- C-001 -->
                ## Experience
                ### Partnerships Manager · Northwind · 2022–2023
                B2B SaaS company, partner channel team.
                - Set up partner deal registration across three tiers;
                  partner-sourced pipeline reached US$2.1M in FY2023. <!-- C-001 -->
                ## Education
                BA · Some University · 2015
                ## Skills
                Partner programs, CRM, 3-tier models
                """).lstrip(), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(SCRIPT), "cv/resumes/r.md", "--lang", "en"],
                               cwd=root, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)
            v = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("validate_evidence.py")), "--lang", "en"],
                               cwd=root, capture_output=True, text=True)
            self.assertEqual(v.returncode, 0, v.stdout)


class Freeze(unittest.TestCase):
    def test_freeze_then_edit_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "evidence/claims").mkdir(parents=True)
            (root / "cv/resumes").mkdir(parents=True)
            (root / "evidence/claims/C-001.md").write_text(PIPELINE.format(id="C-001", verified="✓"), encoding="utf-8")
            r = root / "cv/resumes/sent.md"
            r.write_text("## Experience\n- Pipeline reached US$2.1M. <!-- C-001 -->\n", encoding="utf-8")
            run = lambda script, *args: subprocess.run([sys.executable, "-I", str(SCRIPT.with_name(script)), *args, "--lang", "en"],
                                                        cwd=root, capture_output=True, text=True)
            self.assertEqual(run("freeze.py", "cv/resumes/sent.md").returncode, 0)
            self.assertEqual(run("freeze.py", "--check").returncode, 0)
            self.assertEqual(run("check_claims.py", "cv/resumes/sent.md").returncode, 0)
            r.write_text("## Experience\n- Pipeline reached US$2.1M across 64 deals. <!-- C-001 -->\n", encoding="utf-8")
            out = run("check_claims.py", "cv/resumes/sent.md")
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("was frozen when it was sent", out.stdout)
            out = run("freeze.py", "--check")
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("CHANGED since it was frozen: cv/resumes/sent.md", out.stdout)
            out = run("freeze.py", "cv/resumes/sent.md")
            self.assertEqual(out.returncode, 1, out.stdout)  # can't re-freeze over a sent version


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
        self.assertNotIn("Don't rephrase", out)  # C-001 quotes "40"; a quoted number is not a warning

    def test_new_version_passes_with_note(self):
        code, out = self.run_check("acme-pdm")
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE  C-002", out)

    def test_traps_fail_with_six_errors(self):
        code, out = self.run_check("acme-pdm-with-traps")
        self.assertEqual(code, 1, out)
        self.assertIn("FAILED: 6 error(s)", out)
        for snippet in ("no Claim ID", "C-005 has status", '"420"', "C-009 does not match",
                        "Protected claim C-001", '"revenue" is a banned word on C-003'):
            self.assertIn(snippet, out)
        # trap 6 stays a judgment call: a warning, not an error
        self.assertIn('WARN  acme-pdm-with-traps.md:24: "built and launched" is wording C-002', out)


    def test_protected_check_ignores_other_cards_numbers(self):
        # acme-pdm's summary cites C-001 and C-003 on one line; dropping C-003's US$2.1M must not
        # count as weakening the protected C-001 (found by evals/, v0.5.0)
        import shutil
        with tempfile.TemporaryDirectory() as d:
            ex = Path(d) / "ex"
            shutil.copytree(self.EXAMPLE, ex)
            (ex / "cv/resumes/v2.md").write_text(textwrap.dedent("""
                ---
                id: v2
                type: 01
                base: acme-pdm
                ---
                ## Summary
                Partner development manager: grew active partners from 12 to 40 in 18 months. <!-- C-001 -->
                ## Experience
                ### Partnerships Manager · Northwind Labs · 2022–2023
                - Rebuilt the partner program into a three-tier model and grew active partners from 12 to 40 in 18 months; partners' share of new leads rose from 18% to 34%. <!-- C-001 -->
                - Ran four co-branded webinars with three strategic partners, drawing 380 registrants. <!-- C-004 -->
                ## Education
                BA, Economics · State University · 2019
                """).lstrip(), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(SCRIPT), "cv/resumes/v2.md", "--lang", "en"],
                               cwd=ex, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertNotIn("Protected claim C-001", r.stdout)


DEP_CARD = """\
---
id: {id}
status: Safe to draft
evidence: can explain
protected: {protected}
keep-for: {keep}
role: Partnerships Manager, Northwind Labs (fictional)
period: 2022.03–2023.09
---

# {id} · Secured launch-stage sponsorships

## What happened (raw, unpolished)
{facts}

## Numbers and what they mean
| Number | Unit / currency | Time window | Basis | Verified |
|---|---|---|---|---|
| US$200,000 in sponsorships | USD | 2023 | Signed sponsorship packages | ✓ |

## Attribution
- **What I did**: {did}
- **What the team or others did**: the events team ran the launch.

## Approved wording
> {wording}

## Don't rephrase as
- Banned words: revenue

## Source
Signed sponsorship agreements.

## Notes
{notes}
"""

DEP_RESUME = """\
---
id: {name}
type: 01
status: {status}
base: {base}
---
## Experience
### Partnerships Manager · Northwind · 2022–2023
- {line} <!-- C-001 -->
- Ran the partner newsletter. <!-- C-002 -->
"""


class DependencyHealth(unittest.TestCase):
    """D-020: correct a fact once, and every file that cites the card knows."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "evidence/claims").mkdir(parents=True)
        (self.root / "cv/resumes").mkdir(parents=True)
        (self.root / "interview").mkdir()
        self.card("C-001")
        self.card("C-002", facts="Ran the partner newsletter.", did="wrote it", wording="Ran the partner newsletter.")
        (self.root / "evidence/profile.md").write_text(PROFILE, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def card(self, cid, protected="false", keep="", facts="I designed and negotiated tailored sponsorship packages with partners.",
             did="designed the packages and negotiated every deal.",
             wording="Designed and negotiated sponsorship packages, securing US$200,000.", notes="Expect questions on pricing."):
        (self.root / f"evidence/claims/{cid}.md").write_text(
            DEP_CARD.format(id=cid, protected=protected, keep=keep, facts=facts, did=did, wording=wording, notes=notes),
            encoding="utf-8")

    def resume(self, name, status="Approved", base="", line="Secured US$200,000 in launch-stage sponsorships."):
        (self.root / f"cv/resumes/{name}.md").write_text(
            DEP_RESUME.format(name=name, status=status, base=base, line=line), encoding="utf-8")

    def sh(self, script, *args):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name(script)), *args, "--lang", "en"],
                           cwd=self.root, capture_output=True, text=True)
        return r.returncode, r.stdout

    def check(self, name, *args):
        return self.sh("check_claims.py", f"cv/resumes/{name}.md", *args)

    def approved(self, name="v1"):
        self.resume(name)
        code, out = self.check(name, "--record", "all")
        self.assertEqual(code, 0, out)
        self.assertIn("Recorded", out)

    def test_normalizing_keeps_real_changes(self):
        spec = importlib.util.spec_from_file_location("evidence_deps", SCRIPT.with_name("evidence_deps.py"))
        deps = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deps)
        n = deps.normalize
        self.assertEqual(n("$200,000"), n("$200000"))
        self.assertEqual(n("2022–2023"), n("2022 — 2023"))
        self.assertEqual(n("**Pipeline**, not   revenue"), n("Pipeline, not revenue"))
        self.assertNotEqual(n("$2.1M"), n("$21M"))
        self.assertNotEqual(n("30–50%"), n("30.50%"))
        self.assertNotEqual(n("Led the launch."), n("Led the launch"))  # punctuation still counts

    def test_recorded_version_is_current(self):
        self.approved()
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 0, out)
        self.assertNotIn("changed after", out)
        self.assertNotIn("not checked", out)

    def test_attribution_change_needs_recheck_and_blocks_only_finalize(self):
        self.approved()
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        code, out = self.check("v1")
        self.assertEqual(code, 0, out)  # a reminder until Finalize (D-017)
        self.assertIn("C-001 changed after this version was approved (attribution · major)", out)
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("unresolved major change", out)
        self.assertIn("doesn't mean the resume is wrong", out)

    def test_what_happened_correction_is_major(self):
        self.approved()
        self.card("C-001", facts="As project lead I worked with the design agency to deliver the sponsorship packages.")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("what happened · major", out)

    def test_number_correction_is_major(self):
        self.approved()
        p = self.root / "evidence/claims/C-001.md"
        p.write_text(p.read_text(encoding="utf-8").replace("US$200,000 in sponsorships", "US$20,000 in sponsorships"), encoding="utf-8")
        code, out = self.check("v1", "--finalize")
        self.assertIn("numbers · major", out)

    def test_wording_change_is_minor_and_finalize_passes(self):
        self.approved()
        self.card("C-001", wording="Secured US$200,000 in launch-stage sponsorships.")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 0, out)
        self.assertIn("approved wording · minor", out)

    def test_notes_and_formatting_do_not_count(self):
        self.approved()
        self.card("C-001", notes="Completely different note.",
                  did="designed  the packages and **negotiated** every deal.")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 0, out)
        self.assertNotIn("changed after", out)

    def test_recheck_one_card_only(self):
        self.approved()
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        self.card("C-002", facts="Wrote the partner newsletter every month.", did="wrote it", wording="Ran the partner newsletter.")
        self.assertEqual(self.check("v1", "--record", "C-001")[0], 0)
        code, out = self.check("v1")
        self.assertNotIn("C-001 changed", out)
        self.assertIn("C-002 changed", out)

    def test_old_version_is_not_checked_in_one_line_and_finalize_asks(self):
        self.resume("old")
        code, out = self.check("old")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("not checked against the current cards"), 1)
        code, out = self.check("old", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("C-001, C-002 not checked", out)

    def test_edited_after_record_is_not_checked(self):
        self.approved()
        self.resume("v1", line="Secured US$200,000 in sponsorships for the launch.")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("C-001 not checked", out)

    def test_sent_version_is_history_not_an_error(self):
        self.approved()
        self.assertEqual(self.sh("freeze.py", "cv/resumes/v1.md")[0], 0)
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        code, out = self.check("v1")
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE  v1.md was sent before C-001 changed", out)
        code, out = self.check("v1", "--record", "all")
        self.assertEqual(code, 1, out)  # a sent version's record can't change
        self.assertIn("is frozen", out)

    def test_copied_line_from_out_of_date_baseline_warns(self):
        self.approved("base")
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        self.resume("v2", status="Draft", base="base")
        code, out = self.check("v2")
        self.assertEqual(code, 0, out)
        self.assertIn("copied unchanged from base.md", out)
        self.assertNotIn("C-002", out.split("copied unchanged")[0][-30:])
        self.resume("v2", status="Draft", base="base", line="Designed sponsorship packages that secured US$200,000.")
        code, out = self.check("v2")
        self.assertNotIn("copied unchanged", out)

    def test_keep_for_change_is_major_only_for_this_type(self):
        self.card("C-001", protected="true", keep="01")
        self.approved()
        self.card("C-001", protected="true", keep="01, 03")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 0, out)
        self.assertIn("protection · minor", out)
        self.card("C-001", protected="true", keep="03")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("protection · major", out)

    def test_record_says_nothing_about_card_text(self):
        self.approved()
        text = (self.root / "cv/reviewed.txt").read_text(encoding="utf-8")
        self.assertNotIn("sponsorship", text.lower())
        self.assertIn("cv/resumes/v1.md\tC-001", text)

    def test_used_by_and_health(self):
        self.approved()
        self.resume("old")
        (self.root / "interview/JOB-1.md").write_text(
            "---\njob: JOB-1\n---\n# Follow-up cards\n\n## Sponsorships · C-001\n\nHow it was counted.\n\n## Template line · C-000\n", encoding="utf-8")
        code, out = self.sh("check_claims.py", "interview/JOB-1.md", "--record", "all")
        self.assertEqual(code, 0, out)
        self.assertIn("C-001", out)
        self.assertNotIn("C-000", out)
        code, out = self.sh("list_claims.py", "--health")
        self.assertIn("none needs a recheck", out)
        self.assertIn("Not checked yet (1): old.md", out)
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        code, out = self.sh("list_claims.py", "--health")
        self.assertEqual(code, 0, out)
        self.assertIn("| cv/resumes/v1.md | Approved | needs recheck | C-001: attribution · major |", out)
        self.assertIn("| interview/JOB-1.md | - | needs recheck |", out)
        code, out = self.sh("list_claims.py", "--used-by", "C-001")
        self.assertIn("3 file(s) cite C-001", out)
        code, out = self.sh("list_claims.py", "--used-by", "C-009")
        self.assertIn("No resumes", out)

    def test_deleted_card_still_shows_where_it_was_used(self):
        self.approved()
        (self.root / "evidence/claims/C-001.md").unlink()
        code, out = self.sh("list_claims.py", "--used-by", "C-001")
        self.assertIn("1 file(s) cite C-001", out)
        self.assertIn("removed", out)
        code, out = self.sh("list_claims.py", "--health")
        self.assertIn("| cv/resumes/v1.md | Approved | needs recheck |", out)

    def test_deleted_card_without_a_record_is_missing_not_gone(self):
        # removed = recorded, then deleted; missing = cited, never recorded, no card; not checked = card exists, no record
        self.approved()                      # v1 recorded against C-001
        self.resume("old")                   # a pre-0.7.0 version: no record
        (self.root / "interview/JOB-0.md").write_text(
            "---\njob: JOB-0\n---\n# Follow-up cards\n\n## Sponsorships · C-001\n\nHow it was counted.\n\n## Job ACME-01 notes\n", encoding="utf-8")
        (self.root / "evidence/claims/C-001.md").unlink()
        code, out = self.sh("list_claims.py", "--used-by", "C-001")
        self.assertIn("3 file(s) cite C-001", out)
        self.assertIn("| cv/resumes/v1.md | Approved | needs recheck | C-001: card removed · major |", out)
        self.assertIn("| cv/resumes/old.md | Approved | card missing | C-001: no such card (never recorded here) |", out)
        self.assertIn("| interview/JOB-0.md | - | card missing |", out)
        self.assertNotIn("ACME-01", out)
        code, out = self.sh("list_claims.py", "--used-by", "C-002")
        self.assertIn("| cv/resumes/old.md | Approved | not checked |", out)
        code, out = self.sh("list_claims.py", "--health")
        self.assertIn("3 need a recheck", out)
        code, out = self.sh("check_claims.py", "interview/JOB-0.md", "--record", "all")
        self.assertEqual(code, 1, out)  # C-001 is gone: nothing to record against
        self.assertIn("nothing recorded", out)

    def test_record_on_a_follow_up_card_refused_on_duplicate_ids(self):
        (self.root / "evidence/claims/C-001-copy.md").write_text(
            (self.root / "evidence/claims/C-001.md").read_text(encoding="utf-8"), encoding="utf-8")
        (self.root / "interview/JOB-1.md").write_text("---\njob: JOB-1\n---\n## Sponsorships · C-001\n", encoding="utf-8")
        code, out = self.sh("check_claims.py", "interview/JOB-1.md", "--record", "all")
        self.assertEqual(code, 1, out)
        self.assertIn("nothing was recorded", out)
        self.assertFalse((self.root / "cv/reviewed.txt").exists())

    def test_minor_change_does_not_hide_edited_lines(self):
        self.approved()
        self.card("C-001", wording="Secured US$200,000 in launch-stage sponsorships.")
        self.resume("v1", line="Secured US$200,000 in sponsorships for the launch.")
        code, out = self.check("v1")
        self.assertEqual(code, 0, out)
        self.assertIn("approved wording · minor · edited after it was recorded", out)
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("lines citing it were edited", out)

    def test_record_refused_when_the_check_fails(self):
        self.resume("v1", line="Secured US$200,000 in sponsorships. <!-- C-404 -->")
        code, out = self.check("v1", "--record", "all")
        self.assertEqual(code, 1, out)
        self.assertIn("nothing was recorded", out)
        self.assertFalse((self.root / "cv/reviewed.txt").exists())

    def test_record_names_the_ids_it_skipped(self):
        self.approved()
        code, out = self.check("v1", "--record", "C-001, C-404")
        self.assertEqual(code, 0, out)
        self.assertIn("not recorded: C-404", out)

    def test_incomplete_record_is_never_current(self):
        self.approved()
        f = self.root / "cv/reviewed.txt"
        f.write_text("\n".join("\t".join(x for x in l.split("\t") if not x.startswith("lines="))
                               for l in f.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("not checked", out)

    def test_tagged_line_in_another_section_is_tracked(self):
        (self.root / "cv/resumes/v1.md").write_text(
            DEP_RESUME.format(name="v1", status="Approved", base="", line="Secured US$200,000 in sponsorships.")
            .replace("- Ran the partner newsletter. <!-- C-002 -->\n", "")
            + "\n## Awards\n- Newsletter award for the partner newsletter. <!-- C-002 -->\n", encoding="utf-8")
        self.assertEqual(self.check("v1", "--record", "all")[0], 0)
        self.card("C-002", facts="Edited the partner newsletter.", did="edited it", wording="Ran the partner newsletter.")
        code, out = self.check("v1")
        self.assertIn("C-002 changed after this version was approved", out)

    def test_normalizing_boundaries(self):
        spec = importlib.util.spec_from_file_location("evidence_deps", SCRIPT.with_name("evidence_deps.py"))
        deps = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deps)
        n = deps.normalize
        self.assertEqual(n("Led the launch\nwith two partners."), n("Led the launch with two partners."))
        self.assertNotEqual(n("- Led the launch\n- with two partners."), n("- Led the launch with two partners."))
        self.assertEqual(n("$1,200.50"), n("$1200.50"))
        self.assertEqual(n("1,234,567 users"), n("1234567 users"))
        self.assertNotEqual(n("1.234 users"), n("1234 users"))   # a European thousands dot is not removed
        self.assertNotEqual(n("2,5 FTE"), n("25 FTE"))           # nor a decimal comma
        self.assertNotEqual(n("2022,2023"), n("20222023"))       # nor a list of numbers
        self.assertEqual(len(deps.short_hash("x")), 64)

    # Proposals in the Change Log's Delta table, and reviewed answers (v0.7.0 part 2)
    def changelog(self, status, before='"Secured US$200,000 in launch-stage sponsorships."',
                  after='"Secured US$200,000 in sponsorships I negotiated."'):
        (self.root / "cv/changelogs").mkdir(exist_ok=True)
        (self.root / "cv/changelogs/v2.md").write_text(
            "---\nresume: v2\nstatus: Draft\n---\n# Log\n\n## Delta (against the baseline)\n\n"
            "| # | Location | Change (Before → After) | Basis | Status |\n|---|---|---|---|---|\n"
            f"| 1 | Role A | {before} → {after} | C-001 | {status} |\n", encoding="utf-8")

    def check_v2(self, *args):
        return self.check("v2", "--changelog", "cv/changelogs/v2.md", *args)

    def test_rejected_proposal_still_in_resume_warns(self):
        self.approved("base")
        self.changelog("Rejected")
        self.resume("v2", status="Draft", base="base", line="Secured US$200,000 in sponsorships I negotiated.")
        code, out = self.check_v2()
        self.assertEqual(code, 0, out)
        self.assertIn("proposal #1 was rejected", out)
        self.changelog("Accepted")
        self.assertNotIn("proposal #1", self.check_v2()[1])

    def test_approved_resume_with_pending_proposal_warns(self):
        self.approved("base")
        self.changelog("Pending")
        self.resume("v2", status="Approved", base="base", line="Secured US$200,000 in sponsorships I negotiated.")
        code, out = self.check_v2()
        self.assertEqual(code, 0, out)
        self.assertIn("proposal(s) 1 are still Pending", out)

    def test_pending_proposal_goes_stale_when_its_target_text_changes(self):
        self.approved("base")
        self.changelog("Pending")
        self.resume("v2", status="Draft", base="base")
        self.assertNotIn("stale", self.check_v2()[1])
        self.resume("base", line="Secured US$200,000 in sponsorships across the launch.")
        code, out = self.check_v2()
        self.assertIn("proposal #1 is stale (its Before text is no longer in base.md)", out)

    def test_pending_proposal_goes_stale_when_its_card_changes(self):
        self.approved("base")
        self.changelog("Pending")
        self.resume("v2", status="Draft", base="base")
        code, out = self.sh("check_claims.py", "cv/changelogs/v2.md", "--record", "all")
        self.assertEqual(code, 0, out)
        self.card("C-001", wording="Secured US$200,000 in launch-stage sponsorships.")
        self.assertNotIn("is stale", self.check_v2()[1])  # wording only: not stale
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        code, out = self.check_v2()
        self.assertIn("C-001 changed after it was proposed: attribution · major", out)

    def answer(self, aid, scope, status="Approved", text="I designed the packages and negotiated each deal."):
        (self.root / "interview/answers").mkdir(exist_ok=True)
        (self.root / f"interview/answers/{aid}.md").write_text(
            f"---\nid: {aid}\nquestion: Biggest win?\nscope: {scope}\nstatus: {status}\n---\n# {aid}\n\n"
            f"## Answer (reviewed)\n\n{text} <!-- C-001 -->\n", encoding="utf-8")

    def test_answers_by_scope_and_health(self):
        (self.root / "jobs").mkdir()
        (self.root / "jobs/JOB-1.md").write_text("---\nid: JOB-1\ncompany: Harbor Analytics\n---\n", encoding="utf-8")
        self.answer("A-001", "reusable")
        self.answer("A-002", "employer: Harbor Analytics")
        self.answer("A-003", "employer: Northwind")
        self.answer("A-004", "job: JOB-2")
        for aid in ("A-001", "A-002"):
            self.assertEqual(self.sh("check_claims.py", f"interview/answers/{aid}.md", "--record", "all")[0], 0)
        code, out = self.sh("list_claims.py", "--answers", "JOB-1")
        self.assertEqual(code, 0, out)
        self.assertIn("| A-001 | Biggest win? | reusable | Approved | current | yes |", out)
        self.assertIn("| A-002 |", out)
        self.assertNotIn("A-003", out)
        self.assertNotIn("A-004", out)
        self.assertIn("2 other answer(s)", out)
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        code, out = self.sh("list_claims.py", "--answers", "JOB-1")
        self.assertIn("| A-001 | Biggest win? | reusable | Approved | needs recheck | recheck first |", out)

    # Review of part 2: answers authorize reuse only on a clear yes; proposals are checked per row and per Location
    def answers_out(self, job="JOB-1"):
        (self.root / "jobs").mkdir(exist_ok=True)
        (self.root / f"jobs/{job}.md").write_text("---\nid: JOB-1\ncompany: Harbor Analytics\n---\n", encoding="utf-8")
        return self.sh("list_claims.py", "--answers", job)[1]

    def test_answer_reuse_needs_a_clear_yes(self):
        self.answer("A-001", "reusable")                                  # approved, never recorded
        (self.root / "interview/answers").mkdir(exist_ok=True)
        (self.root / "interview/answers/A-002.md").write_text(          # approved, cites a card that doesn't exist
            "---\nid: A-002\nquestion: Q\nscope: reusable\nstatus: Approved\n---\n## Answer\n\nSomething. <!-- C-009 -->\n", encoding="utf-8")
        (self.root / "interview/answers/A-003.md").write_text(          # approved, cites nothing
            "---\nid: A-003\nquestion: Q\nscope: reusable\nstatus: Approved\n---\n## Answer\n\nSomething.\n", encoding="utf-8")
        out = self.answers_out()
        self.assertNotIn("| yes |", out)
        self.assertIn("| A-001 | Biggest win? | reusable | Approved | not checked | check against the cards first |", out)
        self.assertIn("| A-002 | Q | reusable | Approved | card missing | a card it cites doesn't exist", out)
        self.assertIn("| A-003 | Q | reusable | Approved | not checked | cites no card", out)

    def test_removing_every_card_tag_does_not_bypass_the_recheck(self):
        self.answer("A-001", "reusable")
        self.assertEqual(self.sh("check_claims.py", "interview/answers/A-001.md", "--record", "all")[0], 0)
        self.assertIn("| yes |", self.answers_out())
        (self.root / "interview/answers/A-001.md").write_text(
            "---\nid: A-001\nquestion: Biggest win?\nscope: reusable\nstatus: Approved\n---\n## Answer\n\nI did it all. \n", encoding="utf-8")
        out = self.answers_out()
        self.assertNotIn("| yes |", out)
        self.assertIn("cites no card", out)

    def test_employer_scope_is_an_exact_company_name(self):
        for aid, scope in (("A-001", "employer: Harbor Analytics"), ("A-002", "employer: Harbor"),
                           ("A-003", "employer: Harbor Analytics Group"), ("A-004", "employer:"),
                           ("A-005", "employer: harbor  analytics.")):
            self.answer(aid, scope)
        out = self.answers_out()
        self.assertIn("| A-001 |", out)
        self.assertIn("| A-005 |", out)        # case, spacing and punctuation don't matter
        for aid in ("A-002", "A-003", "A-004"):  # no substring either way, and an empty employer matches nothing
            self.assertNotIn(f"| {aid} |", out)

    def test_changing_an_answers_scope_needs_a_new_confirmation(self):
        self.answer("A-001", "job: JOB-1")
        self.assertEqual(self.sh("check_claims.py", "interview/answers/A-001.md", "--record", "all")[0], 0)
        self.assertIn("| yes |", self.answers_out())
        self.answer("A-001", "reusable")
        out = self.answers_out()
        self.assertNotIn("| yes |", out)
        self.assertIn("edited", self.sh("list_claims.py", "--used-by", "C-001")[1])

    def test_answer_text_is_bound_even_when_the_tag_is_only_in_the_cards_table(self):
        (self.root / "interview/answers").mkdir(exist_ok=True)
        f = self.root / "interview/answers/A-001.md"
        def write(answer, notes):
            f.write_text(
                "---\nid: A-001\nquestion: Biggest win?\nscope: reusable\nstatus: Approved\n---\n# A-001\n\n"
                f"## Answer (reviewed)\n\n{answer}\n\n## Cards it uses\n\n| Card | Part |\n|---|---|\n| C-001 | the packages |\n\n"
                f"## Notes\n\n{notes}\n", encoding="utf-8")
        write("I designed the packages and negotiated each deal.", "Used for ACME-01.")
        self.assertEqual(self.sh("check_claims.py", "interview/answers/A-001.md", "--record", "all")[0], 0)
        self.assertIn("| yes |", self.answers_out())
        write("I designed the packages and negotiated each deal.", "Used for ACME-01 and HARBOR-01, went well.")
        self.assertIn("| yes |", self.answers_out())          # a use record in Notes isn't a new approval
        write("I designed the packages and closed every deal myself.", "Used for ACME-01.")
        out = self.answers_out()
        self.assertNotIn("| yes |", out)                       # the answer text changed: confirm again
        self.assertIn("edited after it was recorded", self.sh("list_claims.py", "--used-by", "C-001")[1])

    def changelog_rows(self, rows):
        (self.root / "cv/changelogs").mkdir(exist_ok=True)
        body = "".join(f"| {i} | {loc} | {b} → {a} | {basis} | {st} |\n" for i, (loc, b, a, basis, st) in enumerate(rows, 1))
        (self.root / "cv/changelogs/v2.md").write_text(
            "---\nresume: v2\nstatus: Draft\n---\n# Log\n\n## Delta (against the baseline)\n\n"
            "| # | Location | Change (Before → After) | Basis | Status |\n|---|---|---|---|---|\n" + body, encoding="utf-8")

    def two_section_base(self):
        (self.root / "cv/resumes/base2.md").write_text(
            "---\nid: base2\ntype: 01\nstatus: Approved\n---\n## Summary\nPartnerships lead. <!-- C-002 -->\n\n## Experience\n"
            "### Partnerships Manager · Northwind · 2022–2023\n- Secured US$200,000 in launch-stage sponsorships. <!-- C-001 -->\n", encoding="utf-8")
        self.resume("v2", status="Draft", base="base2")

    def test_proposal_target_is_looked_for_under_its_location(self):
        self.two_section_base()
        line = '"Secured US$200,000 in launch-stage sponsorships."'
        self.changelog_rows([("Experience", line, '"Brought in US$200,000."', "C-001", "Pending"),
                             ("Summary", line, '"Brought in US$200,000."', "C-001", "Pending")])
        self.sh("check_claims.py", "cv/changelogs/v2.md", "--record", "all")
        out = self.check_v2()[1]
        self.assertNotIn("proposal #1 is stale", out)
        self.assertIn('proposal #2 is stale (its Before text is no longer in base2.md, under "Summary")', out)

    def test_two_proposals_for_the_same_text_conflict(self):
        self.two_section_base()
        line = '"Secured US$200,000 in launch-stage sponsorships."'
        self.changelog_rows([("Experience", line, '"Brought in US$200,000."', "C-001", "Pending"),
                             ("Experience", line, '"Won US$200,000."', "C-001", "Accepted")])
        out = self.check_v2()[1]
        self.assertIn("proposals #1, #2 change the same text", out)

    def test_recording_one_proposal_does_not_refresh_the_others(self):
        self.two_section_base()
        line = '"Secured US$200,000 in launch-stage sponsorships."'
        self.changelog_rows([("Experience", line, '"Brought in US$200,000."', "C-001", "Pending"),
                             ("Summary", '"Partnerships lead."', '"Partnership lead."', "C-002", "Pending")])
        self.sh("check_claims.py", "cv/changelogs/v2.md", "--record", "all")
        self.card("C-001", did="designed the packages; my manager negotiated the deals.")
        self.card("C-002", facts="Edited the partner newsletter.", did="edited it", wording="Ran the partner newsletter.")
        out = self.check_v2()[1]
        self.assertIn("proposal #1 is stale (C-001 changed", out)
        self.assertIn("proposal #2 is stale (C-002 changed", out)
        code, out = self.sh("check_claims.py", "cv/changelogs/v2.md", "--record", "P1")
        self.assertEqual(code, 0, out)
        out = self.check_v2()[1]
        self.assertNotIn("proposal #1 is stale", out)
        self.assertIn("proposal #2 is stale", out)

    def test_unchecked_or_missing_proposals_are_not_valid(self):
        self.two_section_base()
        line = '"Secured US$200,000 in launch-stage sponsorships."'
        self.changelog_rows([("Experience", line, '"Brought in US$200,000."', "C-001", "Pending"),
                             ("Summary", '"Partnerships lead."', '"Partnership lead."', "C-404", "Pending")])
        out = self.check_v2()[1]
        self.assertIn("proposal #1 hasn't been checked against C-001", out)
        self.assertIn("proposal #2 hasn't been checked against C-404", out)
        self.sh("check_claims.py", "cv/changelogs/v2.md", "--record", "P1")
        out = self.check_v2()[1]
        self.assertNotIn("proposal #1 hasn't", out)
        self.assertIn("proposal #2 hasn't", out)
        # editing a recorded row after the record makes it unchecked again
        self.changelog_rows([("Experience", line, '"Brought in US$200,000 for the launch."', "C-001", "Pending"),
                             ("Summary", '"Partnerships lead."', '"Partnership lead."', "C-404", "Pending")])
        self.assertIn("proposal #1 hasn't been checked against C-001", self.check_v2()[1])

    def test_short_rejected_text_is_checked_where_the_location_points(self):
        self.two_section_base()
        self.changelog_rows([("Experience", '"Secured"', '"Led"', "C-001", "Rejected"),
                             ("Headline", '"Partnerships lead."', '"Led"', "C-002", "Rejected")])
        self.resume("v2", status="Draft", base="base2", line="Led the launch sponsorships.")
        out = self.check_v2()[1]
        self.assertIn('proposal #1 was rejected, and its short new text appears in v2.md under "Experience"', out)
        self.assertIn("proposal #2 was rejected, but its new text is too short", out)

    # --- 0.8.0: a disputed fact stops a version only where it is used ---------------------------

    def set_status(self, cid, status):
        p = self.root / f"evidence/claims/{cid}.md"
        p.write_text(p.read_text(encoding="utf-8").replace("status: Safe to draft", f"status: {status}"), encoding="utf-8")

    def only_newsletter(self, name, extra=""):
        (self.root / f"cv/resumes/{name}.md").write_text(
            f"---\nid: {name}\ntype: 01\nstatus: Approved\nbase: \n{extra}---\n## Experience\n"
            "### Partnerships Manager · Northwind · 2022–2023\n- Ran the partner newsletter. <!-- C-002 -->\n", encoding="utf-8")

    def test_disputed_number_blocks_finalize_only_where_it_is_used(self):
        self.approved("v1")
        self.only_newsletter("other")
        self.assertEqual(self.sh("check_claims.py", "cv/resumes/other.md", "--record", "all")[0], 0)
        p = self.root / "evidence/claims/C-001.md"
        p.write_text(p.read_text(encoding="utf-8").replace("| ✓ |", "| to verify |"), encoding="utf-8")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn("US$200,000", out)
        self.assertIn("not marked ✓", out)
        code, out = self.check("other", "--finalize")
        self.assertEqual(code, 0, out)

    def test_disputed_card_blocks_finalize_only_where_it_is_cited(self):
        self.approved("v1")
        self.set_status("C-001", "Needs review")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 1, out)
        self.assertIn('only "Safe to draft" can be used', out)
        self.card("C-001")
        # a disputed card that this version doesn't cite doesn't stop it
        (self.root / "evidence/claims/C-009.md").write_text(
            DEP_CARD.format(id="C-009", protected="false", keep="", facts="x", did="y", wording="z", notes="n")
            .replace("status: Safe to draft", "status: Needs review"), encoding="utf-8")
        code, out = self.check("v1", "--finalize")
        self.assertEqual(code, 0, out)

    def test_protected_ok_does_not_waive_a_disputed_fact(self):
        self.card("C-001", protected="true")
        self.approved("base")
        self.set_status("C-001", "Needs review")
        # Leaving the protected claim out is what protected-ok is for ...
        self.only_newsletter("v2", "protected-ok: C-001\n")
        code, out = self.check("v2")
        self.assertNotIn("Protected claim C-001", out)
        # ... but it never excuses keeping a claim whose card is disputed.
        (self.root / "cv/resumes/v3.md").write_text(
            "---\nid: v3\ntype: 01\nstatus: Draft\nbase: base\nprotected-ok: C-001\n---\n## Experience\n"
            "### Partnerships Manager · Northwind · 2022–2023\n- Secured US$200,000 in launch-stage sponsorships. <!-- C-001 -->\n"
            "- Ran the partner newsletter. <!-- C-002 -->\n", encoding="utf-8")
        code, out = self.check("v3")
        self.assertEqual(code, 1, out)
        self.assertIn('only "Safe to draft" can be used', out)
        # Without protected-ok, dropping the protected claim is still an error.
        (self.root / "cv/resumes/v4.md").write_text(
            "---\nid: v4\ntype: 01\nstatus: Draft\nbase: base\n---\n## Experience\n"
            "### Partnerships Manager · Northwind · 2022–2023\n- Ran the partner newsletter. <!-- C-002 -->\n", encoding="utf-8")
        code, out = self.check("v4")
        self.assertEqual(code, 1, out)
        self.assertIn("Protected claim C-001", out)


class ReportScore(unittest.TestCase):
    """report_score.py must agree with the sample in report/template.html (38, as the page shows)."""

    def test_sample_report_score(self):
        root = SCRIPT.parent.parent
        r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("report_score.py")), str(root / "report" / "template.html")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("38 / 100", r.stdout)


LIST_CLAIMS = SCRIPT.with_name("list_claims.py")


def load_list_claims():
    spec = importlib.util.spec_from_file_location("list_claims_under_test", LIST_CLAIMS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SourceScan(unittest.TestCase):
    """list_claims.py --sources and --fingerprint (D-021): a read-only look at evidence/sources/."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        (self.root / "evidence/claims").mkdir(parents=True)
        (self.root / "evidence/sources").mkdir(parents=True)
        self.lc = load_list_claims()

    def tearDown(self):
        self.tmp.cleanup()

    def src(self, name, text="hello"):
        p = self.root / "evidence/sources" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def intake(self, records=(), skipped=(), heading_r="Source records", heading_s="Skipped sources"):
        body = "# INTAKE\n\n## " + heading_r + "\n| File | Fingerprint | Read |\n|---|---|---|\n"
        body += "".join(f"| `{p}` | {fp} | 2026-11-01 |\n" for p, fp in records)
        body += "\n## " + heading_s + "\n| File | Reason |\n|---|---|\n" + "".join(f"| {p} | private |\n" for p in skipped)
        (self.root / "evidence/INTAKE.md").write_text(body, encoding="utf-8")

    def fp(self, name):
        return self.lc.fingerprint(self.root / "evidence/sources" / name)

    def run_cli(self, *args):
        r = subprocess.run([sys.executable, "-I", str(LIST_CLAIMS), *args, "--lang", "en"],
                           cwd=self.root, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout

    def states(self):
        records, skipped = self.lc.intake_tables(self.root)
        return {r[0]: r for r in self.lc.scan_sources(self.root, records, skipped)}

    def test_no_sources_folder_is_fine(self):
        (self.root / "evidence/sources").rmdir()
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 0, out)
        self.assertIn("nothing to list", out)

    def test_old_intake_without_the_new_sections_works_as_it_is(self):
        self.src("review.txt")
        (self.root / "evidence/INTAKE.md").write_text("# INTAKE\n\n**Mode**: just talk\n\n| # | Accomplishment |\n|---|---|\n| 1 | x |\n", encoding="utf-8")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 0, out)
        self.assertIn("| evidence/sources/review.txt |", out)
        self.assertIn("| new |", out)
        (self.root / "evidence/INTAKE.md").unlink()
        self.assertEqual(self.run_cli("--sources")[0], 0)

    def test_read_before_and_changed_since_read(self):
        a, b = self.src("a.txt", "one"), self.src("b.txt", "two")
        self.intake([("evidence/sources/a.txt", self.fp("a.txt")), ("evidence/sources/b.txt", self.fp("b.txt"))])
        b.write_text("two, edited", encoding="utf-8")
        st = self.states()
        self.assertEqual(st["evidence/sources/a.txt"][3], "read")
        self.assertEqual(st["evidence/sources/b.txt"][3], "changed")

    def test_headings_in_chinese_and_quoted_paths_are_read(self):
        self.src("a.txt")
        self.intake([("./evidence/sources/a.txt", self.fp("a.txt"))], heading_r="来源记录", heading_s="跳过的资料")
        self.assertEqual(self.states()["evidence/sources/a.txt"][3], "read")

    def test_a_unique_rename_is_followed(self):
        self.src("new-name.txt", "same text")
        self.intake([("evidence/sources/old-name.txt", self.fp("new-name.txt"))])
        st = self.states()
        self.assertEqual(st["evidence/sources/new-name.txt"][3:], ("renamed", "n_renamed", "evidence/sources/old-name.txt"))
        self.assertNotIn("evidence/sources/old-name.txt", st)

    def test_a_copy_is_not_a_rename(self):
        self.src("project.txt", "same text")
        self.src("project-copy.txt", "same text")
        self.intake([("evidence/sources/project.txt", self.fp("project.txt"))])
        st = self.states()
        self.assertEqual(st["evidence/sources/project.txt"][3], "read")
        self.assertEqual(st["evidence/sources/project-copy.txt"][3:5], ("new", "n_dup"))

    def test_ambiguous_matches_are_not_migrated(self):
        self.src("one.txt", "same text")
        self.src("two.txt", "same text")
        fp = self.fp("one.txt")
        self.intake([("evidence/sources/gone.txt", fp)])
        st = self.states()  # one vanished path, but two files share the content
        self.assertEqual(st["evidence/sources/one.txt"][3], "new")
        self.assertEqual(st["evidence/sources/two.txt"][3], "new")
        self.assertEqual(st["evidence/sources/gone.txt"][3], "gone")
        self.intake([("evidence/sources/gone1.txt", fp), ("evidence/sources/gone2.txt", fp)])
        (self.root / "evidence/sources/two.txt").unlink()
        st = self.states()  # two vanished paths, one file
        self.assertEqual(st["evidence/sources/one.txt"][3], "new")
        self.assertEqual(st["evidence/sources/gone1.txt"][3], "gone")

    def test_a_file_with_the_same_content_still_there_blocks_a_rename(self):
        self.src("kept.txt", "same text")
        self.src("maybe-renamed.txt", "same text")
        fp = self.fp("kept.txt")
        self.intake([("evidence/sources/kept.txt", fp), ("evidence/sources/vanished.txt", fp)])
        st = self.states()
        self.assertEqual(st["evidence/sources/maybe-renamed.txt"][3], "new")
        self.assertEqual(st["evidence/sources/vanished.txt"][3], "gone")

    def test_a_skipped_file_is_never_opened_even_after_it_changes(self):
        self.src("secret.txt", "v1")
        self.src("fine.txt")
        self.intake(skipped=["evidence/sources/secret.txt"])
        opened = []
        real_fp, real_inspect = self.lc.fingerprint, self.lc.inspect_file
        self.lc.fingerprint = lambda p: opened.append(Path(p).name) or real_fp(p)
        self.lc.inspect_file = lambda p: opened.append(Path(p).name) or real_inspect(p)
        (self.root / "evidence/sources/secret.txt").write_text("v2, edited", encoding="utf-8")
        st = self.states()
        self.assertEqual(st["evidence/sources/secret.txt"][3], "skipped")
        self.assertNotIn("secret.txt", opened)
        self.assertIn("fine.txt", opened)

    def test_a_skipped_folder_is_not_entered(self):
        self.src("private/a.txt")
        self.src("private/deep/b.txt")
        self.intake(skipped=["evidence/sources/private/"])
        opened = []
        real_fp = self.lc.fingerprint
        self.lc.fingerprint = lambda p: opened.append(str(p)) or real_fp(p)
        st = self.states()
        self.assertEqual(st["evidence/sources/private/"][3], "skipped")
        self.assertEqual(len(st), 1)
        self.assertEqual(opened, [])

    def test_one_unreadable_file_does_not_stop_the_scan(self):
        self.src("bad.txt")
        self.src("good.txt")
        real_fp = self.lc.fingerprint

        def flaky(p):
            if Path(p).name == "bad.txt":
                raise PermissionError(13, "Permission denied")
            return real_fp(p)
        self.lc.fingerprint = flaky
        st = self.states()
        self.assertEqual(st["evidence/sources/bad.txt"][3], "unreadable")
        self.assertEqual(st["evidence/sources/good.txt"][3], "new")

    def link(self, link, target, directory=False):
        try:
            Path(link).symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError):
            self.skipTest("no symbolic links here")

    def watch_fingerprints(self):
        opened = []
        real_fp = self.lc.fingerprint
        self.lc.fingerprint = lambda p: opened.append(Path(p).name) or real_fp(p)
        return opened

    def test_links_are_never_followed(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "outside.txt"
            target.write_text("not part of the sources", encoding="utf-8")
            self.link(self.root / "evidence/sources/link.txt", target)
            self.link(self.root / "evidence/sources/linked-dir", other, directory=True)
            self.src("inside.txt")
            self.link(self.root / "evidence/sources/alias.txt", self.root / "evidence/sources/inside.txt")
            opened = self.watch_fingerprints()
            st = self.states()
            for name in ("link.txt", "alias.txt"):
                self.assertEqual(st["evidence/sources/" + name][3], "link")
            self.assertEqual(st["evidence/sources/linked-dir/"][3], "link")
            self.assertEqual(opened, ["inside.txt"])
            self.assertNotIn("evidence/sources/linked-dir/outside.txt", st)

    def test_an_alias_of_a_skipped_file_is_not_opened(self):
        self.src("confidential.pdf", "secret")
        self.link(self.root / "evidence/sources/project.pdf", self.root / "evidence/sources/confidential.pdf")
        self.intake(skipped=["evidence/sources/confidential.pdf"])
        opened = self.watch_fingerprints()
        st = self.states()
        self.assertEqual(st["evidence/sources/confidential.pdf"][3], "skipped")
        self.assertEqual(st["evidence/sources/project.pdf"][3], "link")
        self.assertEqual(opened, [])
        code, out = self.run_cli("--fingerprint", "evidence/sources/project.pdf")
        self.assertEqual(code, 1, out)
        self.assertIn("link", out)

    def test_fingerprint_refuses_a_link_to_a_skipped_file_and_a_skipped_link(self):
        self.src("real.txt")
        self.link(self.root / "evidence/sources/alias.txt", self.root / "evidence/sources/real.txt")
        self.intake(skipped=["evidence/sources/alias.txt"])
        self.assertEqual(self.run_cli("--fingerprint", "evidence/sources/alias.txt")[0], 1)
        self.intake(skipped=[])
        self.assertEqual(self.run_cli("--fingerprint", "evidence/sources/alias.txt")[0], 1)  # a link, skipped or not
        self.assertEqual(self.run_cli("--fingerprint", "evidence/sources/real.txt")[0], 0)

    def test_a_link_in_a_parent_folder_is_refused_too(self):
        with tempfile.TemporaryDirectory() as other:
            (Path(other) / "x.txt").write_text("outside", encoding="utf-8")
            self.link(self.root / "evidence/sources/folder", other, directory=True)
            code, out = self.run_cli("--fingerprint", "evidence/sources/folder/x.txt")
            self.assertEqual(code, 1, out)
            self.assertIn("link", out)

    def test_a_sources_folder_that_is_a_link_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as other:
            (Path(other) / "other.txt").write_text("outside", encoding="utf-8")
            (self.root / "evidence/sources").rmdir()
            self.link(self.root / "evidence/sources", other, directory=True)
            opened = self.watch_fingerprints()
            code, out = self.run_cli("--sources")
            self.assertEqual(code, 1, out)
            self.assertIn("not scanned", out)
            self.assertNotIn("other.txt", out)
            self.assertEqual(opened, [])

    def test_a_pipe_is_not_opened(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("no named pipes here")
        os.mkfifo(self.root / "evidence/sources/pipe")
        self.src("ok.txt")
        code, out = self.run_cli("--sources")  # would hang for the timeout if the pipe were opened
        self.assertEqual(code, 0, out)
        self.assertIn("not a regular file", out)
        self.assertIn("| new |", out)

    def test_icloud_placeholders_are_named_but_not_opened(self):
        (self.root / "evidence/sources/.report.pdf.icloud").write_text("stub", encoding="utf-8")
        opened = []
        real_fp = self.lc.fingerprint
        self.lc.fingerprint = lambda p: opened.append(Path(p).name) or real_fp(p)
        st = self.states()
        self.assertEqual(st["evidence/sources/report.pdf"][3], "cloud")
        self.assertEqual(opened, [])
        self.intake(skipped=["evidence/sources/report.pdf"])
        self.assertEqual(self.states()["evidence/sources/report.pdf"][3], "skipped")

    def test_macos_dataless_flag_is_not_opened(self):
        remote = self.src("remote.txt")
        real_stat = os.stat

        class Fake:
            st_mode, st_size, st_flags = real_stat(remote).st_mode, 5, self.lc.DATALESS

        opened = self.watch_fingerprints()
        with mock.patch("os.stat", lambda p, *a, **k: Fake if Path(p).name == "remote.txt" else real_stat(p, *a, **k)):
            self.assertEqual(self.states()["evidence/sources/remote.txt"][3], "cloud")
        self.assertEqual(opened, [])

    def test_no_hash_opens_nothing(self):
        self.src("a.txt")
        self.lc.fingerprint = lambda p: self.fail("--no-hash must not fingerprint")
        rows = self.lc.scan_sources(self.root, {}, {}, hash_files=False)
        self.assertEqual([r[3] for r in rows], ["listed"])
        code, out = self.run_cli("--sources", "--no-hash")
        self.assertEqual(code, 0, out)
        self.assertIn("listed only", out)

    def test_a_record_never_claims_the_file_is_used_up(self):
        self.src("a.txt")
        self.intake([("evidence/sources/a.txt", self.fp("a.txt"))])
        code, out = self.run_cli("--sources")
        self.assertIn("never means the file has no other usable evidence", out)

    def test_fingerprint_catches_a_change_between_reading_and_writing(self):
        p = self.src("a.txt", "as read")
        code, h1 = self.run_cli("--fingerprint", "evidence/sources/a.txt")
        self.assertEqual(code, 0, h1)
        p.write_text("edited meanwhile", encoding="utf-8")
        code, h2 = self.run_cli("--fingerprint", "evidence/sources/a.txt")
        self.assertNotEqual(h1, h2)
        card = self.root / "evidence/claims/C-001.md"
        card.write_text("---\nid: C-001\n---\n# C-001 · x\n", encoding="utf-8")
        c1 = self.run_cli("--fingerprint", "evidence/claims/C-001.md")[1]
        card.write_text("---\nid: C-001\n---\n# C-001 · x\nedited by another session\n", encoding="utf-8")
        self.assertNotEqual(c1, self.run_cli("--fingerprint", "evidence/claims/C-001.md")[1])

    def test_fingerprint_refuses_skipped_missing_and_outside_files(self):
        self.src("secret.txt")
        self.intake(skipped=["evidence/sources/secret.txt"])
        code, out = self.run_cli("--fingerprint", "evidence/sources/secret.txt")
        self.assertEqual(code, 1)
        self.assertIn("skipped: not opened", out)
        self.assertEqual(self.run_cli("--fingerprint", "evidence/sources/nope.txt")[0], 1)
        with tempfile.NamedTemporaryFile() as other:
            code, out = self.run_cli("--fingerprint", other.name)
            self.assertEqual(code, 1)
            self.assertIn("outside", out)

    def test_chinese_output(self):
        self.src("a.txt")
        r = subprocess.run([sys.executable, "-I", str(LIST_CLAIMS), "--sources", "--lang", "zh"],
                           cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("新文件", r.stdout)


    # --- the skip list must be checkable, and must over-match rather than under-match ---------

    def test_an_unreadable_intake_stops_the_listing(self):
        self.src("a.txt")
        (self.root / "evidence/INTAKE.md").mkdir()
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)
        self.assertIn("Do not read any raw source", out)
        self.assertNotIn("a.txt", out)
        code, out = self.run_cli("--fingerprint", "evidence/sources/a.txt")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)

    def test_an_intake_with_broken_encoding_is_reported_not_a_traceback(self):
        self.src("a.txt")
        (self.root / "evidence/INTAKE.md").write_bytes(b"## Skipped sources\n| a |\n\xff\xfe broken")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)
        self.assertNotIn("Traceback", out)

    def test_a_missing_intake_is_still_fine(self):
        self.src("a.txt")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 0, out)
        self.assertIn("| new |", out)

    def test_skip_matching_ignores_case_and_unicode_form(self):
        self.src("Secret.txt")
        self.src("caf\u00e9.txt")
        self.intake(skipped=["evidence/sources/secret.TXT", "evidence/sources/cafe\u0301.txt"])
        opened = self.watch_fingerprints()
        st = self.states()
        self.assertEqual(st["evidence/sources/Secret.txt"][3], "skipped")
        self.assertEqual(st["evidence/sources/caf\u00e9.txt"][3], "skipped")
        self.assertEqual(opened, [])
        code, out = self.run_cli("--fingerprint", "evidence/sources/Secret.txt")
        self.assertEqual(code, 1, out)
        self.assertIn("skipped", out)

    def test_records_match_regardless_of_case(self):
        self.src("Report.txt")
        self.intake([("evidence/sources/report.txt", self.fp("Report.txt"))])
        self.assertEqual(self.states()["evidence/sources/Report.txt"][3], "read")

    def test_a_skipped_folder_works_with_or_without_a_trailing_slash(self):
        self.src("private/a.txt")
        for entry in ("evidence/sources/private", "evidence/sources/private/"):
            self.intake(skipped=[entry])
            opened = self.watch_fingerprints()
            self.assertEqual(self.states()["evidence/sources/private/"][3], "skipped")
            self.assertEqual(opened, [])

    def test_a_skip_row_that_cannot_be_read_reliably_fails_closed(self):
        self.src("a|b.txt")
        self.src("other.txt")
        opened = self.watch_fingerprints()
        # plain, or wrapped in backticks: split on "|" first, so the row has an extra cell either way
        for row in ("evidence/sources/a|b.txt", "`evidence/sources/a|b.txt`"):
            self.intake(skipped=[row])
            code, out = self.run_cli("--sources")
            self.assertEqual(code, 1, out)
            self.assertIn("skip rules can't be verified", out)
            self.assertIn("evidence/sources/a", out)
            self.assertNotIn("other.txt", out)
            code, out = self.run_cli("--fingerprint", "evidence/sources/a|b.txt")
            self.assertEqual(code, 1, out)
            self.assertIn("skip rules can't be verified", out)
            with self.assertRaises(self.lc.IntakeUnreadable):
                self.lc.intake_tables(self.root)
        self.assertEqual(opened, [])

    def test_a_pipe_in_the_reason_also_fails_closed(self):
        self.src("a.txt")
        (self.root / "evidence/INTAKE.md").write_text(
            "## Skipped sources\n| File | Reason |\n|---|---|\n| evidence/sources/a.txt | contract | draft |\n", encoding="utf-8")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)

    def test_fingerprint_checks_the_path_it_will_open(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other).resolve()
            (outside / "sub").mkdir()
            (outside / "secret.txt").write_text("EXTERNAL", encoding="utf-8")
            self.link(self.root / "evidence/sources/link", outside / "sub", directory=True)
            # "link/.." is the folder above the link's target, so this reaches the outside file
            code, out = self.run_cli("--fingerprint", "evidence/sources/link/../secret.txt")
            self.assertEqual(code, 1, out)
            self.assertNotRegex(out, r"[0-9a-f]{16}")
        self.src("fine.txt")
        code, out = self.run_cli("--fingerprint", "evidence/sources/../sources/fine.txt")
        self.assertEqual(code, 1, out)  # a ".." is refused outright, even when it would be harmless
        self.assertEqual(self.run_cli("--fingerprint", "evidence/sources/fine.txt")[0], 0)

    def skip_table(self, row):
        (self.root / "evidence/INTAKE.md").write_text(
            "## Skipped sources\n| File | Reason |\n|---|---|\n" + row + "\n", encoding="utf-8")

    def test_skip_paths_with_dots_and_double_slashes_still_match(self):
        self.src("secret.txt")
        for row in ("evidence/sources//secret.txt", "evidence/sources/./secret.txt", "evidence/./sources/secret.txt"):
            with self.subTest(row=row):
                self.skip_table("| " + row + " | private |")
                code, out = self.run_cli("--sources")
                self.assertNotRegex(out, r"[0-9a-f]{16}", out)
                self.assertEqual(self.run_cli("--fingerprint", "evidence/sources/secret.txt")[0], 1)

    def test_a_dotdot_in_a_skip_row_fails_closed(self):
        self.src("secret.txt")
        self.skip_table("| evidence/sources/x/../secret.txt | private |")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)

    def test_an_intake_link_that_leads_nowhere_fails_closed(self):
        self.src("secret.txt")
        self.link(self.root / "evidence/INTAKE.md", self.root / "nowhere.md")
        for args in (("--sources",), ("--fingerprint", "evidence/sources/secret.txt")):
            code, out = self.run_cli(*args)
            self.assertEqual(code, 1, out)
            self.assertIn("skip rules can't be verified", out)
        # a really missing INTAKE is still just "no records"
        (self.root / "evidence/INTAKE.md").unlink()
        self.assertEqual(self.run_cli("--sources")[0], 0)

    def test_spaces_inside_backticks_fail_closed(self):
        self.src("a.txt")
        self.skip_table("| ` evidence/sources/a.txt ` | private |")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)
        (self.root / "evidence/INTAKE.md").write_text(
            "## Source records\n| File | Fingerprint |\n|---|---|\n| ` evidence/sources/a.txt ` | 0123456789abcdef |\n", encoding="utf-8")
        self.assertEqual(self.run_cli("--sources")[0], 1)

    def test_a_skipped_sources_folder_is_not_entered(self):
        self.src("a.txt"); self.src("deep/b.txt")
        self.skip_table("| evidence/sources | all private |")
        with mock.patch("os.walk", side_effect=AssertionError("entered")):
            records, skipped = self.lc.intake_tables(self.root)
            rows = self.lc.scan_sources(self.root, records, skipped)
        self.assertEqual([r[3] for r in rows], ["skipped"])
        self.assertEqual(self.run_cli("--sources")[0], 0)

    def test_an_absolute_skip_path_fails_closed(self):
        self.src("secret.txt")
        self.skip_table("| " + str(self.root / "evidence/sources/secret.txt") + " | private |")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)
        self.assertNotRegex(out, r"[0-9a-f]{16}")

    def test_a_name_with_a_pipe_cut_in_two_fails_closed(self):
        self.src("a|b.txt")
        self.skip_table("| evidence/sources/a|b.txt |")  # no reason column: it splits into two cells
        for args in (("--sources",), ("--fingerprint", "evidence/sources/a|b.txt")):
            code, out = self.run_cli(*args)
            self.assertEqual(code, 1, out)
            self.assertIn("skip rules can't be verified", out)

    def test_an_unpaired_backtick_fails_closed(self):
        self.src("a.txt")
        self.skip_table("| `evidence/sources/a.txt | private |")
        code, out = self.run_cli("--sources")
        self.assertEqual(code, 1, out)
        self.assertIn("skip rules can't be verified", out)

    def test_an_unreadable_folder_does_not_hide_a_folder_with_a_similar_name(self):
        self.src("a/in.txt"); self.src("ab/other.txt")
        self.intake([("evidence/sources/ab/x.txt", "0" * 16)])
        real_scandir = os.scandir

        def fake(p="."):
            if str(p).endswith("sources/a"):
                raise PermissionError(13, "Permission denied", str(p))
            return real_scandir(p)
        os.scandir = fake
        try:
            st = self.states()
        finally:
            os.scandir = real_scandir
        self.assertEqual(st["evidence/sources/a/"][3], "unreadable")
        self.assertEqual(st["evidence/sources/ab/x.txt"][3], "gone")  # "ab" is not inside "a"

    def test_a_name_with_a_pipe_is_flagged_when_it_cannot_be_recorded(self):
        self.src("a|b.txt")
        code, out = self.run_cli("--sources")
        self.assertIn("can't be written in the INTAKE table", out)

    def test_a_folder_that_cannot_be_entered_is_reported_not_forgotten(self):
        self.src("ok.txt")
        self.src("locked/in.txt")
        self.intake([("evidence/sources/locked/in.txt", "0" * 16)])
        real_scandir = os.scandir

        def fake(p="."):
            if str(p).endswith("locked"):
                raise PermissionError(13, "Permission denied", str(p))
            return real_scandir(p)
        os.scandir = fake
        try:
            st = self.states()
        finally:
            os.scandir = real_scandir
        self.assertEqual(st["evidence/sources/locked/"][3], "unreadable")
        self.assertNotIn("evidence/sources/locked/in.txt", st)  # not reported as a vanished file
        self.assertEqual(st["evidence/sources/ok.txt"][3], "new")


class ListClaims(unittest.TestCase):
    """list_claims.py: one line per card, protected cards marked, and the read-in-full advice by size."""

    def test_lists_every_card(self):
        ex = SCRIPT.parent.parent / "examples" / "jordan-lee"
        r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("list_claims.py"))], cwd=ex, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        rows = [l for l in r.stdout.splitlines() if l.startswith("| C-")]
        self.assertEqual(len(rows), 5)
        self.assertIn("5 ", r.stdout.splitlines()[-1].replace("共 ", ""))

    def test_big_bank_names_the_protected_cards(self):
        with tempfile.TemporaryDirectory() as d:
            claims = Path(d) / "evidence" / "claims"
            claims.mkdir(parents=True)
            for i in range(1, 18):
                claims.joinpath(f"C-{i:03}.md").write_text(
                    f"---\nid: C-{i:03}\nstatus: Safe to draft\nprotected: {'true' if i == 7 else 'false'}\n---\n# C-{i:03} · Card {i}\n",
                    encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("list_claims.py"))], cwd=d, capture_output=True, text=True)
            self.assertIn("17", r.stdout.splitlines()[-1])
            self.assertIn("(C-007)" if "(C-007)" in r.stdout else "（C-007）", r.stdout)


class ReportRounding(unittest.TestCase):
    """report_score.py rounds like the page (JavaScript Math.round): 62.5 is 63, not Python's 62."""

    def test_half_rounds_up_like_the_page(self):
        sys.path.insert(0, str(SCRIPT.parent))
        import report_score
        self.assertEqual(report_score.half_up(62.5), 63)
        self.assertEqual(report_score.half_up(62.4), 62)
        bullets = [{"result": i < 5} for i in range(8)]  # R1 only: 5 of 8 = 62.5%
        d = {"meta": {"mode": "checkup"}, "bullets": bullets, "dims": {k: k == "R1" for k in ("R2", "R3", "R4", "R5", "R1")}}
        self.assertEqual(report_score.score(d)[0], 63)
        page = (SCRIPT.parent.parent / "report" / "template.html").read_text(encoding="utf-8")
        self.assertIn("Math.round(acc / wsum * 100)", page)  # the page's formula this mirrors


class ReportShare(unittest.TestCase):
    """report_share.py keeps the score and removes every private string from the sample report."""

    def test_share_copy_is_clean_and_scores_the_same(self):
        root = SCRIPT.parent.parent
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "r.html"
            src.write_text((root / "report" / "template.html").read_text(encoding="utf-8"), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("report_share.py")), str(src)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)
            out = (Path(d) / "r-share.html")
            body = out.read_text(encoding="utf-8")
            for private in ("Jordan", "Northwind", "Acme", "old-resume", "webinar", "tiering"):
                self.assertNotIn(private, body)
            self.assertIn('"gate": true', body)
            s = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("report_score.py")), str(out)], capture_output=True, text=True)
            self.assertIn("38 / 100", s.stdout)


    def test_share_copy_ignores_text_outside_the_data_block(self):
        root = SCRIPT.parent.parent
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "r.html"
            page = (root / "report" / "template.html").read_text(encoding="utf-8")
            src.write_text(page.replace("<title>", "<title>Private note Zephyrine ", 1), encoding="utf-8")
            subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("report_share.py")), str(src)], capture_output=True, text=True)
            self.assertNotIn("Zephyrine", (Path(d) / "r-share.html").read_text(encoding="utf-8"))

    def test_embedded_data_cannot_close_the_script_block(self):
        sys.path.insert(0, str(SCRIPT.parent))
        import json, re, report_share
        data = {"meta": {"share_name": "</script><script>alert(1)</script><!--"}}
        html = report_share.embed('<script type="application/json" id="report-data">{}</script>', data)
        inner = re.search(r'id="report-data">(.*)</script>$', html, re.S).group(1)
        self.assertNotIn("<", inner)
        self.assertEqual(json.loads(inner), data)


class ReportCompare(unittest.TestCase):
    """report_compare.py: the example poster goes 38 -> 89, with no private text unless a module adds it."""

    def test_poster(self):
        root = SCRIPT.parent.parent
        ex = root / "examples" / "jordan-lee" / "reports"
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "poster.html"
            r = subprocess.run([sys.executable, "-I", str(SCRIPT.with_name("report_compare.py")),
                                str(ex / "2026-05-02-checkup.html"), str(ex / "2026-05-10-checkup.html"), "--out", str(out),
                                "--tag", "Partner programs"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("38 -> 89", r.stdout)
            body = out.read_text(encoding="utf-8")
            self.assertIn("Partner programs", body)
            for private in ("Jordan", "Northwind", "Acme", "old-resume", "webinar"):
                self.assertNotIn(private, body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
