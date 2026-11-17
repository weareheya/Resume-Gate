# DECISIONS: Decision register

> Rules the user has confirmed. **The AI must follow every one with status Active.** To overturn one, change its status to `Superseded by D-xxx`. Don't delete it.
> Before adding one, run `grep "^## D-" docs/DECISIONS.md`, take the highest number, and add 1.

**scope**: `cv` (resume production) · `process` (how we work together) · `strategy` (job-search direction)

D-001 to D-010 are starter rules, each born from a real mistake. Add, remove, or change them to fit you.

---

## D-001 · A new job's version inherits the latest approved version, not a blank page
- scope: cv · status: Active
- If the type has no baseline, derive one from the closest neighboring type and note it in the Change Log.

## D-002 · Don't cut strong results without a reason
- scope: cv · status: Active
- A cut has to pass three tests (relevance, accuracy, space), and the reason goes in the Change Log.

## D-003 · Every number has a claim card
- scope: cv · status: Active
- A number must trace to a Claim Card in `evidence/claims/`, with its unit, currency, time window, and qualifiers intact. Rewording must not cross the card's "don't rephrase as" list.

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
- Go through `docs/REVIEW-CHECKLIST.md` and fix what you find. When you hand off, include page images, fill rates, self-review fixes, highlights, and risks.

## D-008 · Human review gate
- scope: process · status: Active
- Until the user says "approved," a version stays `Draft`. After that it becomes `Approved`. The AI never finalizes on its own.

## D-009 · The PDF is exactly 1 full page or 2 full pages
- scope: cv · status: Active
- The last page is at least 85% full. Fix content first, then layout settings. Never add unsupported content to fill a page.

## D-010 · Sent versions are frozen
- scope: process · status: Active
- Once a version is `Sent`, don't edit it. To change anything, copy it into a new version. Record the SHA-256 of the exported file in `CV-INDEX`.

---

<!-- Template for a new decision:
## D-0xx · One-line title
- scope: cv|process|strategy · status: Active · date: YYYY-MM-DD
- The rule, where it applies, and any exceptions.
-->
