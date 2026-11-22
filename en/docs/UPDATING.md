# UPDATING: Getting a newer version of the kit

> Read this only when the user asks to check for updates (prompt 5 in [PROMPTS](PROMPTS.md), or `/update`).

1. Read `VERSION`. Get the latest kit: https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-en.zip. It's a public download: no GitHub account or connector is needed. If your tool needs approval to use the network, ask once; or ask the user to download and unzip it into this folder.
2. If its `VERSION` isn't newer, say so and stop. If it is, show the user the `CHANGELOG.md` entries since their version, including any "What you need to do" notes.
3. With the user's go-ahead, replace **only kit files**: `AGENTS.md`, `CLAUDE.md`, `.claude/commands/`, `README.md`, `LICENSE`, `VERSION`, `CHANGELOG.md`, everything in `docs/` except `MY-DECISIONS.md`, `scripts/`, `report/`, `examples/`, `assets/`, and every `_TEMPLATE.md` (including `interview/_TEMPLATE.md`).
4. **`.gitignore` is not replaced automatically.** The user may have changed it, for example by deleting the block that keeps personal files out of Git because their repository is private and they want those files backed up. Replacing it would quietly stop that backup. If the new kit's `.gitignore` differs from theirs, show the difference and ask whether to take it.
5. **Never touch the user's files**: `docs/MY-DECISIONS.md`, `evidence/` (apart from its `_TEMPLATE.md`), `cv/` (apart from the `_TEMPLATE.md` files), `jobs/` and `interview/` (apart from their `_TEMPLATE.md`), `reports/`.
6. If the user had edited a kit file (for example added rules to `docs/DECISIONS.md` before MY-DECISIONS existed), move their changes into `docs/MY-DECISIONS.md` first and show them what moved.
7. Run `python3 scripts/validate_evidence.py`, then `python3 scripts/check_claims.py` on every resume still in use (each Approved version in `cv/CV-INDEX.md`, and versions already sent, which are only read, never edited: report what fails), not only the newest: an older resume can fail a rule that is new. Tell the user in plain words which pass and which now need a fix. Commit only after the user approves.
