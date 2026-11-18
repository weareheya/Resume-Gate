# REVIEW-CHECKLIST: AI self-review

After a resume is written and before the user sees it, the AI must go through this checklist and fix what it finds. When handing off, include what you changed, what's still open, and the highlights.

The writing guidance follows standard university career-center resume guides (start with a strong verb, quantify results, no duty-style descriptions, no empty adjectives) and common ATS advice (single column, standard section names, scannable in seconds). Specific statistics from third-party blogs are unreliable, so don't rely on them.

## A. Facts (pass this first; if it fails, stop here)

Run `python3 scripts/check_claims.py cv/resumes/<id>.md` first. It checks the first two items below mechanically, and also that every number on a checked line appears in the card it cites. It fails if it can't find a Summary or Experience section, and it lists any other section (Skills, Projects…) as not verified: check those by hand. The rest still need judgment.

- [ ] Every line traces to a Claim Card. An approved or sent resume is not evidence, only approved wording
- [ ] Every bullet carries its Claim ID in an HTML comment, and each one points to a card marked `Safe to draft`
- [ ] Numbers keep their units and scope (currency, time window, qualifiers like "potential" or "cumulative")
- [ ] Individual contribution is separate from team results; titles match the employment record and aren't inflated
- [ ] Start and end dates, company type, and role are correct
- [ ] A result that happened at the same time isn't credited entirely to the candidate (causality)
- [ ] Anything the JD asks for without evidence is **not written** and is listed in the Coverage Report
- [ ] No sensitive information (a former employer's confidential details, other people's private information)

## B. Writing

These are defaults. A structure the user has already approved takes priority over them.

- [ ] Summary is short (about 3–4 lines): positioning plus the 2–4 strongest proof points. No filler like "results-oriented" or "team player"
- [ ] Bullets start with a strong verb where that's accurate. Avoid duty-style openers like "Responsible for" or "Duties included." "Helped" and "Served as" are fine when they're the honest description: the wording must never claim more than the role was
- [ ] Each bullet tries to say what you did, how, and what came of it, with numbers where you have them
- [ ] Each bullet is at most 3 lines once laid out, with roughly 2–5 bullets per role (more for recent, relevant roles)
- [ ] The bullet most relevant to the target JD comes first in each role
- [ ] Capitalization, punctuation, and currency formats are consistent
- [ ] Contact details are clean: no `https://`, readable link text
- [ ] Section names are standard (Summary / Experience / Education / Skills)

## C. Layout

- [ ] Exported PDF fills its pages: by default **1 or 2 full pages**, with the content on the last page reaching at least 85% of the page height (both defaults can be changed in D-009), not just a few stray lines
- [ ] Page breaks fall between roles, not between a role's heading and its bullets
- [ ] No one- or two-word widows; reword if you can
- [ ] If your resume tool has a built-in checker, it reports zero errors and zero warnings

Fix order: content first, then layout settings (font size 10.5–12.5, line spacing 1.3–1.5, margins, paragraph spacing).

Check tool:

```bash
swift scripts/pdf_fill.swift <cv.pdf> <output-dir>
```

It checks the page count (default 1 or 2) and how far down the last page the content reaches (default 85%). "Reach" is where the last content ends, not how much of the page is used, so a page number in the footer can make a nearly empty page look full. If your resume has a footer, pass `--ignore-bottom=4` (just the footer's height; it also ignores real content in that zone). Always look at the PNGs as well.

## D. Handoff format

1. **Page images**: paste the PNGs that `pdf_fill` generated. Don't make the user go find the file.
2. **Layout result**: page count and how far down the content reaches on each page
3. **Self-review findings and fixes** (as a table)
4. **Highlights**: the 3–5 strongest selling points in this version, and which JD requirement each answers
5. **Risks and gaps**: what the JD wants but you have no evidence for, and what the candidate must be ready to explain in an interview
6. **Diff against the baseline**: the first time the user sees a resume for a job, include the full text; after that, list only the changes
