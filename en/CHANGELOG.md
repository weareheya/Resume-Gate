# Changelog

What changed in each version, and whether you need to do anything. Your version is in `VERSION`. To update, paste prompt 5 from `docs/PROMPTS.md`.

## 0.3.0 · 2026-11-20

Evidence checks are much harder to slip past. Every case below used to pass `check_claims.py` and now fails.

- **Numbers keep their meaning.** A number only counts if it comes from the card's title, What happened, Attribution, Approved wording or Numbers table. Numbers in "Don't rephrase as", Source, Notes or the Claim ID itself no longer count, so "Closed 003 deals" citing C-003 fails. Scaled amounts are compared by value (US$2.1M = US$2,100,000, but not US$2.1B or US$2M+), and the currency must match the card's (EUR 2.1M against a USD card fails). Single digits and "two" to "twenty" are checked too.
- **Banned words.** A card can list them in "Don't rephrase as": `- Banned words: revenue, closed`. Any line citing the card that uses one fails. The example's revenue trap is now caught by the script.
- **Only ✓ means confirmed.** A blank, misspelt or unknown value in the Verified column used to count as confirmed; now only `✓` does.
- **Duplicate Claim IDs fail.** Before, a second card with the same ID silently replaced the first.
- **New `scripts/validate_evidence.py`** checks the evidence bank itself: unique IDs, valid statuses, `protected` true or false, a ✓ or `to verify` on every number, and a filled-in profile.
- **Roles and education are checked.** New `evidence/profile.md` holds your roles (title, company, start, end) and education. Every role heading in Experience and every Education line must match it.
- **Every line counts.** Plain lines in Experience (not just bullets) need a Claim ID, a line indented under a bullet is read as part of that bullet, Projects / Achievements / Highlights sections are checked like Experience, and a line holding a number in any other section needs a Claim ID.
- **Baseline can't be dodged.** If `cv/CV-INDEX.md` already has a starting point for the resume's type and the file isn't in its resume list, it must have `base:`. Removing `base:` no longer switches off the protected-claims check.
- **Protected claims keep their numbers.** A protected claim that stays in the resume but loses the confirmed numbers the baseline gave it now fails.
- **Job-fit scores can't be inflated by leaving the JD out.** In a job-fit report JD coverage (J1) is always scored: with no requirements it counts 0, and switching it off no longer renormalizes the rest to 100. `report_score.py` also prints how many requirements are direct, partial or none, and lists any requirement marked `"gate": true` that isn't directly met.
- Fixed the example card C-001: its two descriptions of who signed the 28 partners disagreed, and its approved wording called a share of leads a share of "pipeline".
- The repo now runs the tests in both languages on every pull request.

