# AGENTS.md: Instructions for AI

Before you do any resume work in this repo, read these in order:

1. `docs/DECISIONS.md`: every decision marked **Active** is binding
2. `docs/WORKFLOW.md`: the seven steps; don't move to the next step until you can state what the current one produced
3. `cv/CV-INDEX.md`: pick the job type and the baseline resume
4. `docs/LESSONS.md`: skim the mistakes made before
5. When actually writing a resume: `evidence/claims/` (the only source of facts) and `docs/REVIEW-CHECKLIST.md` (self-review)

## Hard rules

**Facts**
- Every experience and every number in a resume must trace to a Claim Card in `evidence/claims/`, or to an approved or sent version. If it has no source, leave it out.
- Keep units, currencies, time windows, and qualifiers ("potential", "cumulative", "per project"). Never present a team result as an individual one.
- If the JD asks for something with no evidence behind it, **don't write it**. Put it in the Coverage Report and let the user decide what to do.
- If you're unsure of a fact, mark it "unverified". Don't guess.

**Process**
- Before generating any resume, pass the Evidence Retrieval Gate: read the relevant Claim Cards and **list which ones you read**.
- Start from the latest approved version and make a delta. Never start from a blank page. Record changes in `cv/changelogs/`.
- When you say a check is done, attach a Coverage Report: what you covered and what you didn't.
- Self-review against `docs/REVIEW-CHECKLIST.md` before showing anything to the user.
- **Human review gate**: until the user says "approved", a version stays `Draft`. Don't edit a version marked `Sent`.

**Permissions**
| Level | Examples | Can the AI do it directly? |
|---|---|---|
| L1 read-only | Read a JD, read evidence, analyze fit | Yes |
| L2 reversible internal edits | Write drafts, edit docs in this repo | Yes, and log it in the changelog |
| L3 external or irreversible | Submit an application, contact a recruiter, change a confirmed fact | **Get explicit approval from the user first** |

**Decisions**
- When the user says "from now on" or "let's go with that," **write it into `docs/DECISIONS.md` right then**. Don't leave it in the chat.
- Before numbering a new decision, run `grep "^## D-" docs/DECISIONS.md`, take the highest number, and add 1. This keeps parallel sessions from colliding (see LESSONS L-06).
- To overturn an old decision, change its status to `Superseded by D-xxx`. Don't delete it.

## Handoff

At the end of each session: update `cv/CV-INDEX.md` if there's a new version, finish the matching changelog, and `git commit`. One commit, one change.

## Never commit

National ID numbers, pay stubs, passwords, API keys, or anything personal the user doesn't want public. The evidence bank holds real work history, so this repo should be private. If it must be public, keep `evidence/` and `cv/` in `.gitignore`.
