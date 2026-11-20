# Eval results

One section per run, newest first. Record the kit versions compared, how many runs per side, and what changed because of the run.

**Scorer change in 0.6.0**: critical recall now counts a card only when its ID is tagged on a visible resume line, and a crashed `check_claims.py` is "could not run" instead of zero errors. Runs before 0.6.0 used the looser count, so their recall figures may read slightly high; compare new rounds with new rounds. The saved outputs of the rounds below weren't kept (`evals/runs/` is local), so they weren't re-scored. The reference answers pass under the new rules.

## 2026-11-20 · v0.5.2 vs v0.6.0 · product-manager, three runs per side, plus a blind read

**Setup**: a spot check of 0.6.0's lighter reading on the case where wording matters most. Six fresh sessions (an AI assistant, no user answering questions), each in its own copy of that version's `en/` kit, with the `jordan-lee` cards, profile and two baselines. Each used prompt 3 with the job pasted in. Scored with `score.py` (0.6.0 rules). The blind read used one AI reviewer acting as a recruiter, with only the job posting and the A/B files from `blind.py`.

| Kit | Pass (of 3) | check_claims errors | Critical recall | Oversell found | Gap kinds | Evidence table | Tokens per run (avg) |
|---|---|---|---|---|---|---|---|
| v0.5.2 | 3 | 0 | 100% | none | 100% | complete | ~101k (95k–109k) |
| v0.6.0 | 3 | 0 | 100% | none | 100% | complete | ~100k (98k–102k) |

**Blind read**: one pair tied with a slight edge to v0.6.0, one tied with a slight edge to v0.5.2, and one went to v0.5.2 (fit 4 vs 3) because that run added an extra bullet on partner segmentation from C-001. Every version was rated 4/5 believable, nothing oversold, and got an interview. All six said "built with engineering", so the 0.5.2 fix for underselling held.

**What it says**
- No regression: on integrity, recall, oversell, gap kinds and the evidence table, both versions were clean in every run, and the blind read found no consistent difference. The one loss came from run-to-run variation in which C-001 details were used, not from a kit rule.
- Tailor didn't get cheaper, as expected: the read-by-task table still sends Tailor to DECISIONS, WORKFLOW, LESSONS and the checklist, so all six runs read nearly the same files. 0.6.0's savings are elsewhere: quick edits and finalize read less, and big evidence banks use `list_claims.py`. Those weren't measured here (the example bank has 5 cards).
- One v0.5.2 run spent the most (109k tokens, 26 tool calls, twice as long) exporting and rendering a PDF during S6. In 0.6.0 that check moves to Finalize, so tailoring no longer does it.
- Both versions still warn that the Skills line isn't verified by script. Each run checked it by hand.

**Changed because of this run**: nothing. 0.6.0 ships as is.

**Limits**: one case, one AI reviewer, three runs per side. Token counts come from the assistant's own usage figures and vary between runs.

## 2026-11-20 · v0.2.3 vs v0.5.1 · three runs per side, plus a blind read

**Setup**: as in the first run below. v0.2.3 reuses that run plus two new ones; v0.5.1 had three fresh runs. 18 resumes in all. Scored with `score.py`. `check_claims.py` from 0.5.1 was also run on every output. A blind read compared the three product-manager pairs: one AI reviewer acting as a recruiter, given only the job posting and the A/B files from `blind.py`.

| Case | Kit | Pass (of 3) | check_claims errors | Critical recall | Oversell found | Gap kinds (avg) | Evidence table |
|---|---|---|---|---|---|---|---|
| channel-bd | v0.2.3 | 0* | 0 | 100% | none | not produced | not produced |
| channel-bd | v0.5.1 | 3 | 0 | 100% | none | 83% | complete |
| product-manager | v0.2.3 | 0* | 0 | 100% | none | not produced | not produced |
| product-manager | v0.5.1 | 3 | 0 | 100% | none | 92% | complete |
| customer-success | v0.2.3 | 0* | 0 | 100% | none | not produced | not produced |
| customer-success | v0.5.1 | 3 | 0 | 100% | none | 100% | complete |

