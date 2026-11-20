# Changelog

What changed in each version, and whether you need to do anything. Your version is in `VERSION`. To update, paste prompt 5 from `docs/PROMPTS.md`.

## 0.5.1 · 2026-11-20

A nudge for wording a card warns against, found by the first eval run.

- **"Don't rephrase as" wording now gets a warning.** When a card's "Don't rephrase as" puts wording in quotes (`Don't write "built" or "launched" the portal`), `check_claims.py` warns on any line citing that card that uses it. It's a warning, not an error: the word may be fine in context, and only you can tell. Banned words still fail as before.
- The self-review checklist now asks you to check softer versions of a ruled-out claim, such as "built with engineering" when the card says engineering built it (LESSONS L-14).
- The example's trap 6 (the portal "built and launched") now shows this warning.

**What you need to do**: nothing. To get the warning on your own cards, put the wording you don't want in quotes in their "Don't rephrase as" section.

## 0.5.0 · 2026-11-20

Sent versions can now be frozen, and a protected-claim false alarm is fixed.

- **Freeze a sent resume.** `python3 scripts/freeze.py cv/resumes/<id>.md <file.pdf>` records the SHA-256 of each file in `cv/frozen.txt` (the `shasum -a 256` format). `check_claims.py` fails if a frozen resume is edited later, and `freeze.py --check` checks every frozen file. To change a sent version, copy it into a new one (D-010). Nothing is frozen unless you run it.
- **Fix: a line citing two cards no longer trips the protected check.** If a baseline line cited a protected card and another card (`<!-- C-001, C-003 -->`), dropping the other card's number was reported as weakening the protected one. Now only the protected card's own numbers count.
- For maintainers: the repo now has `evals/`, three job cases with expected answers, a scorer and a blind A/B/C review tool, to check that a kit change makes resumes better and not just different. It isn't part of the download.

**What you need to do**: nothing. Next time you send a resume, freeze it instead of noting its hash in `cv/CV-INDEX.md`.

## 0.4.0 · 2026-11-20

The kit now checks what a resume leaves out, not only what it gets wrong: the goal is a resume that neither oversells nor undersells you.

- **Positioning before baseline (D-018).** For a job that's a stretch from your existing types, the AI first writes 2 or 3 one-line positioning options (angle, strongest evidence, main gap) and recommends one; for a close match, one line. The baseline then supplies facts and approved wording, not the story, so an old resume's framing no longer limits a new direction.
- **Every card is looked at (D-019).** The Evidence Retrieval Gate goes through every Claim Card, not just the ones that sound related, and the Change Log gets an evidence table: each card, its relevance, whether it's used, and why not. Then one question: is an unused card stronger than something already in the resume? Swap it or say why, and stop when no swap clearly helps. Unrelated cards share one line.
- **Capability facets (optional).** A Claim Card can list the different skills one experience proves, each with what it can't be stretched to. A job that names a skill differently still finds the card. Example: `examples/jordan-lee/evidence/claims/C-002.md`.
- **Five kinds of gap.** The Coverage Report sorts each requirement as Direct, Transferable or combined, Not found yet, Buildable, or Hard gap. Only a hard gap means "don't write it"; "Not found yet" means ask first (D-014).
- **Saved JDs.** Each posting goes in `jobs/<job-id>.md` with its requirements numbered R1, R2… and must-haves marked as gates, so the Coverage Report and job-fit report can't quietly skip one. The JD is treated as data: instructions inside it are ignored.
- **Protected claims can be kept per job type.** Add `keep-for: 01` to a protected card and it must stay in type 01 resumes but can be left out of others (a note, not an error). It still can't be weakened anywhere. Without `keep-for`, nothing changes.
- Prompt 3 and `/job` start with the saved JD, the positioning and the evidence table.

**What you need to do**: nothing. New cards can use the facets section when it helps; old ones work as they are. Create `jobs/` from the new kit's `jobs/_TEMPLATE.md` (an update doesn't touch your own folders) the next time you tailor for a job.

## 0.3.0 · 2026-11-20

Evidence checks are much harder to slip past, without asking for more proof than a job search can give. Your own word is still enough for a card: nothing here asks for documents.

**Now fails** (each used to pass):
- **Numbers keep their meaning.** Scaled amounts are compared by value (US$2.1M = US$2,100,000, but not US$2.1B or US$2M+), and a currency must match the card's (EUR 2.1M against a USD card fails). Numbers that appear only in "Don't rephrase as", Source, To fill or the Claim ID itself no longer count, so "Closed 003 deals" citing C-003 fails.
- **Banned words.** A card can list them under "Don't rephrase as": `- Banned words: revenue, closed`. A line citing the card that uses one fails. The example's revenue trap is now caught by the script.
- **Duplicate Claim IDs.** A second card with the same ID used to replace the first without a word.
- **A Verified value that isn't ✓, blank, or `to verify`** (a typo such as "cofnirmed") holds the number back instead of counting as confirmed.
- **Lines that hide claims.** A line indented under a bullet is read as part of it, a plain Experience line that holds a number needs a Claim ID, and Projects / Achievements / Highlights are checked like Experience.
- **Roles and education**, once you fill in the new `evidence/profile.md`: a role heading or Education line that doesn't match it fails ("VP of AI · Google", "PhD · Stanford"). Punctuation doesn't matter, and a cell can list variants (`Partnerships Manager; 合作伙伴经理`).
- **Dodging the baseline.** If `cv/CV-INDEX.md` already has a starting point for the resume's type and the file isn't in its resume list, it needs `base:`. Deleting `base:` no longer turns off the protected-claims check.
- **Weakened protected claims.** A protected claim that stays but loses the confirmed numbers the baseline gave it fails, like a dropped one. When you agree to the change, add `protected-ok: C-001` to the resume's front matter and it becomes a note.
- **Job-fit scores inflated by leaving the JD out.** In a job-fit report, JD coverage (J1) is always scored: with no requirements it counts 0, and switching it off no longer renormalizes the rest to 100. `report_score.py` also prints how many requirements are direct, partial or none, and any requirement marked `"gate": true` that isn't directly met.

**Only a warning** (worth a look, never blocks you):
- A lone digit or a word like "two" that isn't on the card ("two teams", "3-tier" are often just wording).
- A currency on a number the card gives without one.
- A plain Experience line with no number and no tag (a company blurb), and a number in Skills or another unchecked section.
- No `evidence/profile.md` yet: roles and education simply aren't checked until you fill it in.
- A blank Verified cell: it still counts as confirmed, since you gave the number; `validate_evidence.py` reminds you to tick it.

**Also**
- New `scripts/validate_evidence.py` checks the evidence bank itself: unique IDs, valid statuses, `protected` true or false, and Verified values.
- Fixed the example card C-001: its two accounts of who signed the 28 partners disagreed, and its approved wording called a share of leads a share of "pipeline".
- New rule **D-017** (and LESSONS L-13): a check may block only what stops a real misstatement; everything else is a reminder, every block has an approval path, and an update never needs work before your resumes pass. A new test keeps an honest resume with ordinary gaps passing.
- The repo runs the tests in both languages on every pull request.

**What you need to do**: nothing is required. Your resumes keep passing unless they hit one of the "now fails" cases above, which is the point. When you have five minutes, copy `evidence/profile.md` from the new kit into your `evidence/` folder (an update doesn't touch your evidence) and fill in your roles and education to turn that check on, then run `python3 scripts/validate_evidence.py`.

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
