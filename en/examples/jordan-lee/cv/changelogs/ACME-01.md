---
job_id: ACME-01
role: Acme Cloud · Partner Development Manager (fictional)
status: Approved
base: channel-baseline
date: 2026-05-10
---

# Acme Cloud · Partner Development Manager · CV Change Log

New version: `cv/resumes/acme-pdm.md`. JD: `jobs/ACME-01.md`

## Positioning

Close match to type 01 (channel & partnerships), so one line: a partner developer who builds the program and then gets partners selling. Baseline `channel-baseline` for facts and wording.

## Evidence table (every card)

| Card | Relevance to this job | Used? | Where, or why not |
|---|---|---|---|
| C-001 · Channel partner growth and tiering (protected) | High | Yes | Summary and bullet 1; "don't rephrase as" limits |
| C-002 · Self-serve partner portal | Medium | No | Partner enablement, but the JD doesn't ask for tooling and the page is full |
| C-003 · Partner-sourced pipeline US$2.1M | High | Yes | Moved into the Summary; kept as pipeline, not revenue |
| C-004 · Joint webinars | High | Yes | Moved up; closest evidence for joint go-to-market |
| C-005 · Partner summit talk | Medium | No | Status is Needs review |

**Unused but strong?** C-002 could show enablement, but C-004 is closer to R2 (co-selling) and space is tight. Asked the user (below).

## Delta (against the baseline)

| Location | Change (Before → After) | Basis |
|---|---|---|
| Summary, line 1 | "Partnerships manager who builds partner programs…" → "Partner development manager who recruits and tiers partners, then gets them selling…" | Matches the JD's wording; same facts (C-001) |
| Summary, line 2 | Added the US$2.1M partner-sourced pipeline | C-003 |
| Northwind, bullet 2 (portal) | Removed | The JD doesn't ask for partner tooling; keeps the page to one. C-002 isn't protected |
| Northwind, webinars | Moved from 4th to 2nd | JD asks for co-selling; closest evidence is co-marketing |
| Skills | Added `partner recruitment`, `co-marketing` | C-001, C-004 |

## JD Coverage Report

| # | JD requirement | Gate | Kind | Evidence | Next step |
|---|---|---|---|---|---|
| R1 | Partner recruitment and tiering | yes | Direct | C-001 | n/a |
| R2 | Co-selling with partners | | Transferable or combined | C-004 (co-marketing) + C-003 (deal registration) | Written as co-marketing, not co-selling. Prepare an interview story about joint account planning |
| R3 | Cloud marketplace experience | | Buildable | n/a | Left out. A short marketplace listing course would close part of it; mention willingness to learn, don't imply experience |

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
