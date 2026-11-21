# DECISIONS: Decision register

> Starter rules that ship with Resume-Gate (D-001 to D-099). **The AI must follow every one with status Active**, unless a rule in [MY-DECISIONS.md](MY-DECISIONS.md) overrides it.
> **Don't edit this file.** It's replaced when you update the kit. Your own rules, and any change to these, go in `docs/MY-DECISIONS.md`.

**scope**: `cv` (resume production) · `process` (how we work together) · `strategy` (job-search direction)

**applies-to**: `all` (the default), `type: 01`, or `job: ACME-01`. A rule that only fits one kind of job or one application shouldn't become a global rule. Only `all` binds every resume.

D-001 to D-020 are starter rules, each born from a real mistake. D-001 to D-010 keep facts from getting lost or inflated; D-020 keeps a corrected fact from coming back; D-011 to D-016, D-018 and D-019 help you dig out what your experience is actually worth, so it doesn't get written too weakly; D-017 keeps the rules themselves from asking more than a real job search can give. To change or switch one off, add a rule in `MY-DECISIONS.md` that says which one it overrides.

---

## D-001 · A new job's version inherits the best-fitting approved version, not a blank page
- scope: cv · status: Active
- Choose by fit (positioning, evidence coverage, approval status, recency), not only by type and date.
- If the type has no baseline, derive one from the closest neighboring type and note it in the Change Log.

## D-002 · Don't cut strong results without a reason
- scope: cv · status: Active
- A cut has to pass three tests (relevance, accuracy, space), and the reason goes in the Change Log.
- A claim marked `protected: true` in its Claim Card can't be dropped or weakened without the user's approval.

## D-003 · Every number has a claim card
- scope: cv · status: Active
- A number must trace to a Claim Card in `evidence/claims/`, with its unit, currency, time window, and qualifiers intact. Rewording must not cross the card's "don't rephrase as" list.
- Approved and sent resumes are approved *wording*, not evidence. A line in an old resume that has no Claim Card is unverified.

## D-004 · Don't write what you can't back up
- scope: cv · status: Active
- Put it under "None" in the Coverage Report and let the user decide what to do.

## D-005 · Pick the byline and contact details by job type
- scope: cv · status: Active
- If you use more than one byline, email, or social handle (for example a legal name and a name you go by), list in the "Bylines" table in `cv/CV-INDEX.md` which kind of job each one is for. Don't mix them.

## D-006 · Evidence Retrieval Gate
- scope: process · status: Active
- Before generating any resume, read the relevant Claim Cards and list the Claim IDs you read.

## D-007 · AI self-reviews before the user sees anything
- scope: process · status: Active
- Go through `docs/REVIEW-CHECKLIST.md` and fix what you find. When you hand off, include page images, page count and reach per page, self-review fixes, highlights, and risks.

## D-008 · Human review gate
- scope: process · status: Active
- Until the user says "approved," a version stays `Draft`. After that it becomes `Approved`. The AI never finalizes on its own.

## D-009 · The PDF fills its pages (default: 1 or 2 full pages)
- scope: cv · status: Active
- By default, 1 or 2 full pages with the content on the last page reaching at least 85% of the page height. Both numbers are defaults: change them here if your field expects something else. Fix content first, then layout settings. Never add unsupported content to fill a page.

## D-010 · Sent versions are frozen
- scope: process · status: Active
- Once a version is `Sent`, don't edit it. To change anything, copy it into a new version. Freeze it with `scripts/freeze.py`, which records the SHA-256 of the resume and the exported file in `cv/frozen.txt`.

## D-011 · Choose evidence by how much it sets you apart, not by keyword overlap with the JD
- scope: cv · status: Active
- An experience that shares words with the JD isn't necessarily the most convincing one. Prefer the thing only you did, the one that best proves the skill, even if it's named differently from the JD.
- A common failure: the AI rewrites an unfamiliar strong experience (say, a regional narrative strategy) into familiar, generic wording (say, relationship management) because the generic version looks more like the JD.

## D-012 · One experience can yield several separate proofs; pick the angle per job
- scope: cv · status: Active
- In one project, diagnosing needs and designing the offer before signing is one skill; delivering after signing is another. For a BD role, lead with the first; for a delivery role, the second. Don't blur them into "managed the full lifecycle."
- Both versions rest on exactly the same facts; only the selection and order differ (see D-003).

