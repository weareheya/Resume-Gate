# REPORT · 简历体检报告与岗位匹配报告

一份带分数的可视化简历报告。AI 只填数据，计数和算分都由模板完成，所以同一份简历不管哪个 AI 来填，分数都一样。

- **模板**：[`report/template.html`](../report/template.html)。用浏览器打开，能看到一份虚构的示例。
- **产出**：复制到 `reports/<日期>-checkup.html`（岗位匹配报告用 `-<岗位编号>.html`），替换里面的数据块，用浏览器打开。要文件的话，在浏览器里打印成 PDF。
- **一个文件，两种视图。** *完整报告*给自己看：每条 bullet、每条建议都在。*分享卡*（点顶部的按钮，或在地址后加 `#share`）是一张适合截图发出去的竖版卡片：分数、分档、各维度条形图，附 Resume-Gate 的链接。姓名、公司、目标岗位和 bullet 原文都会隐藏；想在卡上署名，才在 `meta` 里填 `"share_name"`。
- **存成图片。** 很多对话窗口和预览窗口不运行 JavaScript，报告文件在那里只看得到水印。`python3 scripts/report_png.py reports/<文件>.html` 用你电脑上已有的 Chrome、Edge 或 Brave 把分享卡存成 `<文件>-card.png`（1080 px 宽，可以直接发）；加 `--full` 存整份报告 `<文件>-full.png`，只给自己看。`-share.html` 和海报也能用。
- **分享版。** 完整报告的文件里仍然存着全部信息，绝不能直接发出去。`python3 scripts/report_share.py reports/<文件>.html` 会生成 `<文件>-share.html`：分数一样，没有任何隐私文字，打开就是分享卡。加 `--name "…"` 可以在卡上署名。

## 分享：只有分数，或加上本人勾选的模块

分享卡和海报默认**只显示分数和各维度条形图**。生成之前，把下面的菜单给本人看，每个模块写明打算放的具体文字，只加本人勾选的：

| 模块 | 参数 | 显示什么 | 规矩 |
|---|---|---|---|
| 署名 | `--name` | 卡上的名字 | 本人要求才加 |
| 一句话定位 | `--headline` | 一行定位 | 给 3 个候选，每个都要来自 `Safe to draft` 的 Claim Card。具体胜过夸张：「把渠道伙伴从 12 家带到 40 家」好过「BD 达人」 |
| 目标方向 | `--target` | 岗位类型，例如「渠道 BD」 | 只写类型，不写公司 |
| 关键词标签 | `--tag`（最多 5 个） | 关键词 | 从 Claim Card 里提炼的短名词：证据撑得住的技能或领域 |
| 亮点 | `--highlight`（最多 2 条） | 一句话亮点 | 来自卡片，去掉公司名和客户名 |

所有模块都不能出现公司名、客户名，也不能写证据撑不住的内容。本人想要活泼一点的定位也可以，只要卡片支持。

- **分享卡**：`python3 scripts/report_share.py reports/<文件>.html [模块]`
- **改前改后海报**：`python3 scripts/report_compare.py reports/<改前>.html reports/<改后>.html [模块]`。两份报告用同一个公式算分；海报显示两个分数、每个维度的改前改后，以及两份报告的日期。两份报告模式不同时，只比较共有的维度，并在海报上注明。示例：[`examples/jordan-lee/reports/`](../examples/jordan-lee/reports/)。

## 两种模式

| 模式 | 什么时候用 | 维度 |
|---|---|---|
| **简历体检** | Step 0，或任何时候，不针对具体岗位 | R1 ~ R5 |
| **岗位匹配** | 针对一份 JD，通常在 S3 或 S6 之后 | R1 ~ R5，加 J1 ~ J3 |

任何维度都可以在数据块里关掉（`"dims"`）。关掉的不计分，其余权重按比例放大，总分仍然是 100。

## 维度

AI 给每条 Experience bullet 标「是 / 否」，并跑一遍结构检查。模板负责数数。

| 编号 | 维度 | AI 标什么 | 得分 | 权重 |
|---|---|---|---|---|
| R1 | 结果 | 这条写了做出了什么结果，而不只是做了什么 | 标「是」的条数 / 全部 bullet | 25 |
| R2 | 数字 | 至少有一个数字：数量、百分比、金额、时间、规模 | 标「是」的条数 / 全部 bullet | 20 |
| R3 | 动作开头 | 以说得出你做了什么的行动动词开头。不算：「Responsible for」「Duties included」「Worked on」，以及「Helped」「Assisted」「Supported」「Participated in」这类弱动词 | 标「是」的条数 / 全部 bullet | 15 |
| R4 | 具体 | 没有空话：「results-oriented」「passionate」「various」「etc.」「team player」 | 标「是」的条数 / 全部 bullet | 10 |
| R5 | 结构 | 下面的检查项 | 通过 / 检查 | 15 |
| J1 | JD 覆盖 | JD 的每条核心要求：直接、部分，还是没有证据。硬性要求标 `"gate": true`，没有直接满足的会由 `report_score.py` 列出。岗位匹配报告里 J1 一定计分：没填要求就按 0 算，漏掉 JD 不会让分数变高 | （直接 + ½ × 部分）/ 要求数 | 30 |
| J2 | 位置 | 已覆盖的要求，最强证据放在 Summary 或某段经历的第一条 | 标「是」的条数 / 已覆盖的要求 | 15 |
| J3 | 用词 | 证据支持的 JD 关键词里，简历用上了几个 | 用上的 / 有证据支持的 | 10 |

