# Changelog

What changed in each version, and whether you need to do anything. Your version is in `VERSION`. To update, paste prompt 5 from `docs/PROMPTS.md`.

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
