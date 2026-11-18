# WORKFLOW: Making a resume

> If you can't state what a step produced, don't move on to the next one.

No baseline resume yet? Do [Step 0](#step-0-cold-start) first.

| Step | What to do | Output |
|---|---|---|
| S1 | **Pick the type and baseline.** Read the JD, find the job type in `cv/CV-INDEX.md`, compare "core skill sets," and take that type's current starting point. Choose the byline and contact variant by type | "Type X, starting point = …" |
| S2 | **Evidence Retrieval Gate.** Read the JD, then pick up to 5 of the most relevant cases from `evidence/claims/` and read their Claim Cards and approved wording. **List what you read** | List of Claim IDs read |
| S3 | **Map to the JD.** For each core requirement: direct evidence / transferable evidence only / no evidence. Don't stretch to cover a gap | Three-column mapping table |
| S4 | **Delta.** Copy the baseline file in `cv/resumes/` and change only what needs changing: headline, summary, bullet order, keywords. Don't rewrite approved text | New draft |
| S5 | **Change Log.** For each change, write Before / After / Why. Attach a JD Coverage Report and what you checked | `cv/changelogs/<id>.md` |
| S6 | **AI self-review.** Go through the [REVIEW-CHECKLIST](REVIEW-CHECKLIST.md) item by item. Export the PDF and run `scripts/pdf_fill.swift` | Screenshots, page count, fill rates, table of self-review fixes |
| S7 | **Human review.** Give the user the full text and a diff against the baseline. Only when they say it's approved does the status become `Approved` | The user's approval on record |

After you apply, mark the version `Sent` and **freeze** it. In `cv/CV-INDEX.md`, record which job used it and the SHA-256 of the exported file.

## Step 0: Cold start

Do this once, before your first job. It takes you from "I have an old resume" to "I have an approved baseline."

| Step | What to do | Output |
|---|---|---|
| 0a | **Gather raw material**: your current resume, your LinkedIn text, old performance reviews, anything with facts in it. Put it in `evidence/sources/`. That folder is git-ignored, so it never gets committed | Files in `evidence/sources/` |
| 0b | **List the accomplishments.** Use prompt 1 in [PROMPTS](PROMPTS.md). The AI lists what it finds and flags the vague ones | Numbered list |
| 0c | **Turn each one into a Claim Card.** Use prompt 2: the AI interviews you, then drafts the card as `Needs review`. Start with your 5–10 strongest. Once you've read a card and confirmed it's right, change it to `Safe to draft` | Claim Cards in `evidence/claims/` |
| 0d | **Draft the first baseline** from `Safe to draft` cards only. Copy `cv/resumes/_TEMPLATE.md` and tag every bullet with its Claim ID | `cv/resumes/<id>.md` |
| 0e | **Review and approve** it as in S6 and S7. Add it to `cv/CV-INDEX.md` as the starting point for its type | An Approved baseline |

You're done when `cv/CV-INDEX.md` has at least one Approved starting point. After that, every new job follows S1 to S7.

## Claim statuses

| Status | Meaning | Can the AI use it in a resume? |
|---|---|---|
| `Safe to draft` | You've read the card and confirmed the facts and the limits on wording | Yes |
| `Needs review` | Extracted from your material or an interview, but you haven't confirmed it | No. The AI may only ask you about it |
| `Retired` | Out of date, wrong, or something you no longer want to claim | No |

## Principles

**Facts flow one way.** Source material → Claim Card → approved wording → resume version. A resume inherits wording and structure from the baseline, but never its facts: every line still has to stand on a Claim Card. Otherwise an error in one old resume gets approved, copied, and carried into every version after it.

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
