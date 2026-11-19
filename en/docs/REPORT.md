# REPORT: Resume checkup and job-fit report

A visual, scored report on a resume. The AI fills in the data; the template does the counting and the maths, so the same resume gets the same score whichever AI fills it in.

- **Template**: [`report/template.html`](../report/template.html). Open it in a browser to see a made-up example.
- **Output**: copy it to `reports/<date>-checkup.html` (or `-<job-id>.html` for a job-fit report), replace the data block, and open it in a browser. Print to PDF from the browser if you want a file.
- **Two views, one file.** *Full report* is for you: every bullet, every fix. *Share card* (the button at the top, or add `#share` to the address) is a portrait card to screenshot and post: score, band and dimension bars, with a link back to Resume-Gate. It hides your name, employer, target job and bullet text; set `"share_name"` in `meta` only if you want a name on it.
- **Share copy.** The full report file still holds everything, so it must never be sent around. `python3 scripts/report_share.py reports/<file>.html` writes `<file>-share.html`: same score, no private text at all, opens on the share card. Add `--name "…"` to put a name on it.

## Two modes

| Mode | When | Dimensions |
|---|---|---|
| **Checkup** | Step 0, or any time, with no particular job in mind | R1 to R6 |
| **Job fit** | A specific JD, usually at S3 or after S6 | R1 to R6, plus J1 to J3 |

Any dimension can be switched off in the data block (`"dims"`). Switched-off dimensions aren't scored, and the remaining weights are rescaled, so the total is still out of 100.

## Dimensions

The AI marks each Experience bullet (yes or no) and runs the structure checks. The template counts.

| ID | Dimension | What the AI marks | Score | Weight |
|---|---|---|---|---|
| R1 | Results | The bullet says what came of the work, not only what was done | marked / all bullets | 25 |
| R2 | Numbers | The bullet has at least one number: a count, %, money, time, or size | marked / all bullets | 20 |
| R3 | Action-led | The bullet starts with an action verb, not "Responsible for", "Duties included", "Worked on" | marked / all bullets | 15 |
| R4 | Specific | No filler: "results-oriented", "passionate", "various", "etc.", "team player" | marked / all bullets | 10 |
| R5 | Structure | The checks below | passed / run | 15 |
| R6 | Sourced | Backed by a `Safe to draft` Claim Card | marked / all bullets | 15 |
| J1 | JD coverage | Each core JD requirement: direct, partial, or no evidence | (direct + ½ × partial) / requirements | 30 |
| J2 | Placement | The best evidence for a covered requirement sits in the Summary or the first bullet of a role | marked / covered requirements | 15 |
| J3 | Wording | Of the JD's key terms the evidence supports, how many the resume uses | used / supported | 10 |

R6 is 0 before Step 0, and that's expected: no Claim Cards exist yet. It's the part the interview raises.

**R5 structure checks**: Summary is 4 lines or fewer · section names are standard (Summary, Experience, Education, Skills) · each role has 2 to 5 bullets · no bullet runs past 3 lines · contact details are clean (no `https://`, readable links) · single column, no text inside images or tables (if known; otherwise leave it out).

**Bands**: 85 to 100 Strong · 70 to 84 Solid · 55 to 69 Usable, but losing points · below 55 Needs a rewrite.

## Rules for the AI

- **Mark, don't score.** Fill in per-bullet yes/no marks and the check results. Never type a total score or a percentage: the template computes them.
- **Every mark can be checked.** The report lists each bullet with its marks, so the user can see why a dimension scored what it did.
- **Strengths, fixes and gaps use only facts already in the resume or the Claim Cards.** A suggested fix never adds a new fact or number. If a fix needs information the resume doesn't have, say what to ask the user.
- **At most 5 fixes**, most important first.
- Then run `python3 scripts/report_score.py reports/<file>.html` and quote its score in the chat with a three-line summary: the score and band, the strongest point, and the first fix. The `summary` lines in the data block don't mention the score; the page shows it.
- **Then ask once: "Want a version you can share?"** If yes, run `scripts/report_share.py`, give the user the `-share.html` path, and remind them to share only that file or a screenshot of the share card, never the full report.

## What the score is and isn't

The standard is Resume-Gate's own, built on Harvard's career-office resume guides (action verbs, quantified results, no duty-style descriptions, no empty adjectives) and common ATS advice (standard sections, single column), plus this kit's sourcing rule. It is **not** a recruiter's score and doesn't predict interviews. Use it to compare versions of the same resume over time.
