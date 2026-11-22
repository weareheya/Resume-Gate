# REVIEW-CHECKLIST: AI self-review

After a resume is written and before the user sees it, the AI must go through this checklist and fix what it finds. When handing off, include what you changed, what's still open, and the highlights. For a [quick edit](WORKFLOW.md#task-modes), go through section A for the changed lines only. Sections C and D's page images belong to Finalize.

Two sources, each for one job:

- **How to write a resume**: Harvard's career-office resume guides: [Harvard College](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/), [Harvard Extension School](https://careerservices.fas.harvard.edu/resources/hes-create-impactful-resumes-and-cover-letters/), and the [Harvard Law School resume workshop](https://hls.harvard.edu/wp-content/uploads/2024/06/Resume-Workshop-for-Website.pdf). What they agree on: start each bullet with an action verb, quantify where you can, replace "responsible for" with what you actually did, skip empty adjectives, and write for someone who scans in seconds.
- **Checking that a bullet tells the whole story**: STAR (Situation, Task, Action, Result). It comes from DDI's Targeted Selection, a structured behavioral-interview method from 1974 ([DDI's explanation](https://www.ddi.com/blog/what-is-the-star-format)), and was built for interviewers collecting complete answers. It isn't a resume format. Here it's only a checklist; see section B.

Plus common ATS advice (single column, standard section names). Specific statistics from third-party blogs are unreliable, so don't rely on them.

## A. Facts (pass this first; if it fails, stop here)

Run `python3 scripts/validate_evidence.py` and `python3 scripts/check_claims.py cv/resumes/<id>.md` first. They check the first two items below mechanically, plus numbers, banned words, roles and protected claims ([what the scripts check](../README.md#what-the-scripts-check-and-what-they-dont)). Any section they list as not verified (Skills, Projects…) you check by hand. The rest still need judgment.

- [ ] Every line traces to a Claim Card. An approved or sent resume is not evidence, only approved wording
- [ ] Every bullet carries its Claim ID in an HTML comment, and each one points to a card marked `Safe to draft`; no number used is marked `to verify` on its card
- [ ] Numbers keep their units and scope (currency, time window, qualifiers like "potential" or "cumulative")
- [ ] Each line respects its card's "Don't rephrase as". The question is whether a line claims someone else's work as yours alone ("built the portal"). Shared wording such as "built with engineering" is reasonable packaging, and some vagueness is fine. `check_claims.py` warns on quoted wording from that section: read each WARN, and reword only if the line takes sole credit. Don't fix it by going quiet about a real collaboration (D-015, LESSONS L-14)
- [ ] Individual contribution is separate from team results; titles match the employment record and aren't inflated
- [ ] Start and end dates, company type, and role are correct
- [ ] A result that happened at the same time isn't credited entirely to the candidate (causality); a link that *can* be shown is written, not split apart by reflex (D-014)
- [ ] Claims marked `protected` aren't just present; **their meaning hasn't been weakened**. Compare them sentence by sentence with the approved wording. `check_claims.py` checks that the ID and its confirmed numbers are still there, but can't judge wording (LESSONS L-12)
- [ ] Anything the JD asks for without evidence is **not written** and is listed in the Coverage Report, and nothing is called "no evidence" before the cards and the sources were checked; what couldn't be checked is reported as that, and no source the user skipped was opened (D-021)
- [ ] Nothing strong was left out by accident: every Claim Card is in the evidence table (unused ones may share a line; `check_claims.py` warns on a missing one), and any unused card that beats something in the resume was swapped in or has a reason (D-019)
- [ ] Any fact the user corrected in this session is on its card, and no line still says the old version. Every WARN about a card that changed after approval, or a line copied from a baseline approved before a change, is either fixed or shown to the user (D-020)
- [ ] No sensitive information (a former employer's confidential details, other people's private information)

## B. Writing

These are defaults. A structure the user has already approved takes priority over them.

- [ ] Summary is short (about 3–4 lines): positioning plus the 2–4 strongest proof points. No filler like "results-oriented" or "team player"
- [ ] Bullets start with a strong verb where that's accurate. Avoid duty-style openers like "Responsible for" or "Duties included." "Helped" and "Served as" are fine when they're the honest description: the wording must never claim more than the role was
- [ ] Each bullet tries to say what you did, how, and what came of it, with numbers where you have them
- [ ] Check each strong bullet against STAR: the candidate's own action (A) and the result (R) are both there; the situation (S) and task (T) appear only if the bullet makes no sense without them. On paper, compress it to action + key judgment or deliverable + result, not four sentences. Save the full STAR for the interview
- [ ] Each bullet is about 3 lines or fewer once laid out (a key experience may run longer when it earns the space; say which and why), with 2–5 bullets for each of the two most recent roles and 1–3 for earlier ones
- [ ] The bullet most relevant to the target JD comes first in each role
- [ ] Nothing reads like a disclaimer: while staying accurate, the words go to proving what was done, not to explaining what wasn't (D-015)
- [ ] Capitalization, punctuation, and currency formats are consistent
- [ ] Contact details are clean: no `https://`, readable link text
- [ ] Section names are standard (Summary / Experience / Education / Skills)

## C. Layout (at Finalize)

- [ ] Exported PDF fills its pages: by default **1 or 2 full pages**, with the content on the last page reaching at least 85% of the page height (both defaults can be changed in D-009), not just a few stray lines
- [ ] Page breaks fall between roles, not between a role's heading and its bullets
- [ ] When fixing one layout rule would break another (for example, tighter margins to avoid an orphaned heading leave the last page under the fill default), keep this order: no orphaned heading or widow, then the page count, then the fill default. The fill default is a warning, not a gate: tell the user which rule you let slide and why
- [ ] No one- or two-word widows; reword if you can
- [ ] If your resume tool has a built-in checker, it reports zero errors and zero warnings

Fix order: content first, then layout settings (font size 10.5–12.5, line spacing 1.3–1.5, margins, paragraph spacing).

Check tool:

```bash
swift scripts/pdf_fill.swift <cv.pdf> <output-dir>
```

It needs macOS. On any other computer, look at the PDF yourself if your tool can, and ask the user to open it and confirm the page count and that the last page isn't just a few stray lines; the check is done only when they say so. It checks the page count (default 1 or 2) and how far down the last page the content reaches (default 85%). "Reach" is where the last content ends, not how much of the page is used, so a page number in the footer can make a nearly empty page look full. If your resume has a footer, pass `--ignore-bottom=4` (just the footer's height; it also ignores real content in that zone). Always look at the PNGs as well.

## D. Handoff format

1. **Page images** (at Finalize): paste the PNGs that `pdf_fill` generated, or on other computers say that the user confirmed the layout. Don't make the user go find the file.
2. **Layout result** (at Finalize): page count and how far down the content reaches on each page
3. **Self-review findings and fixes** (as a table)
4. **Highlights**: the 3–5 strongest selling points in this version, and which JD requirement each answers
5. **Risks and gaps**: what the JD wants but you have no evidence for, and what the candidate must be ready to explain in an interview
6. **Diff against the baseline**: the first time the user sees a resume for a job, include the full text; after that, list only the changes
