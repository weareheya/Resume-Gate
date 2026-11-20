# REVIEW-CHECKLIST: AI self-review

After a resume is written and before the user sees it, the AI must go through this checklist and fix what it finds. When handing off, include what you changed, what's still open, and the highlights.

Two sources, each for one job:

- **How to write a resume**: Harvard's career-office resume guides: [Harvard College](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/), [Harvard Extension School](https://careerservices.fas.harvard.edu/resources/hes-create-impactful-resumes-and-cover-letters/), and the [Harvard Law School resume workshop](https://hls.harvard.edu/wp-content/uploads/2024/06/Resume-Workshop-for-Website.pdf). What they agree on: start each bullet with an action verb, quantify where you can, replace "responsible for" with what you actually did, skip empty adjectives, and write for someone who scans in seconds.
- **Checking that a bullet tells the whole story**: STAR (Situation, Task, Action, Result). It comes from DDI's Targeted Selection, a structured behavioral-interview method from 1974 ([DDI's explanation](https://www.ddi.com/blog/what-is-the-star-format)), and was built for interviewers collecting complete answers. It isn't a resume format. Here it's only a checklist; see section B.

Plus common ATS advice (single column, standard section names). Specific statistics from third-party blogs are unreliable, so don't rely on them.

## A. Facts (pass this first; if it fails, stop here)

Run `python3 scripts/validate_evidence.py` and `python3 scripts/check_claims.py cv/resumes/<id>.md` first. They check the first two items below mechanically, and also that every number on a checked line comes from the card it cites (same value, scale and currency), that no banned word from the card is used, that role headings and Education match `evidence/profile.md`, and that protected claims keep their numbers. It fails if it can't find a Summary or Experience section, and it lists any other section (Skills, Projects…) as not verified: check those by hand. The rest still need judgment.

- [ ] Every line traces to a Claim Card. An approved or sent resume is not evidence, only approved wording
- [ ] Every bullet carries its Claim ID in an HTML comment, and each one points to a card marked `Safe to draft`; no number used is marked `to verify` on its card
- [ ] Numbers keep their units and scope (currency, time window, qualifiers like "potential" or "cumulative")
- [ ] Individual contribution is separate from team results; titles match the employment record and aren't inflated
- [ ] Start and end dates, company type, and role are correct
- [ ] A result that happened at the same time isn't credited entirely to the candidate (causality); a link that *can* be shown is written, not split apart by reflex (D-014)
- [ ] Claims marked `protected` aren't just present; **their meaning hasn't been weakened**. Compare them sentence by sentence with the approved wording. `check_claims.py` checks that the ID and its confirmed numbers are still there, but can't judge wording (LESSONS L-12)
- [ ] Anything the JD asks for without evidence is **not written** and is listed in the Coverage Report
- [ ] No sensitive information (a former employer's confidential details, other people's private information)

## B. Writing

These are defaults. A structure the user has already approved takes priority over them.

- [ ] Summary is short (about 3–4 lines): positioning plus the 2–4 strongest proof points. No filler like "results-oriented" or "team player"
- [ ] Bullets start with a strong verb where that's accurate. Avoid duty-style openers like "Responsible for" or "Duties included." "Helped" and "Served as" are fine when they're the honest description: the wording must never claim more than the role was
- [ ] Each bullet tries to say what you did, how, and what came of it, with numbers where you have them
- [ ] Check each strong bullet against STAR: the candidate's own action (A) and the result (R) are both there; the situation (S) and task (T) appear only if the bullet makes no sense without them. On paper, compress it to action + key judgment or deliverable + result, not four sentences. Save the full STAR for the interview
- [ ] Each bullet is at most 3 lines once laid out, with 2–5 bullets for each of the two most recent roles and 1–3 for earlier ones
- [ ] The bullet most relevant to the target JD comes first in each role
- [ ] Nothing reads like a disclaimer: while staying accurate, the words go to proving what was done, not to explaining what wasn't (D-015)
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
