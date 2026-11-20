# Eval results

One section per run, newest first. Record the kit versions compared, how many runs per side, and what changed because of the run.

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
