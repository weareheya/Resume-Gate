# LESSONS: Common process mistakes

> Each entry: what happened → why → the guardrail now → the test that guards it. When a new mistake happens, add it at the top.
> Rules about facts and numbers belong in DECISIONS or a Claim Card. This file is for **process** mistakes.
> Before adding a guardrail, ask what it costs: who it slows down, which honest case it could block, and whether a later step already catches the mistake. Several guardrails below were revised in 0.6.0 because they did more harm than the mistake they fixed (L-01, L-04, L-07, L-10, L-12).

## L-15 · A corrected fact came back in the next version
- **What happened**: The user explained that an amount was sponsorship they negotiated, not a marketing budget. The chat moved on, but the card and the approved baseline still said budget, so the next tailored version copied the old wording from the baseline.
- **Why**: The correction lived only in the chat. Nothing linked the baseline's lines to the version of the card they were approved against, so nothing could say they were out of date.
- **Guardrail**: Correct the card first, in the same turn (AGENTS, "Correct once"). `check_claims.py --record` stores what each approved file was checked against; when a card changes, the files that cite it are flagged, and lines copied from an out-of-date baseline get a warning. Only `--finalize` blocks (D-020).
- **Side effect to watch**: a big correction can flag many files. Recheck only what you're about to reuse or send; the rest can wait.
- **Test**: `DependencyHealth` in `test_check_claims.py`, and the `fact-correction` eval.

