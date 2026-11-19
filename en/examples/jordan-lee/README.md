# Jordan Lee: a full worked example

A small, made-up job search laid out exactly like your own project. Jordan Lee, Northwind Labs, Acme Cloud and every number are invented. Don't copy anything from here into your own resume.

| Path | What it shows |
|---|---|
| [evidence/claims/](evidence/claims/) | Five Claim Cards. C-001 is `protected: true`. C-005 is `Needs review`, so it can't be used yet |
| [cv/resumes/channel-baseline.md](cv/resumes/channel-baseline.md) | The first approved baseline, built in Step 0 |
| [cv/resumes/acme-pdm.md](cv/resumes/acme-pdm.md) | A new version for one job, started from the baseline |
| [cv/changelogs/ACME-01.md](cv/changelogs/ACME-01.md) | Its Change Log: what was read, Delta, Coverage Report, self-review |
| [cv/CV-INDEX.md](cv/CV-INDEX.md) | The index after that version |
| [cv/resumes/acme-pdm-with-traps.md](cv/resumes/acme-pdm-with-traps.md) | The same version with seven deliberate mistakes |
| [reports/](reports/) | Checkup reports before Step 0 (34) and for the new version (90). Try `python3 ../../scripts/report_compare.py reports/2026-05-02-checkup.html reports/2026-05-10-checkup.html` from this folder |

## Run the check yourself

From the kit's root folder (on Windows, use `python` instead of `python3`):

```bash
cd examples/jordan-lee
python3 ../../scripts/check_claims.py cv/resumes/acme-pdm.md
python3 ../../scripts/check_claims.py cv/resumes/acme-pdm-with-traps.md
```

**`acme-pdm.md` passes** (exit code 0):

```text
WARN  acme-pdm.md: section "Skills" has 1 line(s) this script does not verify
NOTE  C-002 is used in the baseline (channel-baseline.md) but not here
OK: 5 lines checked, 3 Claim IDs used, no errors
```

The NOTE is expected: C-002 isn't protected, and the Change Log says why it was dropped.

**`acme-pdm-with-traps.md` fails** (exit code 1) with five errors:

```text
ERROR acme-pdm-with-traps.md:17: no Claim ID on this line: Partner development leader with a track record of buildin...
ERROR acme-pdm-with-traps.md:18: C-005 has status "Needs review"; only "Safe to draft" can be used
ERROR acme-pdm-with-traps.md:26: the number "420" doesn't appear in C-004. ...
ERROR acme-pdm-with-traps.md:27: C-009 does not match any Claim Card
ERROR Protected claim C-001 is used in the baseline (channel-baseline.md) but missing from Summary/Experience here. ...
FAILED: 5 error(s) in acme-pdm-with-traps.md
```

## The seven traps

| # | Line | Mistake | Caught by |
|---|---|---|---|
| 1 | Summary, line 1 | A claim with no source | Script |
| 2 | Summary, line 2 | Uses C-005, which is still `Needs review` | Script |
| 3 | Webinars bullet | 420 registrants; the card says 380 | Script |
| 4 | Co-selling bullet | Cites C-009, which doesn't exist | Script |
| 5 | Whole file | Protected C-001 (12 → 40 partners) was dropped | Script |
| 6 | Portal bullet | "Built and launched" the portal. C-002 says engineering built it; Jordan wrote the requirements | **You.** The ID and the number are both valid |
| 7 | Revenue bullet | "Generated US$2.1M in partner revenue". C-003 says it's pipeline, not revenue | **You.** The number is on the card, so the script passes it |

Traps 6 and 7 are the point: the script checks that every line has a source and that its numbers match. It can't tell whether the wording stays inside the card's "Don't rephrase as" limits. That's what the self-review checklist and your own read are for.
