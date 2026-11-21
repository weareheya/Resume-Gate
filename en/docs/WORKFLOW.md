# WORKFLOW: Making a resume

> If you can't state what a step produced, don't move on to the next one.

No baseline resume yet? Do [Step 0](#step-0-cold-start) first.

## Task modes

Not every request needs all seven steps. Pick the mode by what the user asked for; if you're not sure, it's **Tailor**.

| Mode | When | Steps | What you show the user |
|---|---|---|---|
| **Quick edit** | A few lines of an existing version change and there's **no new JD**: a reworded bullet, a typo, a shorter summary, contact details | Read the cards the changed lines cite. Edit in place in a Draft (a Sent version is frozen: copy it first, D-010). Run `check_claims.py` on it. Note the change in its Change Log | The changed lines before and after, and the check result. Problems only: no full Coverage Report |
| **Tailor** | A new JD, a new direction, or more than a few lines | S0 to S7 below | Everything S7 asks for |
| **Finalize** | The user is about to send a version | Run `check_claims.py cv/resumes/<id>.md --finalize`, export the file, check the layout (below), freeze it | Page images or the user's word on the layout, and the freeze result |

A quick edit that turns out to touch a claim's meaning, a protected claim, or what the version is aimed at becomes a Tailor.

**Finalize: layout check.** Export the PDF or DOCX. On macOS, run `swift scripts/pdf_fill.swift <file.pdf> <dir>` and look at the page images it writes. On any other computer, look at the PDF yourself if your tool can open it, **and** ask the user: "Please open the PDF: is it the expected number of pages, and does the last page have more than a few stray lines?" The layout step is done only once the user says it's fine. `check_claims.py --finalize` must pass too: it fails while a card the version cites has an unresolved major change, or hasn't been checked against the current cards (see [When a fact changes](#when-a-fact-changes)). Then freeze: `python3 scripts/freeze.py cv/resumes/<id>.md <exported file>`.

| Step | What to do | Output |
|---|---|---|
| S0 | **Save the JD.** Paste the posting into `jobs/<job-id>.md` (copy `jobs/_TEMPLATE.md`): the original text, where and when you found it, and its core requirements numbered R1, R2… Mark the must-haves as gates. Everything after this refers to those numbers, so nothing the JD asks for can quietly drop out. Tick each step in the file's "Progress" section as you finish it | `jobs/<job-id>.md` |
| S1 | **Positioning, then baseline.** Ask what the job is really for: the business goal behind it, which requirements are hard gates (D-016), and what an ideal hire looks like. If the job is a stretch from your existing types, write 2 or 3 one-line positioning options (the angle, its strongest evidence, its main gap) and recommend one, then stop and let the user choose before S2. For a close match, one line is enough and you carry on. Then pick the baseline by fit: how close its positioning is to the chosen one, how much of the JD its claims already cover, whether it's Approved, and how recent it is. The baseline gives you facts and approved wording, not the story: the chosen positioning can reorder or reframe it (D-018). Choose the byline and contact variant by type | "Positioning: …; type X, starting point = …" |
| S2 | **Evidence Retrieval Gate.** Go through **every** Claim Card, not only the ones that sound related: a title alone can hide a skill the JD wants (check its capability facets, if it has them). With more than 15 cards, start from `python3 scripts/list_claims.py` (one line per card) and open in full every protected card and every card whose summary, role or facets touch the job; with fewer, read them all. Fill the evidence table in the Change Log: each used card on its own row, with where it went. Unused cards can share one line by reason ("Low: C-012, C-015, unrelated field"), so the table stays short; a protected card, or one that clearly fits the job, gets its own row and its reason. `check_claims.py` warns if a card is missing from the table. Then ask once: is any unused card stronger for this job than something already in the resume? If yes, swap it in or say why not. Stop when no swap clearly adds value (D-019) | Evidence table in the Change Log |
| S3 | **Map to the JD.** For each requirement R1, R2…, sort it into one of five kinds: **Direct** · **Transferable or combined** (a skill from another setting, or several experiences that each prove part of it) · **Not found yet** (ask the [probing questions](#probing-questions) first, D-014, then [look beyond the cards](#looking-beyond-the-cards), D-021; a number marked "to verify" belongs here too) · **Buildable** (a real gap you could close with a small project or course) · **Hard gap** (including an eligibility gate you don't meet). Only "Hard gap" means don't write it. If there's still no evidence after asking, don't stretch to cover the gap. The employer's name, the job title, the location, pay and benefits aren't requirements: they're never a gap. Whether the resume uses the JD's keywords is a separate check from whether it shows the value they ask for (D-011) | Five-way mapping in the Coverage Report |
| S4 | **Delta.** Copy the baseline file in `cv/resumes/` and change only what needs changing: headline, summary, bullet order, keywords. Don't rewrite approved text. If `check_claims.py` says a line was copied from a baseline approved before its card changed, write that line from the current card | New draft |
| S5 | **Change Log.** Number each change as a proposal: Before / After in quotes, the basis (card IDs), and Status `Pending`. Attach a JD Coverage Report and what you checked. Then run `python3 scripts/check_claims.py cv/changelogs/<id>.md --record all` once the user has looked at the rows. Each row is recorded on its own (`--record P2` for just row 2), so a proposal written against a card that later changes shows up as stale, and one that was never checked isn't treated as valid. Put the section or role in Location ("Summary", "Experience"): the script looks for the Before text there | `cv/changelogs/<id>.md` |
| S6 | **AI self-review.** Go through the [REVIEW-CHECKLIST](REVIEW-CHECKLIST.md) sections A and B item by item. Run `python3 scripts/validate_evidence.py` and `python3 scripts/check_claims.py cv/resumes/<id>.md` (both must pass). The PDF and layout check wait for Finalize | Table of self-review fixes, check results |
| S7 | **Human review.** Give the user the full text and a diff against the baseline. They can accept or reject each proposal: mark each row `Accepted` or `Rejected`, and take rejected text back out. A rejected wording is a wording preference, not a fact change: leave the card alone unless they say a fact was wrong. Only when they say it's approved does the status become `Approved`. Then run `python3 scripts/check_claims.py cv/resumes/<id>.md --record all` | The user's approval on record |

Before you apply, **Finalize** (see [task modes](#task-modes)): export, check the layout, and freeze. `python3 scripts/freeze.py cv/resumes/<id>.md <exported.pdf>` records both files' SHA-256 in `cv/frozen.txt`, and `check_claims.py` fails if a frozen resume is edited later. Mark the version `Sent`, and in `cv/CV-INDEX.md` record which job used it.

**Picking up later.** The "Progress" section of `jobs/<job-id>.md` says which steps are done and what's waiting on the user. It's a pointer, not proof: check it against the files (the Change Log, the resume's status) before relying on it, and count something as approved only if the user's own words say so.

## Step 0: Cold start

Do this once, before your first job. It takes you from "I have an old resume" to "I have an approved baseline."

| Step | What to do | Output |
|---|---|---|
| 0a | **Gather raw material**: your current resume, your LinkedIn text, old performance reviews, anything with facts in it. Put it in `evidence/sources/`. That folder is git-ignored, so it never gets committed | Files in `evidence/sources/` |
| 0b | **Checkup report.** Use prompt 1 in [PROMPTS](PROMPTS.md). The AI reads the resume, counts what [REPORT](REPORT.md) asks for, and fills `report/template.html`. You get a scored, visual report before any interview: what's strong, what's vague, the five fixes that matter most. Then it asks whether you want a shareable version | `reports/<date>-checkup.html` and its card as a PNG, a three-line summary in the chat, and `-share.html` if you asked for one |
| 0c | **Interview plan.** The AI picks your **3 strongest** accomplishments (enough for a first baseline; the rest can wait), lists only what's still missing for each after reading your material, and writes the plan into `evidence/INTAKE.md`: how many questions, about how long. You pick a mode (see below) | `evidence/INTAKE.md` |
| 0d | **Interview and write cards.** Use prompt 2. Every question starts with a progress line. Skip any question or stop any time: what's unanswered goes on the card as "To fill", not into more questions. After each accomplishment, the AI shows you the card's essentials (the wording it would use, the numbers, what not to say). Say "right" or fix a few things, and the card is `Safe to draft`: no separate review round, unless it's risky (see "What counts as risky") | Claim Cards in `evidence/claims/`, `INTAKE.md` updated |
| 0d+ | **Fill in `evidence/profile.md`**: your roles (title, company, start, end) and education, taken from your resume and confirmed by you. `check_claims.py` checks every role heading and Education line against it | `evidence/profile.md` |
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
- Write from the current cards, not from an older follow-up card or the chat. Then run `python3 scripts/check_claims.py interview/<job ID>.md --record all`. If the sent version predates a card change, the check says so: the sent file stays as it is, so put the difference under "Read this first: risks" and prepare from the current card.

### Reviewed answers

An answer the user has approved ("Why are you leaving?", "Tell me about a launch that went wrong") can be reused, but only where it fits and only while its cards haven't changed.

- **Where**: `interview/answers/<A-id>.md`, in the format of [`interview/answers/_TEMPLATE.md`](../interview/answers/_TEMPLATE.md). Tag each fact with its card ID.
- **Scope**: `reusable` (fits any job), `employer: <name>` (the company name exactly as `company:` reads in the job file; case and punctuation don't matter, but "Harbor" doesn't match "Harbor Analytics"), or `job: <job ID>` (written for one application). An answer is never reused outside its scope. The user's approval covers the question, the scope and everything in the file except Notes, so changing any of them needs a new confirmation. Use records go in Notes and never trigger one.
- **Record it** once the user approves it: `python3 scripts/check_claims.py interview/answers/<A-id>.md --record all`.
- **Before reusing**: `python3 scripts/list_claims.py --answers <job ID>` lists the answers that fit and whether each can be reused. Only `yes` means as it is: it cites cards, none is missing or changed, it was checked against them, and the user approved it. Anything else (not approved, not checked, no card cited, a card missing, a card changed) is rewritten from the current cards and confirmed again.

## When a fact changes

The goal: the user corrects a fact once, and every later step knows. Nothing that used the old fact is reused without anyone noticing, and nothing unrelated has to be reviewed again (D-020).

**1. Is it a correction or a wording change?** A correction changes what is true or claimable: what happened, a number or what it measures, who did which part, a status, what not to say. "The $200K wasn't marketing budget, it was sponsorship I negotiated" is a correction. "Make that bullet punchier" is wording: change the resume, not the card. If you can't tell, ask one question.

**2. Correct the card first**, in the same turn, and say back what changed in one line. Keep the strongest true version of the result: a correction narrows a claim, it doesn't delete the accomplishment (D-015). If the correction makes the source weaker ("I don't have that report any more, it's from memory"), lower the card's evidence strength or status too, not only the Source line: that's what tells every file citing it that this is a major change.

**3. See what it touches**: `python3 scripts/list_claims.py --used-by C-xxx`. Tell the user which files cite the card and whether each needs a recheck. Don't edit approved or sent files on your own.

**4. From then on the card wins.** Anything said earlier in this chat, in an old resume or in a follow-up card that disagrees with it is void. After many corrections, suggest a fresh session.

**How the check knows.** `check_claims.py --record` stores fingerprints of each card's blocks, plus the lines that cite it, in `cv/reviewed.txt`. On every run the script works out each file's state from those; nothing is written into the resumes:

| State | Means | What happens |
|---|---|---|
| Current | Every card it cites matches what was approved | Nothing |
| Needs recheck | A cited card changed after approval | WARN, naming the card and the blocks that changed. At `--finalize`, a major change is an error, and so is any change when the lines citing the card were also edited after approval |
| Sent before the change | The version was sent, then a card changed | A note only. The sent file stays as it is; the follow-up cards get the warning |
| Card missing | It cites a card ID that doesn't exist and was never recorded here: a typo, or a card deleted before 0.7.0. (A card deleted after the record shows as Needs recheck: card removed) | Listed by `--used-by` and `--health`. In a resume, `check_claims.py` already fails on an unknown ID |
| Not checked | No record yet (versions made before 0.7.0, or an incomplete record), or the lines were edited after the record | One summary line. At `--finalize`, an error until the user confirms and you record |

**Current is not approved.** These states only say whether the lines still match the cards. Whether the user approved a version is its status (Draft / Approved / Sent), and only the user changes that. A current Draft is still a draft, and a reviewed answer is reused only if it is both current and Approved.

A draft copied from a baseline also gets a WARN on every line copied unchanged from a baseline that was approved before its card changed: that's how an old wording slips into a new version.

| Major (can change what's true) | Minor (usually wording) |
|---|---|
| What happened (and the card's title), numbers and their Verified column, attribution, status / evidence / role / period, don't rephrase as, and protected / keep-for when it changes what this file's job type must keep | Approved wording, capability facets, source, any section the template doesn't have. Notes and To fill never count |

Spacing, a line wrapped inside a paragraph, bold, dash styles and 1,234-style thousands separators don't count as changes. A new bullet or row does, and so does `1.234`, `1 234` or a decimal comma, since those differ by region. The convention: a comma between digits followed by exactly three digits is a thousands separator, so `€2,100` and `€2100` are the same number. Write decimals with a point (`€2.1K`), never a comma, on the cards; every other character does, so `$2.1M` → `$21M` is a change and `$200,000` → `$200000` isn't.

**Rechecking.** Show the user only the lines citing the changed card, next to the card's current text. If they still hold, run `--record C-xxx` for that card only; the rest of the version keeps its approval. If not, make a new version (an approved or sent file isn't edited in place).

**A needs-recheck isn't a finding of error.** It means nobody has looked at those lines against the corrected card yet.

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

**No evidence, no claim.** If the JD wants something the evidence bank doesn't cover, even after you've looked beyond the cards (D-021), put it under "None" in the Coverage Report. The user decides whether to build the evidence, cover it in the interview, or skip the job.

**Don't cut strong results without a reason.** Removing an existing strong bullet has to pass three tests: relevance (it doesn't help for this job), accuracy (there's doubt about it), or space (it doesn't fit). Write the reason in the Change Log. A claim marked `protected: true` can't be weakened without the user's approval. If its card lists `keep-for` types, it must stay in resumes of those types and may be left out of others; with no `keep-for`, it stays everywhere.

**Two kinds of error.** Writing something the evidence doesn't support is one (commission). Leaving out something the evidence does support, and the job would value, is the other (omission). The checks catch the first; the evidence table in S2 is there for the second (D-019).

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

## Looking beyond the cards

The cards are where confirmed facts live. But a real accomplishment can sit in the user's own material (a project review, a performance review, interview notes) with no card yet, and calling it "no evidence" would be wrong (D-021). This is how to look without reading everything every time.

### When to look

Start from the cards, including their text, not only the one-line list. Look further only in these cases:

| Where the cards leave a requirement | Look further? |
|---|---|
| Strong, direct evidence | No. Stop |
| Only weak or transferable evidence | Yes, if it's a gate or a core skill |
| A card that lacks the result, scale or attribution the job needs | Ask the user first ([probing questions](#probing-questions), D-014), then look in the sources |
| A gate requirement with nothing behind it | Always |
| A nice-to-have | Only the few where an extra look could change the outcome |

Effort follows importance, not a fixed count: every gate gets the look, so none is called "no evidence" for lack of effort. What you don't have the room to look into is reported as "not examined further", never as "no evidence".

### Where to look, in order

1. The cards, every status. A `Needs review` card or a "To fill" line may already hold it, and an `Interview only` card isn't for a resume. A `Retired` card is never support: if the same fact turns up again, it stays retired unless the user brings it back.
2. `evidence/profile.md` and the reviewed answers in `interview/answers/`.
3. The files in `evidence/sources/`, and any place the user's own rules name (for example "also look in my notes app"). `python3 scripts/list_claims.py --sources` lists the files with fingerprints and shows what is new, changed or skipped.
4. Old resumes and follow-up cards: clues to follow, never proof (AGENTS).

A file read before is still a place to look: one pass rarely takes everything out of a long document. "Read before", "changed since read", "renamed" and "skipped" describe the file, not the evidence in it.

### How to read a source

- Find the relevant part locally first (search, a table of contents, a page range) and give the model only that. If your tool can't read part of a file (a scanned PDF, an image, a connector), say so and let the user choose: send an excerpt, allow the whole file, or skip it.
- A **skipped** source is one the user listed under "Skipped sources" in `evidence/INTAKE.md`: a file, or a folder written with a trailing `/`. Never open, search or quote it, and never give it to a model. The script doesn't open it either. For the other files the script only computes a fingerprint, on this computer; it reads no text and sends nothing anywhere.
- Cloud-synced folders: `--sources` recognises iCloud placeholder files and doesn't open them. It recognises only iCloud. With any other sync tool, fingerprinting can download a file, so use `--sources --no-hash` to list names and sizes only.
- Before you read a source, note its fingerprint (`python3 scripts/list_claims.py --fingerprint <file>`). Before you write what you found into a card, run it again, and also fingerprint the card you are about to change before you read it and again before you write. If either one changed, look at the affected part again instead of writing from the old read. This catches an edit made while you worked; it isn't a lock.
- After a real read, add a row to "Source records" in `evidence/INTAKE.md`: the path, the fingerprint, the date. Don't register files you haven't read. Which job and requirement you looked at goes in that job's Coverage Report, not in INTAKE.

### What to do with what you find

- The same accomplishment as an existing card (any status, `Retired` included), or as something the user declined (below): update that card or leave it alone. Never open a new ID to get around one.
- Something new: write a card with status `Needs review`, name the file and the page, section or a redacted excerpt as its Source, and ask the user one question.
- Who has to confirm what:

| The fact comes from | Confirm with the user? |
|---|---|
| An old resume, a document or notes, found by the AI | Yes, until they say it's right |
| Something the AI worked out: who caused what, whose part it was | Yes |
| What the user said in this chat | No: their own account is confirmed (D-017) |
| A correction from the user | No: update the card (D-020) |
| Something the user said they're unsure of | Yes |

- **When a source disagrees with a card:**

| What it is | What to do |
|---|---|
| An old document that contradicts something the user later corrected | The card wins; don't ask again |
| New material that could overturn the card | Mark the conflict (below) and ask |
| The user correcting a fact | Do it now (D-020) |
| The same fact worded differently | Not a conflict |
| A different amount, owner, unit or period | Mark it and settle it before Finalize |

To mark a conflict, use what already exists: put `to verify` in the Verified cell of the disputed number, or set the card to `Needs review` if the accomplishment, or who did it, is disputed (split the card if only part of it is in doubt). Say why under "To fill" on the card. `check_claims.py` then stops any line that uses it, and `--finalize` stops a version that cites it; a version that doesn't cite it is not affected. `protected-ok` only approves leaving a protected claim out. It never excuses keeping a claim whose card is disputed.

### Not asking twice

When the user says no to something you found, add a row under "Declined facts" in `evidence/INTAKE.md`: what it was, why (wrong · not mine · true but not for a resume) and the date. If a card exists for it, fix the card instead (D-020). Don't record "not needed for this job" (that belongs in that job's evidence table) or "no time now" (leave the card `Needs review`). Check the list before you ask about something you found.

### What to report

In the Coverage Report keep two things apart: what the evidence is (confirmed, waiting for the user, conflict, not found) and how far you looked (cards, sources too, partly, not accessible, not examined further, waiting for the user). "No evidence" means the cards and the sources were checked and there is none; if something couldn't be checked, say that instead. List the files you actually read under "Scope of check". The report is your own account of the search: nothing in it proves it.

## Coverage Report format

```markdown
| # | JD requirement | Gate | Kind | Evidence | Checked | Next step |
|---|---|---|---|---|---|---|
| R1 | Requirement A | yes | Direct | C-003 | Cards | n/a |
| R2 | Requirement B | | Transferable or combined | C-007 (different setting) + C-002 | Cards | Lead with the transferable skill; be ready to say how the setting differs |
| R3 | Requirement C | | Not found yet | n/a | Cards and sources | Ask the probing questions; may turn up evidence |
| R4 | Requirement D | | Buildable | n/a | Not examined further | A small project could close it; your call |
| R5 | Requirement E | yes | Hard gap | n/a | Cards and sources; one source not accessible | Left out. Answer it in the interview, or skip the job |

**Checked** says how far you looked: Cards · Cards and sources · Partly (say what's missing) · Not accessible · Not examined further · Waiting for the user. An evidence line that is waiting for the user, or in conflict with a source, says so in Evidence or Next step.

**Scope of check**: covered …; not covered … (reason); files read: …
```

In a job-fit report, Direct counts as `direct`, Transferable or combined as `partial`, and the other three as `none`.

## When a new type is warranted

Open a new type in `CV-INDEX` only if all three are true. Otherwise treat it as a job-specific version of an existing type.

1. The headline and summary need a full rewrite, not just new keywords.
2. More than half of the experience bullets change priority.
3. You expect to apply to 3 or more jobs of this kind.