\* v0.2.3 fails only because it doesn't produce the evidence table or gap kinds. On the resume text alone, all 9 of its runs were clean too.

**Blind read (product-manager)**: the reviewer preferred v0.2.3 in all three pairs (one nearly a tie). Every version was rated believable with nothing oversold, and every version got an interview. The reason was the same each time: the v0.5.1 versions never mentioned engineering, and the job's one required skill is "write requirements *with engineering*". All three v0.2.3 versions said so ("built by engineering", "with engineering"). That is underselling, and it was caused by our own 0.5.1 nudge: told not to imply they built the portal, the runs dropped engineering altogether.

**What it says**
- Both versions are now clean on integrity, recall and oversell for these cases. v0.5.1's extra outputs (positioning, evidence table, gap kinds) were consistent across runs.
- v0.5.1's "Don't rephrase as" guidance overcorrected into underselling on the one case where the true story includes another team.
- The scorer flagged "Engineering designed and built it" as oversell. That was a false positive: the sentence is accurate attribution. The `built` patterns now target the candidate as builder ("built the…", "built with…", "helped build").
- `check_claims.py` also warns on "built by engineering". That is noise, but it is only a warning, and the self-review note now says how to resolve it.

**Changed because of this run**: kit 0.5.2 redraws the line as sole credit vs shared credit. "Built with engineering" is reasonable packaging (the maintainer's call, and what the blind reader rewarded). Only "built the portal"-style sole credit is ruled out (REVIEW-CHECKLIST A, LESSONS L-14). The gold's `built` patterns now target sole credit only. By this rule, the first run's "a portal, built with engineering" wasn't an oversell either.

**Limits**: one AI reviewer, one case blind-read, three runs per side. Treat this as direction. Have a real recruiter do the blind read before drawing firmer conclusions.

## 2026-11-20 · v0.2.3 vs v0.5.0 · one run per side

**Setup**: one fresh session per case and kit version (an AI assistant with no user answering questions). Each workspace had the same evidence bank (the current `en/examples/jordan-lee` cards and profile) and the same two baselines; only the kit's instructions differed. Each used that version's prompt 3 with the job pasted in. Scored with `score.py` from this repo.

| Case | Kit | check_claims errors | Critical recall | Should recall | Oversell found | Gap kinds | Evidence table |
|---|---|---|---|---|---|---|---|
| channel-bd | v0.2.3 | 0 | 100% | 100% | none | not produced | not produced |
| channel-bd | v0.5.0 | 0 | 100% | 100% | none | 100% | complete |
| product-manager | v0.2.3 | 0 | 100% | n/a | none | not produced | not produced |
| product-manager | v0.5.0 | 0 | 100% | n/a | "a portal, built with engineering" | 100% | complete |
| customer-success | v0.2.3 | 0 | 100% | 100% | none | not produced | not produced |
| customer-success | v0.5.0 | 0 | 100% | 100% | none | 75% | complete |

**What it says**
- On the resume text, both versions were clean on integrity and recall. One run per side can't separate them on quality, and v0.5.0 slipped one oversell: "built with engineering" blurs C-002's "engineering built it". The script can't catch that by design (it's trap 6 in the worked example); the self-review should have.
- v0.5.0 produced what v0.2.3 doesn't: the saved JD, positioning options for stretch jobs, an evidence table covering every card, and five-way gap kinds. Its gap calls mostly matched gold; the misses were defensible ("Not found yet" before the user has been asked), so gold now accepts more than one kind where a careful reviewer could differ.
- v0.5.0 restored the portal card (C-002) for the channel job where v0.2.3 left it out, and left out pipeline (C-003) for customer success. Both choices were explained in the evidence table.

**Changed because of this run**: kit 0.5.1 warns on wording a card's "Don't rephrase as" quotes, and the self-review checks softer versions of a ruled-out claim (LESSONS L-14); re-run on the same outputs, it flags the product-manager line and nothing in the other five. `score.py` reads a kind followed by a note ("Direct (marketing only)"), and gold can list several acceptable kinds.

**Next**: three or more runs per side before drawing conclusions, and a blind A/B/C read of the product-manager pair, where the two versions differ most.
