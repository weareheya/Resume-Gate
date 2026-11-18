# Roadmap

Known gaps, in the order I plan to fix them. Each item applies to both `en/` and `zh-CN/`. Feedback and PRs welcome.

已知缺口，按计划修复的顺序排列。每一项都要同时改 `en/` 和 `zh-CN/`。欢迎反馈和 PR。

## P0 · A newcomer gets stuck here / 新用户最先会卡住的地方

- [ ] **Step 0: cold start.** Import an existing resume → split it into Claim Cards → make the first baseline. Today the workflow assumes a baseline already exists.
  **Step 0：冷启动。** 导入现有简历 → 拆成 Claim Card → 做出第一份基线。目前流程默认已经有基线。
- [ ] **Where the resume itself lives.** Say where baseline and draft files go, and in what format (Markdown, docx, or a resume tool).
  **简历正文放哪里。** 说明基线和草稿文件放在哪、用什么格式（Markdown、docx 或简历工具）。
- [ ] **Interview prompt for Claim Cards.** A prompt that has the AI interview you and turn raw experience into cards, so you aren't staring at blank templates.
  **Claim Card 采访提示词。** 让 AI 采访你、帮你把经历拆成卡片，不用对着空模板发呆。

## P1 · Clarity / 说清楚

- [ ] **Define claim statuses.** Say that only `Safe to draft` cards may be used, and what to do with `Needs review`.
  **定义 Claim 状态。** 说明只能用 `Safe to draft` 的卡，`Needs review` 的怎么处理。
- [ ] **Copy-paste prompts** for common moments: import my resume, make a version for this JD, self-review this version.
  **可直接复制的提示词**：导入我的简历、给这个 JD 做一版、自审这一版。
- [ ] **`pdf_fill` is macOS only.** Add a cross-platform alternative or document a manual check.
  **`pdf_fill` 只支持 macOS。** 增加跨平台替代方案，或写清楚手动检查办法。

## P2 · Polish / 打磨

- [ ] A filled-in `CV-INDEX` and a full baseline → new-version walkthrough in `examples/`.
  `examples/` 里补一份填好的 `CV-INDEX` 和完整的「基线 → 新版本」对照。
- [ ] Mark the byline table as optional for people with a single name.
  署名表标注为可选，只有一个名字的人可以跳过。
- [ ] Cover letters and LinkedIn: the "Supporting" type exists, but there is no workflow for it yet.
  求职信和 LinkedIn：已有「Supporting」类型，但还没有对应流程。
- [ ] Package the workflow as a reusable Claude skill (`SKILL.md`) once real users have run it.
  等有真实用户跑过后，再把流程打包成可复用的 Claude Skill（`SKILL.md`）。
