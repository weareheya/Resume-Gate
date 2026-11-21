---
job_id: 
resume:          # id of the resume this log is for; check_claims.py uses it to find the evidence table
role: 
status: Draft   # Draft | Approved | Sent | Unused
base: (baseline resume name / version)
date: YYYY-MM-DD
---

# <Role> · CV Change Log

JD: `jobs/<job-id>.md`

## Positioning

(One line for a close match. For a stretch: 2 or 3 options with their angle, strongest evidence and main gap, and which one was chosen and why.)

## Evidence table (every card)

| Card | Relevance to this job | Used? | Where, or why not |
|---|---|---|---|
| C-0xx | High / Medium / Low | Yes / No | |
| Low: C-0xx, C-0yy | Low | No | Unrelated to this job (one line for all of them) |

Every card appears once: used cards on their own row, unused ones grouped by reason. A protected card, or one that clearly fits the job, gets its own row even when unused. `check_claims.py` warns if a card is missing.

**Unused but strong?** (Any card that would beat something already in the resume, and what was decided.)

## Delta (against the baseline)

| # | Location | Change (Before → After) | Basis | Status |
|---|---|---|---|---|
| 1 | Headline | | | Pending |
| 2 | Summary | | | Pending |
| 3 | Role A | | | Pending |

Each row is one proposal the user can accept or reject on its own ("accept 1 and 3, reject 2"). Status is Pending, Accepted or Rejected. Put the exact old and new text in quotes ("…" → "…") so `check_claims.py` can find it, and the Claim IDs it rests on under Basis. It warns when a rejected change is still in the resume, when an Approved version still has a Pending row, and when a Pending row is **stale**: its quoted Before text is gone from the baseline, or a card it cites had a major change after the Change Log was recorded. Re-propose a stale row instead of applying it. Each row is recorded on its own once the user has looked at it (`check_claims.py cv/changelogs/<id>.md --record P2`, or `--record all`); a row that was never recorded, or was edited after, isn't treated as valid.

## JD Coverage Report

| # | JD requirement | Gate | Kind | Evidence | Next step |
|---|---|---|---|---|---|
| R1 | | | Direct / Transferable or combined / Not found yet / Buildable / Hard gap | | |

**Main gaps**:

## Scope of check

- Covered:
- Not covered:

## AI self-review

| Finding | Fix |
|---|---|
| | |

Layout (at Finalize): pages , reach per page , or "the user checked the PDF" on a computer without `pdf_fill` (result from your resume tool's checker)

## Open questions for the user

1. 

## Review outcome

(Date, and whether the user approved. Once approved, set the status to Approved; this version becomes the baseline for later jobs of the same type.)
