# LESSONS: Common process mistakes

> Each entry: what happened → why → the guardrail now. When a new mistake happens, add it at the top.
> Rules about facts and numbers belong in DECISIONS or a Claim Card. This file is for **process** mistakes.

## L-12 · A strength that had been corrected came back weakened (semantic regression)
- **What happened**: The user had already corrected it once: the core of an experience was a regional narrative strategy, not relationship management. In the next version the experience was still there, Claim ID and all, but the wording had slid back to "relationship management."
- **Why**: The AI rewrote toward the JD's familiar vocabulary and swapped an unfamiliar strength for a familiar, weaker phrase. `check_claims.py` only checks that the Claim ID is present, so it passed.
- **Guardrail**: During self-review, compare the wording of every `protected` claim with its approved wording, sentence by sentence, and check whether the meaning got weaker (REVIEW-CHECKLIST A). Put wording you've already corrected into the Claim Card's "don't rephrase as" list.

## L-11 · The AI "remembered" a difference that never existed
- **What happened**: In a retrospective, the AI said two applications had used two differently positioned resumes. CV-INDEX recorded the same hash for both exported PDFs: they were the same file.
- **Why**: The AI wrote the retrospective from conversation memory instead of checking the records.
- **Guardrail**: Retrospectives, audits, and write-ups of the method go by `cv/CV-INDEX.md`, the Change Logs, and file hashes, never by conversation memory.

## L-10 · A decision lived in one tool, and the next session lost it
- **What happened**: The job-type taxonomy had already been settled in the project. Another session, working in a different tool, never read it and proposed rules that already existed as if they were new.
- **Why**: The Evidence Retrieval Gate only required reading Claim Cards, not DECISIONS or CV-INDEX.
- **Guardrail**: Every settled decision lives only in `docs/DECISIONS.md`. Any new session, in any tool, reads DECISIONS and CV-INDEX before the evidence (see the reading order in AGENTS.md).

## L-09 · An error in an approved resume got inherited
- **What happened**: A number was wrong in an old resume. Because that resume was approved, the AI treated it as a valid source and copied the number into every new version.
- **Why**: The rules said a fact could come from a Claim Card *or* from an approved version, so a mistake could bypass the evidence bank.
- **Guardrail**: An approved or sent resume is approved wording, never evidence. Every line must still trace to a Claim Card (AGENTS.md, D-003).

## L-01 · A confirmed result dropped out of the new version
- **What happened**: A result that had already been verified was left out of a new resume, or weakened.
- **Why**: The AI didn't re-read the evidence bank and wrote from what it remembered of the conversation.
- **Guardrail**: Evidence Retrieval Gate (WORKFLOW S2), and the AI has to list which Claim IDs it read.

## L-02 · A new version went back to an older one
- **What happened**: The new version didn't start from the latest approved one, so old errors came back.
- **Guardrail**: Baseline + delta + Change Log (WORKFLOW S1, S4, S5; `cv/CV-INDEX.md`).

## L-03 · The same resume kept getting restructured
- **What happened**: A structure that had been settled (for example, merging the summary with key results) was overturned in the next round.
- **Guardrail**: Every approved design decision goes into DECISIONS, and the AI checks the scope = cv entries before generating.

## L-04 · "Checked" was claimed, but things were missed
- **Guardrail**: Coverage Report. State what was checked and what wasn't. "Check complete" with no scope doesn't count.

## L-05 · An uncertain version was recorded as the one that was sent
- **What happened**: The user couldn't remember which version they'd sent, so one file was linked to the application as "sent" on a guess. That left a believable but wrong record.
- **Guardrail**: Record only versions the user has **confirmed**. If unsure, leave it blank and note the guess and its basis.

## L-06 · Two sessions numbered decisions independently and collided
- **What happened**: Two AI sessions were setting rules at the same time. Each took the highest number it could see and added 1, so the numbers clashed. One of them wrote its number only in the chat, not in DECISIONS, so the clash was invisible.
- **Guardrail**: Write a new decision into DECISIONS right away. Before numbering, run `grep "^## D-" docs/DECISIONS.md`, take the highest, and add 1. Let only one session edit the rule files at a time.

## L-07 · A few extra lines became an orphan page
- **What happened**: After a content edit, page 3 held just 2 lines.
- **Guardrail**: Run `scripts/pdf_fill.swift` on every export. Cut weak bullets first, then adjust layout settings (D-009).

## L-08 · Status was judged from the subject line alone
- **What happened**: A rejection email was taken for an application receipt because it also began "We received your application."
- **Guardrail**: Judge an application's status from the **full body** of the email, never from the subject or preview.
