# REPORT: Resume checkup and job-fit report

A visual, scored report on a resume. The AI fills in the data; the template does the counting and the maths, so the same resume gets the same score whichever AI fills it in.

- **Template**: [`report/template.html`](../report/template.html). Open it in a browser to see a made-up example.
- **Output**: copy it to `reports/<date>-checkup.html` (or `-<job-id>.html` for a job-fit report), replace the data block, and open it in a browser. Print to PDF from the browser if you want a file.
- **Two views, one file.** *Full report* is for you: every bullet, every fix. *Share card* (the button at the top, or add `#share` to the address) is a portrait card to screenshot and post: score, band and dimension bars, with a link back to Resume-Gate. It hides your name, employer, target job and bullet text; set `"share_name"` in `meta` only if you want a name on it.
- **As an image.** Many chat windows and preview panes don't run JavaScript, so the report file shows only its watermark there. `python3 scripts/report_png.py reports/<file>.html` saves the share card as `<file>-card.png` (1080 px wide, ready to post) using the Chrome, Edge or Brave already on your computer; add `--full` for the whole report as `<file>-full.png`, which is for your eyes only. It works on `-share.html` copies and posters too.
- **Share copy.** The full report file still holds everything, so it must never be sent around. `python3 scripts/report_share.py reports/<file>.html` writes `<file>-share.html`: same score, no private text at all, opens on the share card. Add `--name "…"` to put a name on it.

## Sharing: score only, or with modules the user picks

By default a share card or poster shows **only the score and the dimension bars**. Before making one, show the user this menu with the exact text you'd use for each module, and add only what they tick:

| Module | Flag | What it shows | Rule |
|---|---|---|---|
| Name | `--name` | A name on the card | Only if the user asks |
| Headline | `--headline` | One line of positioning | Offer 3 candidates. Each must come from a `Safe to draft` Claim Card. Concrete beats hype: "Took channel partners from 12 to 40" over "BD guru" |
| Target | `--target` | The kind of role, e.g. "Channel BD" | A role type, never an employer |
| Tags | `--tag` (up to 5) | Keyword tags | Short nouns from the Claim Cards: skills or areas the evidence backs |
| Highlights | `--highlight` (up to 2) | One-line strengths | From the cards, with employer and client names removed |

None of them may name an employer or client, or carry anything the evidence can't support. A playful headline is fine if the user wants one, as long as the cards back it.

- **Share card**: `python3 scripts/report_share.py reports/<file>.html [modules]`
- **Before-and-after poster**: `python3 scripts/report_compare.py reports/<before>.html reports/<after>.html [modules]`. Both reports are scored with the same formula; the poster shows both scores, each dimension before and after, and the two dates. If the reports were made in different modes, only the shared dimensions are compared and the poster says so. Example: [`examples/jordan-lee/reports/`](../examples/jordan-lee/reports/).

## Two modes

| Mode | When | Dimensions |
|---|---|---|
| **Checkup** | Step 0, or any time, with no particular job in mind | R1 to R5 |
| **Job fit** | A specific JD, usually at S3 or after S6 | R1 to R5, plus J1 to J3 |

Any dimension can be switched off in the data block (`"dims"`). Switched-off dimensions aren't scored, and the remaining weights are rescaled, so the total is still out of 100.

## Dimensions

The AI marks each Experience bullet (yes or no) and runs the structure checks. The template counts.

| ID | Dimension | What the AI marks | Score | Weight |
|---|---|---|---|---|
| R1 | Results | The bullet says what came of the work, not only what was done | marked / all bullets | 25 |
| R2 | Numbers | The bullet has at least one number: a count, %, money, time, or size | marked / all bullets | 20 |
| R3 | Action-led | The bullet starts with a verb that says what you did. Not "Responsible for", "Duties included", "Worked on", nor weak verbs such as "Helped", "Assisted", "Supported", "Participated in" | marked / all bullets | 15 |
| R4 | Specific | No filler: "results-oriented", "passionate", "various", "etc.", "team player" | marked / all bullets | 10 |
| R5 | Structure | The checks below | passed / run | 15 |
| J1 | JD coverage | Each core JD requirement: direct, partial, or no evidence. Map the five kinds in WORKFLOW S3: Direct → `direct`, Transferable or combined → `partial`, the rest → `none`. Mark a must-have with `"gate": true`; `report_score.py` lists any gate not directly met. In a job-fit report J1 is always scored: with no requirements it counts 0, so leaving the JD out can't raise the score | (direct + ½ × partial) / requirements | 30 |
| J2 | Placement | The best evidence for a covered requirement sits in the Summary or the first bullet of a role | marked / covered requirements | 15 |
| J3 | Wording | Of the JD's key terms the evidence supports, how many the resume uses | used / supported | 10 |

**Marking examples**: when in doubt, mark by this table. A different AI marking the same bullet should land on the same answer.

