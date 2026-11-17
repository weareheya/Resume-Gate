# WORKFLOW: Making a resume

> If you can't state what a step produced, don't move on to the next one.

| Step | What to do | Output |
|---|---|---|
| S1 | **Pick the type and baseline.** Read the JD, find the job type in `cv/CV-INDEX.md`, compare "core skill sets," and take that type's current starting point. Choose the byline and contact variant by type | "Type X, starting point = …" |
| S2 | **Evidence Retrieval Gate.** Read the JD, then pick up to 5 of the most relevant cases from `evidence/claims/` and read their Claim Cards and approved wording. **List what you read** | List of Claim IDs read |
| S3 | **Map to the JD.** For each core requirement: direct evidence / transferable evidence only / no evidence. Don't stretch to cover a gap | Three-column mapping table |
| S4 | **Delta.** Copy the baseline and change only what needs changing: headline, summary, bullet order, keywords. Don't rewrite approved text | New draft |
| S5 | **Change Log.** For each change, write Before / After / Why. Attach a JD Coverage Report and what you checked | `cv/changelogs/<id>.md` |
| S6 | **AI self-review.** Go through the [REVIEW-CHECKLIST](REVIEW-CHECKLIST.md) item by item. Export the PDF and run `scripts/pdf_fill.swift` | Screenshots, page count, fill rates, table of self-review fixes |
| S7 | **Human review.** Give the user the full text and a diff against the baseline. Only when they say it's approved does the status become `Approved` | The user's approval on record |

After you apply, mark the version `Sent` and **freeze** it. In `cv/CV-INDEX.md`, record which job used it and the SHA-256 of the exported file.

## Principles

**Baseline plus delta, never a blank page.** A new job inherits the latest approved version of its type. That way confirmed facts and settled structure don't get lost. If the type has no baseline, derive one from the closest neighboring type and say so in the Change Log.

**The Evidence Gate has to be checkable.** "I read the evidence bank" doesn't count. List the specific Claim IDs. If you can't, you didn't read them.

**No evidence, no claim.** If the JD wants something the evidence bank doesn't cover, put it under "None" in the Coverage Report. The user decides whether to build the evidence, cover it in the interview, or skip the job.

**Don't cut strong results without a reason.** Removing an existing strong bullet has to pass three tests: relevance (it doesn't help for this job), accuracy (there's doubt about it), or space (it doesn't fit). Write the reason in the Change Log.

**Layout follows content, not the other way around.** If the page count is off, edit the content first (cut weak bullets, tighten long sentences). Only then touch font size, line spacing, or margins. Never add unsupported content to fill a page.

## Coverage Report format

```markdown
| JD requirement | Covered | Notes |
|---|---|---|
| Requirement A | Yes | Claim C-003 |
| Requirement B | Partly | Transferable: C-007 (different setting) |
| Requirement C | None | No evidence, so left out. Suggestion: … |

**Scope of check**: covered …; not covered … (reason)
```

## When a new type is warranted

Open a new type in `CV-INDEX` only if all three are true. Otherwise treat it as a job-specific version of an existing type.

1. The headline and summary need a full rewrite, not just new keywords.
2. More than half of the experience bullets change priority.
3. You expect to apply to 3 or more jobs of this kind.
