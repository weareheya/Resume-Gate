# Evals

Maintainer tools for checking that a change to the kit (a prompt, a rule, a script, or a new model) makes resumes better, not just different. Users of the kit don't need this folder: it isn't part of the `en/` or `zh-CN/` downloads.

[中文说明在下面](#中文说明)

## What's here

| Path | What it is |
|---|---|
| `cases/<case>/job.md` | A fictional job posting, in the kit's `jobs/` format, with requirements R1, R2… |
| `cases/<case>/gold.json` | What a good answer must and must not do for that job (see below) |
| `cases/<case>/reference/` | One answer that scores 100%: a resume and its change log. A floor to compare against, not the only right answer |
| `score.py` | Scores one resume (and optionally its change log) against a case |
| `blind.py` | Prepares an A/B/C blind comparison for human raters |
| `test_evals.py` | Checks the cases, the scorer and the blind tool; runs in CI |
| `RESULTS.md` | What each eval run found and what changed because of it |

All cases use the evidence bank in `en/examples/jordan-lee`, so anyone can rerun them. Each one tests a different trap:

| Case | Job | The trap |
|---|---|---|
| `channel-bd` | Channel Sales Manager | Asks for a revenue quota; there is pipeline evidence but no closed revenue |
| `product-manager` | Associate PM | A stretch role: don't say "built" or "launched" the portal (engineering did), don't claim roadmap ownership nobody asked about |
| `customer-success` | Partner Success Manager | Asks for onboarding time and cost savings, which were never measured; webinar registrants aren't attendees |

## gold.json

| Field | Meaning | Gate? |
|---|---|---|
| `bank` | Evidence bank the case uses, from the repo root | |
| `must_use` | Cards a good answer cites. Missing one is underselling (D-019). A card counts only when its ID is tagged on a line a reader sees (or on the line right under a wrapped bullet), not when it's named in a note | yes: critical recall must be 100% |
| `should_use` | Cards that usually help. Reported as a score | no |
| `must_not_use` | Cards that can't go in a resume (e.g. `Needs review`) | yes |
| `forbidden` | Regexes for overselling, matched case-insensitively against what a reader sees (no front matter, no comments) | yes |
| `gaps` | Expected kind for each requirement: Direct, Transferable or combined, Not found yet, Buildable, Hard gap. Give a list when more than one is defensible (e.g. `["Hard gap", "Not found yet"]`: Not found yet is right if the user hasn't been asked yet) | no: reported as accuracy, since reviewers can reasonably differ |

`score.py` also runs the kit's `check_claims.py` on the resume (any error fails the case) and, given a change log, checks that its evidence table lists every card in the bank. It fails closed: if `check_claims.py` crashes or ends without its verdict line, the score is "could not run" (exit 2), never a pass.

## Running it

```bash
# score one answer
python3 evals/score.py evals/cases/product-manager path/to/resume.md --changelog path/to/changelog.md
# all references (should all PASS)
for c in evals/cases/*/; do python3 evals/score.py "$c" "$c/reference/resume.md" --changelog "$c/reference/changelog.md"; done
python3 evals/test_evals.py
```

To evaluate a change: for each case, start a fresh session in a copy of the example (`en/examples/jordan-lee` with the kit around it), save the case's `job.md` as `jobs/<id>.md`, ask for a tailored resume with prompt 3, and score what comes back, once with the old kit and once with the new one. Run each side at least three times: answers vary between runs, so compare the pass rate and the average scores, not a single run.

## Blind A/B/C review

Scores catch overselling and missing evidence. Whether a resume is *persuasive* still needs people. **Do a blind read in every eval round**, at least on the case the change touches: in round 2 the scores were perfect on both sides and only the blind read showed that the new version undersold (RESULTS.md).

1. Pick the versions to compare for one job, for example the old kit's answer (A), the new kit's (B) and the user's own resume (C).
2. `python3 evals/blind.py evals/runs/<date>-<case> a.md b.md c.md`. It strips Claim IDs, notes and front matter, shuffles the order, and writes `A.md`, `B.md`, `C.md`, `rating-sheet.md` and `key.json`. (`evals/runs/` is ignored by git.)
3. Give each rater the job posting, the lettered files and the rating sheet, but not `key.json`. Two or three raters is enough; recruiters or hiring managers in that field are best.
4. Each rater scores fit, strongest evidence up front, believability, and "would you interview?", then ranks the versions.
5. `python3 evals/blind.py --reveal evals/runs/<date>-<case>` and compare. A new kit version should win or tie on fit, and must not lose on believability.

Use only fictional or consented resumes: rating sheets get passed around.

## Adding a case

Write `job.md` with numbered requirements and `gold.json`, then a reference answer that passes. Base each `forbidden` pattern on a card's "Don't rephrase as" or attribution notes, so the case tests a real way of overselling, not a style preference (D-017). Add the case to the table above.

---

## 中文说明

这个文件夹是维护者用的：改了提示词、规则、脚本，或换了模型之后，用它确认简历是真的变好了，而不只是变了。普通用户用不到它，它也不在 `en/`、`zh-CN/` 的下载包里。

- `cases/<case>/`：一个虚构岗位（`job.md`）、标准答案要求（`gold.json`）和一份 100 分的参考答案（`reference/`）。三个案例都用 `en/examples/jordan-lee` 的证据库，各自考一个陷阱：渠道销售岗要营收指标但只有 pipeline；产品岗不能说门户是自己「搭建 / 上线」的，也不能声称管过路线图；客户成功岗要入驻时间和成本节省，但从来没量过，webinar 报名人数也不是到场人数。
- `score.py`：先跑工具里的 `check_claims.py`（有错误就不通过；它崩溃或没跑完时判为「跑不了」，绝不算通过），再算关键卡召回率（必须 100%，漏用就是写低了自己；只有标在读者看得到的那一行上的卡才算用过，写在备注里的不算）、建议卡召回率、不能用的卡、夸大措辞、缺口分类准确率，以及证据表是否列了每张卡。缺口分类和建议卡只打分不卡关，因为合理的人也会有不同判断。
- `blind.py`：A/B/C 盲评。去掉 Claim ID、注释和 front matter，打乱顺序，生成评分表；`key.json` 等所有人评完再看（`--reveal`）。新版本在「匹配度」上应该赢或打平，在「可信度」上不能输。
- 每边至少跑三次再比较，因为每次生成的结果会不一样。
- **每一轮评测都要做盲评**，至少做改动涉及的那个案例：第二轮两边分数都满分，只有盲评发现新版写低了自己（RESULTS.md）。
- 加新案例时，`forbidden` 要依据卡片上的「不要改写成」或归属说明，考的是真实的夸大方式，而不是文风偏好（D-017）。
