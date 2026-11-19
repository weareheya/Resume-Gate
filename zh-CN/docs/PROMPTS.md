# PROMPTS · 可直接复制的提示词

在对应的时刻把它们贴给 AI。方括号里的内容换成你自己的。

## 0. 第一次使用

```text
先读 AGENTS.md，再读 docs/WORKFLOW.md。我第一次用这套工具，带我一步一步做 Step 0。先给我现在这份简历做体检报告，开始提问之前先给我看采访计划。每一步开始前，先告诉我这一步要产出什么、需要我提供什么。我说继续之前，不要进下一步。
```

## 1. 给我的简历做体检报告（Step 0，或任何时候）

```text
先读 AGENTS.md 和 docs/REPORT.md。这是我的简历［或：在 evidence/sources/ 里］：

[把简历贴在这里]

做一份简历体检报告［或：针对这份 JD 的岗位匹配报告：贴上 JD］。把 report/template.html 复制到 reports/，只填数据块，然后跑 scripts/report_score.py，给我三行摘要。先不要写任何 Claim Card。最后列出你建议先采访的 3 项成果，以及每项还缺什么。
```

## 2. 采访我，写一张 Claim Card（Step 0）

```text
先读 evidence/claims/_TEMPLATE.md 和 docs/WORKFLOW.md 里「让采访短一点」那一节。先把计划写进 evidence/INTAKE.md：一共几个问题、大约多久。然后按这种问法采访第 [N] 项成果：［一问一答 / 一项一张表 / 我直接口述］。每个问题前带进度条，材料里已有的不问，最多问 5 个。只问下面这些里还缺的：
- 背景
- 我本人做了什么，团队做了什么
- 每个数字量的是什么（单位、时间窗口、累计 / 单个 / 潜在）
- 我不能说的因果
- 我能怎么证明

不要奉承我，也不要用猜测补空白：我跳过的记在卡上「待补」。我说「好了」或「先到这」时，写出状态为 `需复核` 的 Claim Card，更新 evidence/INTAKE.md，两样都给我看。
```

## 3. 给某个岗位做一版

```text
按 docs/WORKFLOW.md 的 S1 到 S6，给这个岗位做一版：

[把 JD 贴在这里]

先告诉我：岗位类型、你选的基线、你读了哪些 Claim ID。只能用状态为 `Safe to draft` 的 claim。做到 S7 之前停下，给我看全文、和基线的改动对照、以及 Coverage Report。
```

## 4. 自审一版

```text
对照 docs/REVIEW-CHECKLIST.md 审一遍 cv/resumes/[文件名].md。用表格报告发现的问题，能改的直接改，没法检查的单独列出来。
```

## 5. 检查更新

```text
看看 Resume-Gate 有没有新版本。按 AGENTS.md 里「更新工具」的步骤做：对比 VERSION，告诉我改了什么、我需要做什么，我同意后只替换工具文件。永远不要动我自己的文件。
```
