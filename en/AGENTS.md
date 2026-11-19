# AGENTS.md: Instructions for AI

Before you do any resume work in this repo, read these in order:

1. `docs/DECISIONS.md` (starter rules) and `docs/MY-DECISIONS.md` (the user's own rules): every decision marked **Active** is binding. Where they conflict, MY-DECISIONS wins
2. `docs/WORKFLOW.md`: the seven steps; don't move to the next step until you can state what the current one produced
3. `cv/CV-INDEX.md`: pick the job type and the baseline resume
4. `docs/LESSONS.md`: skim the mistakes made before
5. When actually writing a resume: `evidence/claims/` (the only source of facts) and `docs/REVIEW-CHECKLIST.md` (self-review)

## Hard rules

**Facts**
- Use only claims marked `Safe to draft`. A `Needs review` claim is something to ask the user about, never something to write.
- Tag every resume bullet with its Claim ID in an HTML comment (`<!-- C-001 -->`). A bullet with no tag has no source, so treat it as a bug.
- Every experience and every number in a resume must trace to a Claim Card in `evidence/claims/`, and through the card to its source. If it has no source, leave it out.
- An approved or sent resume is **not evidence**. It only records which wording and structure the user approved. If a bullet in an old resume has no Claim Card behind it, treat it as unverified: don't copy it forward. Write the missing card and get it confirmed first.
- Keep units, currencies, time windows, and qualifiers ("potential", "cumulative", "per project"). Never present a team result as an individual one.
- If the JD asks for something with no evidence behind it, **don't write it**. Put it in the Coverage Report and let the user decide what to do. But before marking anything "no evidence," ask the user the probing questions in `docs/WORKFLOW.md` (D-014).
- Among the defensible ways to say something, pick the strongest: never inflated, never written like a disclaimer (D-015).
- If you're unsure of a fact, mark it "unverified". Don't guess.

**Process**
- If `cv/CV-INDEX.md` has no Approved starting point yet, do Step 0 in `docs/WORKFLOW.md` before anything else.
- Before generating any resume, pass the Evidence Retrieval Gate: read the relevant Claim Cards and **list which ones you read**.
- Start from the best-fitting approved version and make a delta. Never start from a blank page. Record changes in `cv/changelogs/`.
- Never drop or weaken a claim marked `protected: true` without the user's approval. If a new version leaves one out, say so and explain why.
- When you say a check is done, attach a Coverage Report: what you covered and what you didn't.
- Self-review against `docs/REVIEW-CHECKLIST.md` before showing anything to the user.
- Before showing a resume to the user, run `python3 scripts/check_claims.py cv/resumes/<id>.md`, fix every error, and report its result.
- **Human review gate**: until the user says "approved", a version stays `Draft`. Don't edit a version marked `Sent`.

**Permissions**
| Level | Examples | Can the AI do it directly? |
|---|---|---|
| L1 read-only | Read a JD, read evidence, analyze fit | Yes |
| L2 reversible internal edits | Write drafts, edit docs in this repo | Yes, and log it in the changelog |
| L3 external or irreversible | Submit an application, contact a recruiter, change a confirmed fact | **Get explicit approval from the user first** |

**Decisions**
- When the user says "from now on" or "let's go with that," **write it into `docs/MY-DECISIONS.md` right then**. Don't leave it in the chat, and never edit `docs/DECISIONS.md`: it's replaced on every update.
- Number the user's rules from D-101. Before numbering, run `grep "^## D-" docs/MY-DECISIONS.md`, take the highest number, and add 1. This keeps parallel sessions from colliding (see LESSONS L-06).
- To change a starter rule, add a rule in MY-DECISIONS with `overrides: D-0xx`. To overturn one of the user's rules, change its status to `Superseded by D-xxx`. Don't delete it.

## Updating the kit

When the user asks to check for updates (prompt 5 in `docs/PROMPTS.md`):

1. Read `VERSION`. Get the latest kit: https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-en.zip. It's a public download: no GitHub account or connector is needed. If your tool needs approval to use the network, ask once; or ask the user to download and unzip it into this folder.
2. If its `VERSION` isn't newer, say so and stop. If it is, show the user the `CHANGELOG.md` entries since their version, including any "What you need to do" notes.
3. With the user's go-ahead, replace **only kit files**: `AGENTS.md`, `README.md`, `LICENSE`, `VERSION`, `CHANGELOG.md`, `.gitignore`, everything in `docs/` except `MY-DECISIONS.md`, `scripts/`, `report/`, `examples/`, `assets/`, and the three `_TEMPLATE.md` files.
4. **Never touch the user's files**: `docs/MY-DECISIONS.md`, `evidence/` (apart from its `_TEMPLATE.md`), `cv/` (apart from the `_TEMPLATE.md` files), `reports/`.
5. If the user had edited a kit file (for example added rules to `docs/DECISIONS.md` before MY-DECISIONS existed), move their changes into `docs/MY-DECISIONS.md` first and show them what moved.
6. Run `python3 scripts/check_claims.py` on the newest resume to confirm nothing broke, then commit only after the user approves.

## Handoff

At the end of each session: update `cv/CV-INDEX.md` if there's a new version, finish the matching changelog, and `git commit` if any tracked files changed. One commit, one change.

## Never commit

National ID numbers, pay stubs, passwords, API keys, or anything personal the user doesn't want public. The evidence bank holds real work history, so this repo should be private. If it must be public, keep `evidence/` and `cv/` in `.gitignore`.