**判例**：拿不准时照这张表标，换一个 AI 来标也应该是同一个结果。

| 维度 | 算「是」 | 算「否」 |
|---|---|---|
| R1 结果 | Grew active partners from 12 to 40.（写了做成了什么） | Managed relationships with channel partners.（只写了在做什么） |
| R1 结果 | Cut onboarding from 3 weeks to 4 days.（没有营收数字也算，结果是时间缩短） | Launched a partner portal.（上线是动作；写了「之后发生了什么」才算） |
| R2 数字 | Ran four webinars with 380 registrants. | Ran several webinars with strong turnout. |
| R2 数字 | Led a team of 6 across 3 markets.（规模也算数字） | Led a cross-functional team.（没有任何数量） |
| R3 动作开头 | Negotiated / Built / Rebuilt / Launched … | Responsible for… / Worked on… / Duties included… |
| R3 动作开头 | Built the pitch deck that won the account.（写出你具体做了什么） | Helped / Assisted / Supported / Participated in / Involved in / 协助 / 参与…（弱动词：看不出你做了哪一部分） |
| R4 具体 | Translated the roadmap into launch messaging for 3 markets. | Drove various initiatives to improve results, etc. |
| R4 具体 | Reframed the pitch around player-owned AI agents. | Passionate, results-oriented team player.（形容自己，不是事实） |

弱动词标「否」，不等于这件事不能写：真的是配合角色，就写你配合的那一块具体做了什么。修改建议照这个方向给，不替本人夸大成主导。

**R5 结构检查**：Summary 不超过 4 行 · 栏目名标准（Summary、Experience、Education、Skills）· 最近两段经历各 2 ~ 5 条 bullet，更早的 1 ~ 3 条就够（早年、短期的经历只写 1 条是正常写法） · 没有超过 3 行的 bullet · 联系方式干净（不带 `https://`，链接可读）· 单栏，文字不藏在图片或表格里（知道的话；不知道就不检查这项）。

**分档**：85 ~ 100 很强 · 70 ~ 84 扎实 · 55 ~ 69 能用，但在丢分 · 55 以下 需要重写。

## 面试底气（不计分）

总分看的是简历读起来怎么样。证据不改变这一点，所以不计分。它决定的是另一件事：面试官追问「这个数字怎么来的」「哪部分是你做的」时，你接不接得住。报告把它单独放在一个面板里。

AI 给每条 bullet 标 `sourced`，并把对应的 Claim ID 写进 `claims`，例如 `"claims": ["C-004", "C-012"]`。简历上不会印 Claim ID，所以这一项要对照证据库（`evidence/claims/`，或你存证据的地方）。卡号不要写进 `where`。

| `sourced` | 意思 | 显示为 |
|---|---|---|
| `true` | 有一张 `Safe to draft` 的 Claim Card 覆盖整条 | ✓ 已确认 |
| `"partial"` | 找到了卡，但还在复核，或只覆盖这条的一部分 | ½ 复核中或部分 |
| `false` | 还没有卡 | – 还没有卡 |

**第一次体检、还没做 Step 0：** 还没有卡，每条都标 `false`、`claims` 留空。面板会显示「第二阶段 · 做完 Step 0 采访后解锁」，逐条标注表也不显示证据这一列。总分不受影响。有卡但 AI 读不到时，在摘要里说明。

## AI 的规矩

- **只标注，不打分。** 填每条 bullet 的是 / 否和检查结果。不要自己写总分或百分比，由模板来算。
- **每个标注都能核对。** 报告会逐条列出 bullet 和它的标注，本人能看到每个维度为什么是这个分。
- **亮点、修改建议和缺口，只用简历或 Claim Card 里已有的事实。** 修改建议绝不加新事实或新数字。需要简历里没有的信息时，写明要问本人什么。
- **修改建议最多 5 条**，最重要的在前。
- 然后跑 `python3 scripts/report_score.py reports/<文件>.html`，在对话里引用它算出的分数，给三行摘要：分数和分档、最强的一点、第一条修改建议。数据块里的 `summary` 不写分数，页面上会显示。
- **在对话里给本人看报告。** 跑 `python3 scripts/report_png.py reports/<文件>.html`，把卡片图片显示出来（Claude Code 里读一下这张 PNG，它就会出现在对话里；别的工具给出路径）。找不到浏览器时，给 HTML 路径，请本人用浏览器打开。
- **第一次体检、还没有 Claim Card：用两行说明第二阶段是什么。** 第二阶段是就最强的 3 项成果做一次简短采访，写成 Claim Card。做完解锁「面试底气」：面试官追问「数字怎么来的」「哪部分是你做的」时，哪些经历你接得住。它不计分，不影响简历的分数。
- **然后问一次：「要不要出一份可以分享的版本？」** 本人说要，先给上面的模块菜单，再带上本人勾选的模块跑 `scripts/report_share.py`，把 `-share.html` 的路径给本人，并提醒只分享这个文件或分享卡截图，不要发完整报告。

## 这个分数是什么，不是什么

这是 Resume-Gate 自己的标准，依据 Harvard 就业指导中心的简历指南（行动动词、量化结果、不写职责描述、不用空泛形容词）和常见的 ATS 建议（标准栏目、单栏）。它只给读者在纸面上看得到的东西打分；背后的证据准备得怎么样，单独放在「面试底气」里。它**不是**招聘方的评分，也不预测面试率。适合用来比较同一份简历前后几个版本的变化。
