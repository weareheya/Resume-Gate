# PROMPTS · 可直接复制的提示词

在对应的时刻把它们贴给 AI。方括号里的内容换成你自己的。

**省钱的用法。** 如果你的工具能选模型：保存 JD、跑脚本、小改动用更快更便宜的模型就够了。定位（S1–S3）、采访你挖证据、自审用最强的模型：弱模型最容易在这几步说大或漏掉缺口。同一个聊天里纠正了很多次之后，开一个新会话：真实情况都在卡上，不会丢。

## 0. 第一次使用

```text
先读 AGENTS.md，再读 docs/WORKFLOW.md。我第一次用这套工具，带我一步一步做 Step 0。先给我现在这份简历做体检报告，开始提问之前先给我看采访计划。每一步开始前，先告诉我这一步要产出什么、需要我提供什么。我说继续之前，不要进下一步。
```

## 1. 给我的简历做体检报告（Step 0，或任何时候）

```text
先读 AGENTS.md 和 docs/REPORT.md。这是我的简历［或：在 evidence/sources/ 里］：

[把简历贴在这里]

做一份简历体检报告［或：针对这份 JD 的岗位匹配报告：贴上 JD］。把 report/template.html 复制到 reports/，只填数据块，然后跑 scripts/report_score.py，给我三行摘要，再用 scripts/report_png.py 把卡片图给我看。先不要写任何 Claim Card。问我要不要一份可以分享的版本。最后列出你建议先采访的 3 项成果，以及每项还缺什么。
```

## 2. 采访我，写一张 Claim Card（Step 0）

```text
先读 evidence/claims/_TEMPLATE.md 和 docs/WORKFLOW.md 里「让采访短一点」那一节。先把计划写进 evidence/INTAKE.md：一共几个问题、大约多久。然后按这种问法采访第 [N] 项成果：［一问一答 / 一项一张表 / 我直接口述］。每个问题前带进度条，材料里已有的不问，最多问 5 个。只问下面这些里还缺的：
- 背景
- 我本人做了什么，团队做了什么
- 每个数字量的是什么（单位、时间窗口、累计 / 单个 / 潜在）
- 我不能说的因果
- 我能怎么证明

不要奉承我，也不要用猜测补空白：我跳过的记在卡上「待补」。我说「好了」或「先到这」时，写出 Claim Card，把要点给我看一眼；我说「对」就标 `Safe to draft`，没确认的、或踩到 docs/WORKFLOW.md「什么算有风险」的，先问我一个问题，问清之前留 `需复核`。`evidence:` 按我能讲多清楚来填；我亲口说的数字标 `✓`，我说「大概」的标 `待核实`。然后更新 evidence/INTAKE.md，两样都给我看。
```

## 3. 给某个岗位做一版

```text
按 docs/WORKFLOW.md 的 S0 到 S6，给这个岗位做一版：

[把 JD 贴在这里]

先把 JD 存进 jobs/，再告诉我：定位（岗位离得远就给几个方案；给了方案就停下来等我选，再往下做）、你选的基线、证据表（每张 Claim Card 用没用、没用的原因）。只能用状态为 `Safe to draft` 的 claim。做到 S7 之前停下，给我看全文、和基线的改动对照、以及 Coverage Report。
```

## 4. 自审一版

```text
对照 docs/REVIEW-CHECKLIST.md 审一遍 cv/resumes/[文件名].md。用表格报告发现的问题，能改的直接改，没法检查的单独列出来。
```

## 5. 检查更新

```text
看看 Resume-Gate 有没有新版本。按 docs/UPDATING.md 的步骤做：对比 VERSION，告诉我改了什么、我需要做什么，我同意后只替换工具文件。永远不要动我自己的文件。
```

## 6. 改前改后海报

```text
用和第一次相同的方式，给 [cv/resumes/文件.md] 再做一次体检，然后用 scripts/report_compare.py 把 reports/[第一份报告] 和新报告做成改前改后海报。生成之前，先把 docs/REPORT.md 里的模块菜单给我看，每个模块写明打算放的文字；只加我勾选的。
```

## 7. 面试追问卡（拿到面试之后）

```text
我拿到了 [岗位编号] 的面试。按 docs/WORKFLOW.md「拿到面试之后：追问卡」，用 interview/_TEMPLATE.md 的格式，给 [cv/resumes/文件.md] 做追问卡，存到 interview/[岗位编号].md。先读这一版用到的每张 Claim Card 和 cv/changelogs/ 里的 Coverage Report，列出你读了哪些 Claim ID。回答只用卡上的事实；卡上没有的放进「面试前要补」，问我，不要编。
```

## 8. 复用已审核的答案

```text
针对 [岗位编号]，先跑 python3 scripts/list_claims.py --answers [岗位编号]。标着「当前」的答案照用。标着「需复核」的，按现在的 Claim Card 重写，存之前先给我看。超出适用范围的答案不要用。
```
