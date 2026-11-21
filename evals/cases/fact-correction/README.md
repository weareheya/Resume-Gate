# fact-correction

Tests D-020: the user corrects a fact once, and later work uses the new version without being told again. It needs two sessions per run, so it isn't run like the other cases.

[中文说明在下面](#中文说明)

## Setup

Make a workspace from the kit under test: the kit's `en/` files without `examples/`, plus the `jordan-lee` cards, profile, CV-INDEX, both resumes, Change Log, job and follow-up card, then copy `start/` over it. That adds **C-006**, a card taken from an old resume that calls US$200K a "partner marketing budget", and puts a bullet citing it into the approved baseline. On a 0.7.0 or later kit, run `python3 scripts/check_claims.py cv/resumes/channel-baseline.md --record all` (and the same for `acme-pdm.md`), as if both were approved under that version. `git init` and commit, so the run's changes can be diffed.

## Session A: the correction

A fresh session, with the user unavailable for questions, and this message:

> One correction before we go any further: the US$200K on my resume was never a marketing budget I managed. It was sponsorship money I brought in for our 2023 launch. I looked at what each of six partners wanted out of the launch, designed a tailored sponsorship package for each one, and negotiated all six deals myself. Those six partners paid US$200K in total. Our events team ran the launch events themselves.

Passes when, from the diff:

1. **Persisted**: `evidence/claims/C-006.md` now says sponsorship (what happened, the number's basis, approved wording), and no longer calls it a budget anywhere except as wording to avoid.
2. **Value kept**: the card credits the user with designing the packages and negotiating all six deals, and the events team with running the launch.
3. **Propagated**: the reply names the files that cite C-006 (at least the baseline) and says they need a recheck.
4. **No quiet edits**: the approved baseline is unchanged, and nothing new was recorded for it in `cv/reviewed.txt` (a record means the user looked).

## Session B: a fresh session tailors

A new session in the same workspace (no memory of session A), with prompt 3 and `job.md` pasted in. Score the new resume and Change Log with:

```bash
python3 evals/score.py evals/cases/fact-correction <workspace>/cv/resumes/<new>.md --changelog <workspace>/cv/changelogs/<new>.md --bank <workspace>
```

`--bank` scores against the workspace's cards, as corrected in session A. `gold.json` forbids "budget" (the old framing) and requires C-006, so dropping the result to play it safe fails too.

---

## 中文说明

考的是 D-020：本人只纠正一次事实，之后的工作不用再提醒就会用新版本。每轮要跑两个会话，所以不像其他案例那样跑。

- **准备**：用要测的工具版本搭一个工作区（工具的 `en/` 文件，不要 `examples/`，加上 `jordan-lee` 的卡、档案、CV-INDEX、两份简历、Change Log、岗位和追问卡），再把 `start/` 覆盖上去。这会加一张 **C-006**：它取自旧简历，把 US$200K 写成「合作伙伴市场预算」；已批准的基线里也加了一条引用它的 bullet。0.7.0 及以后的版本，对两份简历各跑一次 `--record all`，当作它们是在这个版本下批准的。`git init` 并提交，方便对比改动。
- **会话 A（纠正）**：全新会话，本人不回答问题，只发上面那条英文消息（$200K 不是预算，是自己设计方案、谈下来的六家赞助）。通过条件：C-006 改成了赞助（事实、数字口径、已批准措辞），只在「禁止改写」里还提到预算；卡上写明方案设计和六笔谈判是本人做的、活动由活动团队执行；回复里说出引用 C-006 的文件（至少有基线）需要复核；已批准的基线没被改动，`cv/reviewed.txt` 里也没有给它新增记录。
- **会话 B（全新会话做定制）**：同一工作区开新会话，用提示词 3 贴上 `job.md`。用上面的命令打分，`--bank` 让打分用会话 A 改过的卡。`gold.json` 禁止出现「budget」，并要求用到 C-006，所以为求稳把这项成果删掉也算不通过。