## D-013 · Transferable skills come from what you actually did and owned, not from titles or industry labels
- scope: cv · status: Active
- Ask first: what the candidate was actually responsible for, what they decided, who they worked with, and who owns the result. Someone titled "coordinator" may have designed commercial deals; someone titled "lead" may have done only part of the work.
- Keep three kinds of credit apart: running the project, doing the specialist work (for example a design team's output), and owning the outcome. Write only the candidate's share.

## D-014 · Every restricting rule comes with a probing question
- scope: process · status: Active
- Before applying rules like "no evidence, no claim," "a plan isn't a result," or "don't imply causation," ask first, then decide how far the wording can go. An AI that only filters throws away experiences the candidate described incompletely.
- **Plans, proposals, targets, and analysis given in an interview** aren't delivered results. But ask first: "Was any part of this proposal later adopted or carried out?" Often part of it was.
- **How two contributions relate**: ask whether it's direct cause, indirect support, or independent. Write the link you can show (for example "cited as one basis for approving the program"); only a link you can't show stays unwritten.
- The standing questions are in the "Probing questions" section of `docs/WORKFLOW.md`.

## D-015 · Among all the defensible ways to say it, pick the strongest
- scope: cv · status: Active
- Accuracy, strength of positioning, and how a recruiter will read it all have to pass. Vague wording fails (for example lumping two companies together as "ventures"), and so does a string of disclaimers ("part-time, occasional, not involved day to day").
- How to judge: when both versions are accurate, look at where the words go. One spends them explaining what you didn't do; the other spends them proving what you did. Pick the second.

## D-016 · Understand the role from the JD and from what people in that role actually do
- scope: strategy · status: Active
- Look at public career information for people in the same role at the company. Use it to tell which JD requirements are hard gates and which can be met with adjacent experience, then decide the order of your experience and whether to apply.
- Public information only, used to understand the role. Don't build profiles of individuals.

## D-017 · No rule may ask for more than a real job search can give
- scope: process · status: Active
- Most facts rest on your own account and how solidly you can explain them in an interview, not on contracts or documents. Your own word is enough for a card, a number you gave is confirmed, and a blank field you didn't fill is not held against you.
- A rule may **block** (fail a check, refuse to write) only when it stops a real misstatement: a changed amount, scale or currency; a banned phrase; an invented role, employer or degree; a claim with no card; a duplicate ID; a protected claim dropped without approval. Anything that might just be wording, or that's merely incomplete, is a **reminder** at most.
- Every block has a way through once you agree (for a protected claim, `protected-ok: C-xxx`). You never get stuck on an error you've already approved.
- An update never requires work before your resumes keep passing. New checks start as reminders, or only switch on once you've filled in what they need.
- Before adding or tightening a rule, ask: what fabrication does this stop? If there's no answer, it's a reminder, not a block (LESSONS L-13).


## D-018 · Inherit the facts, not the story
- scope: cv · status: Active
- A new version inherits confirmed facts, numbers and their attribution, approved wording, the user's decisions and known mistakes from its baseline. It does not have to inherit the baseline's positioning, which experiences lead, how they're combined, or their order.
- When a job is a stretch from your existing types, the best story may never have appeared in an old resume. Choose the positioning first (S1), then use the baseline as the source of wording. Show the result as a delta, so the user can still see every change.

## D-019 · Check what's missing, not only what's wrong
- scope: cv · status: Active
- A resume can be accurate and still undersell the candidate. In S2, look at every Claim Card and record which ones are used and why the others aren't.
- If an unused card is stronger for this job than something already in the resume, swap it in or say why not. Stop when no swap clearly adds value; don't keep rewriting a version that's already good.
- Keep the record light: unused cards can share one line by reason; a protected card, or one that clearly fits the job, gets its own row. `check_claims.py` warns when a card is missing from the table.

---

## D-020 · Correct a fact once; everything that used it knows
- scope: process · status: Active
- The problem: the user corrected a fact, and later work still used the old version, from an approved resume, a follow-up card, or something said earlier in the chat.
- A correction goes into the Claim Card first, in the same turn. From then on the card wins. The resumes, follow-up cards and answers that cite it are flagged for a recheck by `check_claims.py` and `list_claims.py --health`, worked out fresh from fingerprints in `cv/reviewed.txt`. Nothing is rewritten on its own, and a sent version stays as it was sent.
- Only the lines citing the changed card need a recheck; the rest of the version keeps its approval. A draft gets a reminder; only `--finalize` blocks, and only for a major change or a card nobody has checked, because that's the point where an old fact would reach an employer (D-017).
- A record means the user looked. Never write one to clear a warning.
- Accepted when: after one correction, a fresh session uses the new fact without being told again, keeps the real value of the accomplishment, and doesn't treat a wording request as a correction (evals, `fact-correction`).

