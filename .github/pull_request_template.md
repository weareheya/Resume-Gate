## What changed

## Why

## Rule changes: D-017 check
Fill this in if the PR adds or tightens a check, a rule, or a default. Otherwise write "none".

- [ ] Each new **error** names the fabrication it stops (a changed amount, scale or currency, a banned phrase, an invented role, a claim with no card...). Anything that might be wording or is just incomplete is a **warning**.
- [ ] Each new error has a way through once the user agrees (e.g. `protected-ok:`).
- [ ] Self-stated facts and blank fields the user didn't fill are still accepted. No new rule asks for documents.
- [ ] Updating needs no action before existing resumes pass again. Anything that does is listed as optional in the CHANGELOG.
- [ ] Tests cover both directions: the fake fails, and `HonestResume` (an honest resume with ordinary gaps) still passes.
- [ ] en and zh-CN were changed together (`python3 tools/check_sync.py`).

## Documentation impact
Does this change what users see or do: a feature, the workflow, a product claim, privacy, or a limit? If yes, update only the READMEs, examples, flow chart or privacy notes it touches (en and zh-CN together). If not, write "Documentation impact: none". `python3 tools/check_sync.py` already checks version numbers and the rule count; whether the descriptions are still true is for this check.

## Test plan