**What you need to do**: copy `evidence/profile.md` from the new kit into your `evidence/` folder (an update doesn't touch your evidence) and fill in your roles and education. Then run `python3 scripts/validate_evidence.py` and fix what it reports, usually blank Verified cells. Then rerun `check_claims.py` on your newest resume: numbers that came only from a card's Notes or "Don't rephrase as" will now need a home in the Numbers table.

## 0.2.3 · 2026-11-20

- **Follow-up cards.** Once you're invited to interview, prompt 7 or `/prep` takes the resume version you sent and lists, for each bullet, the questions it's likely to draw, answers that hold up, and what not to say. Every answer comes from your Claim Cards; anything they don't cover goes under "Fill before the interview", never made up. Example: `examples/jordan-lee/interview/ACME-01.md`.
- **A definition of risky.** Big claims, group results claimed as your own, anything likely to be asked for proof, and anything that doesn't match elsewhere get one question before they go on a resume, even after you've said the card is right.
- **Evidence is no longer part of the score.** The score now measures only how the resume reads (R1 to R5, plus J1 to J3 for a job). Before, every first checkup lost 15 points because no Claim Cards existed yet, and a share card showing "Sourced 0%" read like a weak resume. The checkup standard is now v2.
- **New "Interview readiness" panel**, not scored. Before Step 0 it says it unlocks in stage 2 and why it matters: whether you can back each bullet when an interviewer digs in. Once you have cards, it counts the bullets that are confirmed, under review or partial (`"sourced": "partial"`), or still without a card.
- **The share card shows interview readiness too**, dimmed and below the scored rows. Before Step 0 it's locked, with a small "Stage 2 · unlocks after the interview". After a first checkup, the AI also says in two lines what stage 2 unlocks.
- **Reports as images.** New `scripts/report_png.py` saves the share card (or the whole report, with `--full`) as a PNG using the Chrome, Edge or Brave you already have, so you can see the report right in the chat. Before, chat windows and preview panes that don't run JavaScript showed only the watermark; the report file now says so and how to open it.
- Each bullet can list its Claim IDs in a new `claims` field, shown under the bullet in the full report, never on the share card.
- Fixed: `report_share.py` turned every evidence mark into yes or no.
- The example reports now score 38 and 89 (were 34 and 90).
- **Claim Cards record three things separately.** `status` still decides whether a card can go on a resume, and has a new value, `Interview only`: true, but not for a resume (client names, confidential figures). A new `evidence:` field records how well it holds up in an interview. A new Verified column in the Numbers table marks each number `✓` or `to verify`, so one unconfirmed number no longer holds back the whole card.
- **Fitted to how job searches really go.** `evidence:` records how solidly you can talk about something in an interview, not whether you can hand over a contract: `can explain` (the default; most work sits here), `on record` (naming the source is enough), `can be vouched for`, and `vague` (the only one that needs attention). In the interview the AI shows you each card's essentials; say it's right and the card is ready, with no separate review round, and numbers you gave yourself count as confirmed. `Needs review` is only for facts the AI took from old material that you haven't said yourself.
- `check_claims.py` now flags a number marked `to verify` and a card marked `Interview only`.
- **More consistent marking.** Action-led no longer accepts weak verbs such as Helped, Assisted or Supported, which hide which part was yours. The structure check is looser: 2 to 5 bullets for each of the two most recent roles, 1 to 3 for earlier ones. REPORT now has yes/no marking examples for Results, Numbers, Action-led and Specific, so a different AI should mark the same bullet the same way.
- Fixed: the card template defaulted to `Safe to draft`. New cards now start as `Needs review`, as the workflow always said.

**What you need to do**: nothing. Cards without `evidence:` or a Verified column still work exactly as before; add them when you next review a card. Reports you already made keep their old score on the page. `report_score.py` and the before-and-after poster use the new formula for both reports, so a poster still compares like with like. To refresh an old report's page, ask the AI to run the checkup again.

## 0.2.2 · 2026-11-20

- **No more blank first screen.** Open the folder and say anything ("start", "hi"): the AI checks where you are and either welcomes you and asks for your resume, picks up an unfinished Step 0, or shows a short menu.
- Claude Code reads the kit's rules on its own (new `CLAUDE.md`), and has slash commands: `/start`, `/checkup`, `/job`, `/poster`, `/update`.

**What you need to do**: nothing. If you updated with prompt 5, the new files arrive with it.

## 0.2.1 · 2026-11-19

- Share card and poster: more breathing room, band ticks moved outside the score ring, a lighter watermark that no longer sits on the score, and a call to action that wraps cleanly on phones.
- Full report on phones: tighter dimension cards, and the band scale shows only the current band.

**What you need to do**: nothing; reports you make from now on use the new layout.

## 0.2.0 · 2026-11-19

**New**
- **Checkup report.** A scored, visual report on any resume, on its own or against a JD. The AI only marks each bullet; the template does the counting, so the score is the same whichever AI fills it in. See `docs/REPORT.md` and `report/template.html`; `scripts/report_score.py` prints the same score in the chat. One file, two views: the full report, and a share card to screenshot and post, which hides your name, employer and bullets. The AI asks whether you want a shareable version; `scripts/report_share.py` makes a separate copy with every private detail removed, safe to send as a file.
- **Before-and-after poster.** `scripts/report_compare.py` turns two reports into a poster: both scores, every dimension before and after. Cards and posters show only the score by default; you can add a headline, target role, keyword tags or highlights, each drawn from your Claim Cards and never naming an employer. Prompt 6.
- **Shorter Step 0 interview.** The checkup comes first, then a plan: your 3 strongest accomplishments, at most 5 questions each, with a time estimate. Every question has a progress line. Three modes: one at a time, one form per accomplishment, or just talk. "Skip" and "stop" always work. Progress is saved in `evidence/INTAKE.md`.
- **Your own rules have their own file.** `docs/MY-DECISIONS.md` holds your rules (from D-101). `docs/DECISIONS.md` keeps the starter rules and is replaced on update, so updates never overwrite your rules.
- **Updating.** `VERSION`, this changelog, and prompt 5.
- Claim Cards have a "To fill" section for skipped questions.
- Diagrams and the report carry icons and a RESUME-GATE watermark. In the report, the score and every dimension are coloured by band (red, ochre, blue, green), with serif headings and numbers.

**What you need to do**
- If you added or changed rules in `docs/DECISIONS.md`, they need to move to `docs/MY-DECISIONS.md`. Prompt 5 does this for you and shows you what moved.

## 0.1.1 · 2026-11-19

- One-click downloads: one zip per kit, no Git or GitHub account needed.
- Diagrams redrawn; Chinese README opening rewritten.
- The self-review checklist names its sources (Harvard's career-office resume guides) and uses STAR as a self-check.
- Step-by-step Get started, with setup links for each AI tool.

**What you need to do**: nothing.

## 0.1.0 · 2026-11-18

First public release.