| Dimension | Marks yes | Marks no |
|---|---|---|
| R1 Results | Grew active partners from 12 to 40. (says what came of it) | Managed relationships with channel partners. (only what you were doing) |
| R1 Results | Cut onboarding from 3 weeks to 4 days. (no revenue needed; the result is time saved) | Launched a partner portal. (launching is the action; say what happened next) |
| R2 Numbers | Ran four webinars with 380 registrants. | Ran several webinars with strong turnout. |
| R2 Numbers | Led a team of 6 across 3 markets. (size counts) | Led a cross-functional team. (no quantity at all) |
| R3 Action-led | Negotiated / Built / Rebuilt / Launched … | Responsible for… / Worked on… / Duties included… |
| R3 Action-led | Built the pitch deck that won the account. (says what you did) | Helped / Assisted / Supported / Participated in / Involved in… (weak verbs: they hide which part was yours) |
| R4 Specific | Translated the roadmap into launch messaging for 3 markets. | Drove various initiatives to improve results, etc. |
| R4 Specific | Reframed the pitch around player-owned AI agents. | Passionate, results-oriented team player. (describes you, not a fact) |

A weak verb marked no doesn't mean the work can't go in. If your part really was supporting, say what you did in that part. Fixes go in that direction; they never inflate a supporting role into a leading one.

**R5 structure checks**: Summary is 4 lines or fewer · section names are standard (Summary, Experience, Education, Skills) · the two most recent roles have 2 to 5 bullets each, earlier roles 1 to 3 (one bullet for an early or short role is normal) · no bullet runs past 3 lines · contact details are clean (no `https://`, readable links) · single column, no text inside images or tables (if known; otherwise leave it out).

**Bands**: 85 to 100 Strong · 70 to 84 Solid · 55 to 69 Usable, but losing points · below 55 Needs a rewrite.

## Interview readiness (not scored)

The score measures how the resume reads. Evidence doesn't change that, so it isn't scored. It decides something else: whether you can stand behind each bullet when an interviewer asks where a number came from, or which part was yours. The report shows it in its own panel.

The AI marks each bullet's `sourced` and lists its Claim IDs in `claims`, for example `"claims": ["C-004", "C-012"]`. Claim IDs never appear on the resume itself, so this needs the evidence bank (`evidence/claims/`, or wherever your evidence lives). Don't put IDs in `where`.

| `sourced` | Means | Shown as |
|---|---|---|
| `true` | A `Safe to draft` Claim Card covers the whole bullet | ✓ Confirmed |
| `"partial"` | A card exists but is still under review, or covers only part of the bullet | ½ Under review or partial |
| `false` | No card yet | – No card yet |

**First checkup, before Step 0:** there are no cards yet, so leave `sourced` false and `claims` empty for every bullet. The panel then says it unlocks in stage 2, after the Step 0 interview, and the bullet table drops the evidence column. Nothing is lost from the score. If cards exist but the AI can't reach them, it says so in the summary.

## Rules for the AI

- **Mark, don't score.** Fill in per-bullet yes/no marks and the check results. Never type a total score or a percentage: the template computes them.
- **Every mark can be checked.** The report lists each bullet with its marks, so the user can see why a dimension scored what it did.
- **Strengths, fixes and gaps use only facts already in the resume or the Claim Cards.** A suggested fix never adds a new fact or number. If a fix needs information the resume doesn't have, say what to ask the user.
- **At most 5 fixes**, most important first.
- Then run `python3 scripts/report_score.py reports/<file>.html` and quote its score in the chat with a three-line summary: the score and band, the strongest point, and the first fix. The `summary` lines in the data block don't mention the score; the page shows it.
- **Show the report in the chat.** Run `python3 scripts/report_png.py reports/<file>.html` and show the card image (in Claude Code, read the PNG so it appears in the conversation; elsewhere, give its path). If no browser is found, give the HTML path and say to open it in a browser.
- **First checkup, no Claim Cards yet: say what stage 2 is**, in two lines. Stage 2 is a short interview on your 3 strongest accomplishments, written up as Claim Cards. It unlocks interview readiness: which bullets you can back when an interviewer asks where a number came from or what part was yours. It isn't scored and doesn't change the resume's score.
- **Then ask once: "Want a version you can share?"** If yes, show the module menu above, then run `scripts/report_share.py` with only the ticked modules, give the user the `-share.html` path, and remind them to share only that file or a screenshot of the share card, never the full report.

## What the score is and isn't

The standard is Resume-Gate's own, built on Harvard's career-office resume guides (action verbs, quantified results, no duty-style descriptions, no empty adjectives) and common ATS advice (standard sections, single column). It scores only what a reader sees on the page; whether the evidence behind it is ready is shown separately, under interview readiness. It is **not** a recruiter's score and doesn't predict interviews. Use it to compare versions of the same resume over time.
