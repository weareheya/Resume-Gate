# LESSONS: Common process mistakes

> Each entry: what happened → why → the guardrail now. When a new mistake happens, add it at the top.
> Rules about facts and numbers belong in DECISIONS or a Claim Card. This file is for **process** mistakes.

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
