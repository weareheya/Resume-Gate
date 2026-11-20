# WORKFLOW: Making a resume

> If you can't state what a step produced, don't move on to the next one.

No baseline resume yet? Do [Step 0](#step-0-cold-start) first.

| Step | What to do | Output |
|---|---|---|
| S1 | **Pick the type and baseline.** Read the JD, find the job type in `cv/CV-INDEX.md`, compare "core skill sets," and choose the baseline by fit: how close its positioning is to this job, how much of the JD its claims already cover, whether it's Approved, and how recent it is. The type's current starting point is the default, not a rule. Choose the byline and contact variant by type. If useful, look at the public backgrounds of people in the same role at the company to see which requirements are hard gates (D-016) | "Type X, starting point = …" |
| S2 | **Evidence Retrieval Gate.** Read the JD, then search `evidence/claims/` for every case that's relevant, with no cap on how many, and read their Claim Cards and approved wording. Also read every Claim ID the baseline already uses and every claim marked `protected`. **List what you read** | List of Claim IDs read |
| S3 | **Map to the JD.** For each core requirement: direct evidence / transferable evidence only / no evidence. Before marking anything "no evidence," go through the [probing questions](#probing-questions) (D-014). If there's still no evidence, don't stretch to cover the gap | Three-column mapping table |
| S4 | **Delta.** Copy the baseline file in `cv/resumes/` and change only what needs changing: headline, summary, bullet order, keywords. Don't rewrite approved text | New draft |
| S5 | **Change Log.** For each change, write Before / After / Why. Attach a JD Coverage Report and what you checked | `cv/changelogs/<id>.md` |
| S6 | **AI self-review.** Go through the [REVIEW-CHECKLIST](REVIEW-CHECKLIST.md) item by item. Run `python3 scripts/check_claims.py cv/resumes/<id>.md` (it must pass), then export the PDF and run `scripts/pdf_fill.swift` | Screenshots, page count and reach per page, table of self-review fixes |
| S7 | **Human review.** Give the user the full text and a diff against the baseline. Only when they say it's approved does the status become `Approved` | The user's approval on record |

After you apply, mark the version `Sent` and **freeze** it. In `cv/CV-INDEX.md`, record which job used it and the SHA-256 of the exported file.

## Step 0: Cold start

Do this once, before your first job. It takes you from "I have an old resume" to "I have an approved baseline."

| Step | What to do | Output |
|---|---|---|
| 0a | **Gather raw material**: your current resume, your LinkedIn text, old performance reviews, anything with facts in it. Put it in `evidence/sources/`. That folder is git-ignored, so it never gets committed | Files in `evidence/sources/` |
| 0b | **Checkup report.** Use prompt 1 in [PROMPTS](PROMPTS.md). The AI reads the resume, counts what [REPORT](REPORT.md) asks for, and fills `report/template.html`. You get a scored, visual report before any interview: what's strong, what's vague, the five fixes that matter most. Then it asks whether you want a shareable version | `reports/<date>-checkup.html` and its card as a PNG, a three-line summary in the chat, and `-share.html` if you asked for one |
| 0c | **Interview plan.** The AI picks your **3 strongest** accomplishments (enough for a first baseline; the rest can wait), lists only what's still missing for each after reading your material, and writes the plan into `evidence/INTAKE.md`: how many questions, about how long. You pick a mode (see below) | `evidence/INTAKE.md` |
| 0d | **Interview and write cards.** Use prompt 2. Every question starts with a progress line. Skip any question or stop any time: what's unanswered goes on the card as "To fill", not into more questions. After each accomplishment, the AI shows you the card's essentials (the wording it would use, the numbers, what not to say). Say "right" or fix a few things, and the card is `Safe to draft`: no separate review round, unless it's risky (see "What counts as risky") | Claim Cards in `evidence/claims/`, `INTAKE.md` updated |
| 0e | **Draft the first baseline** from `Safe to draft` cards only. Copy `cv/resumes/_TEMPLATE.md` and tag every bullet with its Claim ID | `cv/resumes/<id>.md` |
| 0f | **Review and approve** it as in S6 and S7. Add it to `cv/CV-INDEX.md` as the starting point for its type. Then the AI offers to rerun the checkup and make a before-and-after poster (prompt 6) | An Approved baseline; a poster if you want one |

You're done when `cv/CV-INDEX.md` has at least one Approved starting point. After that, every new job follows S1 to S7. Add more cards whenever you like with prompt 2, and rerun the checkup (prompt 1) to see the score move.

### Keeping the interview short

The interview is the slowest part of Step 0, so the AI keeps it small and always says where you are.

- **Don't ask what the material already answers.** If the old resume says "grew partners from 12 to 40", confirm it in one yes/no question instead of asking for it again.
- **At most 5 questions per accomplishment.** What's still open after that goes on the card as "To fill".
- **Three modes; the user picks one in 0c:**
  - *One at a time*: one question, one answer. Slowest, easiest.
  - *One form per accomplishment*: all of its questions in one message, answered in one reply.
  - *Just talk*: the user describes it freely in one long message; the AI pulls out the facts and asks only what's left.
- **A progress line before every question**, in this format:

  `▓▓▓▓▓▓░░░░░░░░░ 6/15 · accomplishment 2/3 · question 1/5`

- **"Skip" and "stop" always work.** On "stop", save `evidence/INTAKE.md` and say where the next session picks up.

## After you get an interview: follow-up cards

Every bullet on a resume can draw a follow-up: "How was that counted?", "Which part was yours?", "Was all of that down to you?" The answers are already on the Claim Cards: the basis, the attribution, the claims you can't make, the source. A follow-up card puts them in the order an interview will ask for them.

- **When**: once you're invited to interview, for the resume version you sent. Use prompt 7, or `/prep`.
- **Output**: `interview/<job ID>.md`, in the format of [`interview/_TEMPLATE.md`](../interview/_TEMPLATE.md). Example: [`examples/jordan-lee/interview/ACME-01.md`](../examples/jordan-lee/interview/ACME-01.md).

**The questions come from the cards, not from guessing:**

| On the card | Becomes |
|---|---|
| Numbers and what they mean | "How was that counted? Over what period? Out of how many?" |
| Attribution | "Which part was yours? How big was the team?" |
| Causal claims you can't make | "Was all that growth down to you?": draw the line honestly |
| Don't rephrase as | The interviewer rounds it up: "So you brought in $2M in revenue?": correct it on the spot; far better than a reference check finding it |
| Source | "Do you have data on that?": naming the source is enough, no need to produce it |
| Notes | Interview points already written on the card |
| Partial or None in the Coverage Report | Skills the JD wants that the evidence only partly covers: how to answer honestly with adjacent experience |

**Rules:**
- Answers use only facts on the cards. Anything likely to come up that the cards don't cover goes under "Fill before the interview", as a question for the user; never make it up.
- At most 3 follow-ups per bullet, the most likely ones. Same order as the resume, strongest first.
- Risks go at the top: `vague`, `Needs review`, `to verify`, and anything that hits "What counts as risky".
- `Interview only` cards go under "Worth bringing up": not on the resume, but a plus to mention in the room.

## Claim statuses

| Status | Meaning | Can the AI use it in a resume? |
|---|---|---|
| `Safe to draft` | You've read the card and confirmed the facts and the limits on wording | Yes |
| `Needs review` | Not confirmed yet, or risky (see "What counts as risky" below) | No. The AI may only ask you about it |
| `Interview only` | True, but not for a resume: client names, confidential figures, details you'd only say in person | No. Fine for interview prep |
| `Retired` | Out of date, wrong, or something you no longer want to claim | No |

The status answers one question: can this go on a resume? Two other things are recorded separately:

- **Whether each number is confirmed**: the Verified column in the card's Numbers table. A number you gave in the interview is `✓` straight away. Only a number you called rough, or one the AI took from old material without asking you, is `to verify`, and those can't go on a resume.
- **How well it holds up in an interview**: the card's `evidence:` field. Most work leaves no contract or report you can hand over; in an interview what counts is how solidly you can talk about it. So the default, `can explain`, is enough. Only `vague` needs attention: fill in the details before an interview, or word the bullet more carefully.

| `evidence:` | Means |
|---|---|
| `can explain` | You can walk through how it happened, how each number was counted, and which part was yours. Most work sits here, and it's enough for an interview |
| `on record` | There are also documents, reports or emails. You don't need to hand them over; naming the source is enough |
| `can be vouched for` | A former manager, client or partner, or public coverage, could confirm it |
| `vague` | You remember the outline but not the details or numbers. Easy to get stuck on in an interview |

`Needs review` is for what isn't really confirmed yet, or is risky; see the next section.

### What counts as risky

When the user says a card is right in the interview, it's ready, unless it hits any of the cases below. Then it stays `Needs review` for now:

| Risk | Example |
|---|---|
| **Not in the user's own words** | The AI took it from an old resume, LinkedIn or a document, and the user hasn't said it in the interview |
| **The user isn't sure** | "roughly", "I think", "something like" |
| **A big claim** | Large sums; "first", "only", "#1"; growth by multiples; scope well beyond what the role would normally own |
| **A group result claimed as your own** | Company funding, team revenue or market growth written as if the user caused it |
| **Likely to be asked for proof** | Specific amounts and client names; numbers anyone can look up (funding, user counts, rankings); awards; promotions; anything a reference check could confirm |
| **Doesn't match elsewhere** | An old resume, LinkedIn or another card gives a different number or title |

**What happens next:** this isn't saying the user is exaggerating, only that these are the lines an interviewer is most likely to probe. The AI names the case and asks one question: how was this counted? What's it based on? Which part was yours? If the user can explain it, the basis goes on the card and it becomes `Safe to draft`. If not, pick a more careful wording that holds up (D-015), or leave it `Needs review` for now.

## Principles

**Facts flow one way.** Source material → Claim Card → approved wording → resume version. A resume inherits wording and structure from the baseline, but never its facts: every line still has to stand on a Claim Card. Otherwise an error in one old resume gets approved, copied, and carried into every version after it.

**Baseline plus delta, never a blank page.** A new job inherits the best-fitting approved version, usually the latest one of its type. That way confirmed facts and settled structure don't get lost. If the type has no baseline, derive one from the closest neighboring type and say so in the Change Log.

**The Evidence Gate has to be checkable.** "I read the evidence bank" doesn't count. List the specific Claim IDs. If you can't, you didn't read them.

**Dig before you filter.** Rules like "no evidence, no claim" and "a plan isn't a result" apply only after you've asked. Candidates often describe what they did in very few words: an "unlaunched proposal" may have had a part that was adopted, and a "coordinator" may have designed commercial deals. Use the probing questions to dig out the value first, then decide how far the wording can go (D-014).

**No evidence, no claim.** If the JD wants something the evidence bank doesn't cover, put it under "None" in the Coverage Report. The user decides whether to build the evidence, cover it in the interview, or skip the job.

**Don't cut strong results without a reason.** Removing an existing strong bullet has to pass three tests: relevance (it doesn't help for this job), accuracy (there's doubt about it), or space (it doesn't fit). Write the reason in the Change Log. A claim marked `protected: true` can't be dropped or weakened at all without the user's approval.

**Layout follows content, not the other way around.** If the page count is off, edit the content first (cut weak bullets, tighten long sentences). Only then touch font size, line spacing, or margins. Never add unsupported content to fill a page.

## Probing questions

Before writing a Claim Card, mapping to a JD, or marking anything "no evidence," ask at least these:

1. Would this have happened if you hadn't done it? Which part was yours, and which part was the team's?
2. Beyond your title, what were you actually responsible for?
3. Which decisions involving money were you part of: budgets, pricing, contracts, sponsorships?
4. Was any part of this proposal or plan later adopted or carried out?
5. Are these two things related? Did one directly cause the other, support it indirectly, or are they independent?
6. What does this number measure: unit, time window, cumulative or per item, actual or potential?
7. Is there wording you've corrected before? (Weakened wording you've already fixed is the most likely to come back.)

## Coverage Report format

```markdown
| JD requirement | Covered | Notes | How to close the gap |
|---|---|---|---|
| Requirement A | Yes | Claim C-003 | n/a |
| Requirement B | Partly | Transferable: C-007 (different setting) | Lead with the transferable skill; be ready to say how the setting differs |
| Requirement C | None | No evidence, so left out | Build the evidence, answer it in the interview, or skip the job |

**Scope of check**: covered …; not covered … (reason)
```

## When a new type is warranted

Open a new type in `CV-INDEX` only if all three are true. Otherwise treat it as a job-specific version of an existing type.

1. The headline and summary need a full rewrite, not just new keywords.
2. More than half of the experience bullets change priority.
3. You expect to apply to 3 or more jobs of this kind.
