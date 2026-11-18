---
job_id: ACME-01
role: Acme Cloud · Partner Development Manager (fictional)
status: Approved
base: channel-baseline
date: 2026-05-10
---

# Acme Cloud · Partner Development Manager · CV Change Log

New version: `cv/resumes/acme-pdm.md`. JD source: (fictional; not included)

## Evidence Retrieval Gate · What was read

| Source | Used for |
|---|---|
| C-001 · Channel partner growth and tiering (protected) | Summary and bullet 1; "don't rephrase as" limits |
| C-002 · Self-serve partner portal | Read; dropped from this version (see Delta) |
| C-003 · Partner-sourced pipeline US$2.1M | Moved into the Summary; kept as pipeline, not revenue |
| C-004 · Joint webinars | Moved up; adjacent evidence for co-selling |
| C-005 · Partner summit talk | Not used: status is Needs review |
| DECISIONS D-001 to D-004 | Inherit the baseline, keep strong results, claim cards, no evidence no claim |

## Delta (against the baseline)

| Location | Change (Before → After) | Basis |
|---|---|---|
| Summary, line 1 | "Partnerships manager who builds partner programs…" → "Partner development manager who recruits and tiers partners, then gets them selling…" | Matches the JD's wording; same facts (C-001) |
| Summary, line 2 | Added the US$2.1M partner-sourced pipeline | C-003 |
| Northwind, bullet 2 (portal) | Removed | The JD doesn't ask for partner tooling; keeps the page to one. C-002 isn't protected |
| Northwind, webinars | Moved from 4th to 2nd | JD asks for co-selling; closest evidence is co-marketing |
| Skills | Added `partner recruitment`, `co-marketing` | C-001, C-004 |

## JD Coverage Report

| JD requirement | Covered | Notes / How to close the gap |
|---|---|---|
| Partner recruitment and tiering | Direct | C-001 |
| Co-selling with partners | Partial | C-004 is co-marketing, not co-selling. Written as co-marketing. Prepare an interview story about joint account planning |
| Cloud marketplace experience | None | No evidence, so left out. Mention willingness to learn; don't imply experience |

**Main gap**: no direct co-selling or marketplace results.

## Scope of check

- Covered: the full baseline, C-001 to C-005, the JD requirements above.
- Not covered: the real page count inside the resume tool (see layout below); C-005's source (still missing).

## AI self-review

| Finding | Fix |
|---|---|
| First draft wrote "generated US$2.1M in revenue" | Back to C-003's wording: partner-sourced pipeline |
| Summary ran 4 lines | Cut to 2 |
| `check_claims.py` gave a NOTE: C-002 dropped from the baseline | Expected; explained in Delta. C-002 isn't protected |

Script result: `OK: 5 lines checked, 3 Claim IDs used, no errors` (plus the NOTE above).
Layout: 1 page, content reaches 93% down the page.

## Open questions for the user

1. Is it fine to leave the portal (C-002) out for this job?

## Review outcome

Approved by the user on 2026-05-10; status set to Approved.
