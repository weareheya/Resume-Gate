# UPDATING：升级工具包

> 只在本人要求检查更新时读（[PROMPTS](PROMPTS.md) 的提示词 5，或 `/update`）。

1. 读 `VERSION`。下载最新版：https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-zh-CN.zip。这是公开下载，不需要 GitHub 账号或连接器。如果联网要批准，就问一次；或者请本人自己下载并解压到这个文件夹。
2. 新版的 `VERSION` 不比本地新，就说明并停下。比本地新，就把本地版本之后的 `CHANGELOG.md` 条目给本人看，包括「你需要做什么」。
3. 本人同意后，**只替换工具文件**：`AGENTS.md`、`CLAUDE.md`、`.claude/commands/`、`README.md`、`LICENSE`、`VERSION`、`CHANGELOG.md`、`docs/` 里除 `MY-DECISIONS.md` 以外的全部文件、`scripts/`、`report/`、`examples/`、`assets/`，以及各个 `_TEMPLATE.md`（包括 `interview/_TEMPLATE.md`）。
4. **`.gitignore` 不自动替换。** 本人可能改过它，比如仓库是私有的、想让 Git 备份，所以删掉了「个人资料不进 Git」那一段。直接替换会让备份悄悄停掉。新版的 `.gitignore` 和本地不一样时，把差异给本人看，问要不要换。
5. **永远不动本人的文件**：`docs/MY-DECISIONS.md`、`evidence/`（`_TEMPLATE.md` 除外）、`cv/`（各 `_TEMPLATE.md` 除外）、`jobs/` 和 `interview/`（各自的 `_TEMPLATE.md` 除外）、`reports/`。
6. 如果本人改过工具文件（例如在有 MY-DECISIONS 之前往 `docs/DECISIONS.md` 里加过规则），先把这些改动挪进 `docs/MY-DECISIONS.md`，并告诉本人挪了什么。
7. 先跑 `python3 scripts/validate_evidence.py`，再对每一份还在用的简历（`cv/CV-INDEX.md` 里每个 Approved 的版本，已投出的版本也算，但只读不改：不通过的只报告）跑 `python3 scripts/check_claims.py`，不要只跑最新的：旧简历可能过不了新规则。用大白话告诉本人哪些通过、哪些现在要改。本人同意后再提交。