## L-14 · Sole credit vs shared credit
- **What happened**: In the first eval run (2026-11-20), a product-manager version said the candidate wrote the requirements for "a self-serve partner portal, built with engineering", where the card says engineering built it. The next kit version (0.5.1) treated that as oversell. In the following run, all three product-manager versions dropped engineering altogether, and a blind reviewer preferred the older versions, which named the collaboration.
- **Why**: The line between packaging and fabrication was drawn in the wrong place. Shared wording ("built with engineering", "launched with the product team", "partnered with engineering on") is ordinary, defensible framing: it's true, and the candidate can explain their part in an interview. What a card rules out is **sole credit**: "built the portal", "launched the portal" as if no one else did.
- **Guardrail**: `check_claims.py` warns when a line uses wording that a card's "Don't rephrase as" puts in quotes, so quote the sole-credit phrase ("built the portal"), not the bare verb. Self-review asks one question: does the line claim someone else's work as yours alone? Some vagueness is fine; going silent about a true collaboration is underselling (D-015).
- **Side effect to watch**: if a card quotes wording that is fine ("built with engineering"), every honest line using it gets a warning. Quote only the sole-credit phrase.
- **Test**: `test_traps_fail_with_six_errors` (the trap's "built and launched" warns) and the eval baseline, which must show no warning on shared credit.

## L-13 · New checks were stricter than real life
- **What happened**: Twice, a hardening pass added rules that real job searching can't meet: a card needing a document to count, new cards defaulting to `Needs review`, and in 0.3.0's first draft a blank Verified cell failing, a missing profile failing every resume, and any stray "two" or single digit failing. Even an approved protected-claim drop kept failing, with no way to record the approval.
- **Why**: Each rule was judged by "could this hide a fake?" instead of "what fake does this stop, and what does it cost the user?" Strictness felt safe, so it went unquestioned.
- **Guardrail**: D-017. Before shipping a check, sort each case into "stops a fabrication" (error) or "might be wording / incomplete" (warning), give every error an approval path, and make sure an upgrade needs no action. Test both directions: a fake must fail, and an honest resume with ordinary gaps must pass.
- **Test**: `test_ordinary_gaps_pass`, `test_blank_verified_counts_as_confirmed`, `test_single_digits_and_number_words_are_warnings`, `test_evidence_table_gap_is_a_warning`.

## L-12 · A strength that had been corrected came back weakened (semantic regression)
- **What happened**: The user had already corrected it once: the core of an experience was a regional narrative strategy, not relationship management. In the next version the experience was still there, Claim ID and all, but the wording had slid back to "relationship management."
- **Why**: The AI rewrote toward the JD's familiar vocabulary and swapped an unfamiliar strength for a familiar, weaker phrase. `check_claims.py` only checks that the Claim ID is present, so it passed.
- **Guardrail**: During self-review, compare the wording of every `protected` claim with its approved wording, sentence by sentence, and check whether the meaning got weaker (REVIEW-CHECKLIST A). Put wording you've already corrected into the Claim Card's "don't rephrase as" list.
- **Revised in 0.6.0**: in 0.5.1 this list was read too broadly, and ordinary shared-credit wording got pushed out of resumes (L-14). Put in it only the weaker or sole-credit phrasing you corrected, not every nearby verb.
- **Test**: `test_protected_claim_weakened_fails` covers the numbers; the wording itself is self-review.

## L-11 · The AI "remembered" a difference that never existed
- **What happened**: In a retrospective, the AI said two applications had used two differently positioned resumes. CV-INDEX recorded the same hash for both exported PDFs: they were the same file.
- **Why**: The AI wrote the retrospective from conversation memory instead of checking the records.
- **Guardrail**: Retrospectives, audits, and write-ups of the method go by `cv/CV-INDEX.md`, the Change Logs, and file hashes, never by conversation memory.
- **Test**: none yet; `freeze.py --check` makes the hashes easy to compare.

## L-10 · A decision lived in one tool, and the next session lost it
- **What happened**: The job-type taxonomy had already been settled in the project. Another session, working in a different tool, never read it and proposed rules that already existed as if they were new.
- **Why**: The Evidence Retrieval Gate only required reading Claim Cards, not DECISIONS or CV-INDEX.
- **Guardrail**: Every settled decision lives only in `docs/DECISIONS.md` (starter rules) or `docs/MY-DECISIONS.md` (yours). A new session reads MY-DECISIONS for any resume work, and DECISIONS and CV-INDEX before tailoring for a job (the table in AGENTS.md).
- **Revised in 0.6.0**: this used to apply to every task, so even a one-word fix started by reading all the rules. That was the largest fixed cost per session. A quick edit now reads only the user's own rules and the cards it touches.
- **Test**: none; it's a reading rule.

## L-09 · An error in an approved resume got inherited
- **What happened**: A number was wrong in an old resume. Because that resume was approved, the AI treated it as a valid source and copied the number into every new version.
- **Why**: The rules said a fact could come from a Claim Card *or* from an approved version, so a mistake could bypass the evidence bank.
- **Guardrail**: An approved or sent resume is approved wording, never evidence. Every line must still trace to a Claim Card (AGENTS.md, D-003).
- **Test**: `test_needs_review_and_unknown_ids_fail`, `test_number_not_on_card_fails`.

## L-01 · A confirmed result dropped out of the new version
- **What happened**: A result that had already been verified was left out of a new resume, or weakened.
- **Why**: The AI didn't re-read the evidence bank and wrote from what it remembered of the conversation.
- **Guardrail**: Evidence Retrieval Gate (WORKFLOW S2), and the AI has to list which Claim IDs it read.
- **Revised in 0.6.0**: listing every card on its own row grew with the evidence bank, and listing an ID didn't prove the card was used. Now unused cards can share a line, a big bank starts from `list_claims.py`, `check_claims.py` warns about a card missing from the table, and the evals count a card only when it's tagged on a line a reader sees.
- **Test**: `test_evidence_table_gap_is_a_warning`, `test_unused_cards_can_share_one_line`; evals: critical recall.

## L-02 · A new version went back to an older one
- **What happened**: The new version didn't start from the latest approved one, so old errors came back.
- **Guardrail**: Baseline + delta + Change Log (WORKFLOW S1, S4, S5; `cv/CV-INDEX.md`).
- **Test**: `test_missing_baseline_fails`, `test_base_required_when_index_has_a_starting_point`.

## L-03 · The same resume kept getting restructured
- **What happened**: A structure that had been settled (for example, merging the summary with key results) was overturned in the next round.
- **Guardrail**: Every approved design decision goes into DECISIONS, and the AI checks the scope = cv entries before generating.
- **Test**: none; self-review.

## L-04 · "Checked" was claimed, but things were missed
- **Guardrail**: Coverage Report. State what was checked and what wasn't. "Check complete" with no scope doesn't count.
- **Revised in 0.6.0**: a full report after every one-line change buried the one thing that mattered. A [quick edit](WORKFLOW.md#task-modes) reports only what was checked and any problem; Tailor and Finalize keep the full report.
- **Test**: none; `check_claims.py` prints its own scope line.

## L-05 · An uncertain version was recorded as the one that was sent
- **What happened**: The user couldn't remember which version they'd sent, so one file was linked to the application as "sent" on a guess. That left a believable but wrong record.
- **Guardrail**: Record only versions the user has **confirmed**. If unsure, leave it blank and note the guess and its basis.
- **Test**: none; `freeze.py` records the exact file when you send it.

## L-06 · Two sessions numbered decisions independently and collided
- **What happened**: Two AI sessions were setting rules at the same time. Each took the highest number it could see and added 1, so the numbers clashed. One of them wrote its number only in the chat, not in DECISIONS, so the clash was invisible.
- **Guardrail**: Write a new decision into MY-DECISIONS right away. Before numbering, run `grep "^## D-" docs/MY-DECISIONS.md`, take the highest, and add 1. Let only one session edit the rule files at a time.
- **Test**: none.

## L-07 · A few extra lines became an orphan page
- **What happened**: After a content edit, page 3 held just 2 lines.
- **Guardrail**: Check the layout once, at Finalize: `scripts/pdf_fill.swift` on macOS; on other computers the AI looks at the PDF if it can and the user confirms the last page. Cut weak bullets first, then adjust layout settings (D-009).
- **Revised in 0.6.0**: the old rule was "run `pdf_fill.swift` on every export". The script needs macOS, so on Windows and Linux the AI got stuck, and small edits were forced through a PDF export.
- **Test**: none; layout is checked by eye or by `pdf_fill`.

## L-08 · Status was judged from the subject line alone
- **What happened**: A rejection email was taken for an application receipt because it also began "We received your application."
- **Guardrail**: Judge an application's status from the **full body** of the email, never from the subject or preview.
- **Test**: none.
