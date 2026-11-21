# Resume-Gate

**English** · [简体中文](#简体中文)

[Get started](#get-started) · [See a full example](en/examples/jordan-lee/README.md)

> Use AI to tell the right story about your career: one that shows how you make sense of your own experience, and that you can still defend in the interview. Every line has a source, every version can be traced, and every change goes through you.

**Your career story is you.** How you tell your experience shows who you are and how you've digested what you've done: what you chose to own, what you learned, what you'd stand behind. An AI can polish that story or quietly replace it with a more impressive one that isn't yours. Resume-Gate keeps the story yours: it starts from facts you confirmed, and every change goes through you.

**A faked story may get you the interview; the cost can be one you can't undo.** An AI can hallucinate: make a number bigger, a role broader, or an outcome sound finished when it wasn't, or invent a detail that never happened. It reads well on paper. Then an interviewer asks "how was that counted?" or "what did you do yourself?", and a line you can't back up can cost more than the whole resume gained and damage your credibility. Resume-Gate works backwards from that moment and does its best to keep AI hallucination off your resume: every line traces to a fact you confirmed, the scripts check sources and numbers, and each Claim Card records how a number was counted, what was yours versus the team's, and wording you can't use.

**The right story isn't the smallest one.** Playing it safe is a failure too. Within what the facts support, the kit pushes for the strongest defensible wording: lead with the result you can back, and word shared work as collaboration. Before it drops or weakens anything the AI asks follow-up questions, and it checks every card against every job, which helps bring out strengths you might have overlooked. Before an interview, follow-up cards list the questions each bullet is likely to draw, with answers taken only from your cards.

**Every tool has limits; know Resume-Gate's before you start.**

- It can't guarantee an interview or an offer.
- It does its best to catch AI mistakes, but can't catch them all. The scripts check sources, numbers and some known risky wording. A wrong attribution or an exaggeration they don't recognize can still get through, so read every change before you approve it.
- It is only as accurate as the facts you confirm. If a Claim Card is wrong, everything built from it is wrong too.
- Whether a story persuades is a human judgment. The scripts don't judge it, and the blind reads in our own tests are done by an AI, not by real hiring managers.
- What the AI finds and how well it words things depend, to a degree, on the model you use, your materials and your answers.
- What you give the AI goes to that AI service (see Privacy below).

A resume workflow for a long job search, where you tailor many versions over weeks or months: **evidence bank → baseline resume → per-job delta → AI self-review → your sign-off → freeze → interview prep**. It's docs, templates, and a few small scripts, and it isn't tied to any AI or resume tool.

**It's for you if** you use AI to tailor resumes and have seen it drop results you already confirmed, inflate a number, or quietly water down your strongest experience. **It's probably overkill if** you need one resume, once.

**Why not just ask an AI?** Any AI can make a resume read better. What it can't know is how each number was counted, which part was yours, and which line will get you stuck when an interviewer digs in. Only you know that. Resume-Gate writes it down once, as Claim Cards, and everything after grows from the same facts: every resume version, every checkup, and the follow-up cards you read before each interview. A fresh chat may not reliably carry over what you've confirmed; this folder keeps it in files.

![Resume-Gate overview: one fact, one card; every version and every interview traces back](assets/overview-en.svg)

**New in 0.7.0 (2026-11-21):** correct a fact once. When you fix a Claim Card, the scripts flag every resume, follow-up card and saved answer that used the old version, so a corrected error doesn't come back unnoticed. These are reminders for you to review, not a guarantee about what the AI will write; sent resumes stay unchanged. You can also accept or reject the AI's proposed changes one by one, and keep answers you've approved for reuse (`interview/answers/`). [Details](en/CHANGELOG.md)

**New in 0.6.0 (2026-11-20):** your cards and resumes stay out of Git by default; quick edit / tailor / finalize modes, so a small fix doesn't run the whole pipeline; layout check works on Windows and Linux (you confirm the last page); a lighter evidence table that the script checks; hard requirements shown on the report. No hard rule was removed. [Details](en/CHANGELOG.md)

**New in 0.5.0 (2026-11-20):** sent resumes can be frozen (`scripts/freeze.py`), and the repo has an [eval set](evals/README.md) with blind A/B/C review to check that kit changes make resumes better. 0.4.0 made the kit check what a resume leaves out, not only what it gets wrong; 0.3.0 made the evidence checks much harder to slip past. [All changes](en/CHANGELOG.md)

## What's inside

| Feature | What it does | English | 中文 |
|---|---|---|---|
| Claim Cards | One file per accomplishment: facts, what each number measures, your share vs the team's, wording you can't use | [template](en/evidence/claims/_TEMPLATE.md) · [example](en/examples/jordan-lee/evidence/claims/C-001.md) | [模板](zh-CN/evidence/claims/_TEMPLATE.md) · [示例](zh-CN/examples/jordan-lee/evidence/claims/C-001.md) |
| Workflow | Step 0 (cold start) and seven steps per job, each with an output you must show | [WORKFLOW](en/docs/WORKFLOW.md) | [WORKFLOW](zh-CN/docs/WORKFLOW.md) |
| Probing questions | Seven questions the AI asks before it drops or weakens anything | [WORKFLOW](en/docs/WORKFLOW.md#probing-questions) | [追问清单](zh-CN/docs/WORKFLOW.md#追问清单) |
| Decision register | 20 starter rules, from "don't cut strong results" to "pick the strongest defensible wording" | [DECISIONS](en/docs/DECISIONS.md) | [DECISIONS](zh-CN/docs/DECISIONS.md) |
| AI self-review | Facts, writing, layout, and handoff checks the AI runs before you see anything | [REVIEW-CHECKLIST](en/docs/REVIEW-CHECKLIST.md) | [自审清单](zh-CN/docs/REVIEW-CHECKLIST.md) |
| Lessons | Real process mistakes and the guardrail each one led to | [LESSONS](en/docs/LESSONS.md) | [LESSONS](zh-CN/docs/LESSONS.md) |
| Follow-up cards | Before an interview: the questions each bullet is likely to draw, answers that hold up, and what not to say, all from your Claim Cards | [WORKFLOW](en/docs/WORKFLOW.md#after-you-get-an-interview-follow-up-cards) · [example](en/examples/jordan-lee/interview/ACME-01.md) | [WORKFLOW](zh-CN/docs/WORKFLOW.md#拿到面试之后追问卡) · [示例](zh-CN/examples/jordan-lee/interview/ACME-01.md) |
| Prompts | Copy-paste prompts for the first session, Step 0, a new job, self-review, and interview prep | [PROMPTS](en/docs/PROMPTS.md) | [PROMPTS](zh-CN/docs/PROMPTS.md) |
| Checkup report | A scored, visual report on a resume, on its own or against a JD, plus a share card | [REPORT](en/docs/REPORT.md) · [sample](en/report/template.html) | [REPORT](zh-CN/docs/REPORT.md) · [示例](zh-CN/report/template.html) |
| Scripts | `check_claims.py` (every bullet has a source), `report_score.py` (report score), `report_png.py` (report as an image) and `pdf_fill.swift` (pages are full) | [scripts](en/scripts/) | [scripts](zh-CN/scripts/) |
| Updates | Your rules live in their own file, so updating never overwrites them; one prompt checks for a new version | [CHANGELOG](en/CHANGELOG.md) | [更新记录](zh-CN/CHANGELOG.md) |
| Cases | Ten made-up before-and-after cases, one or two rules each | [cases](en/examples/cases.md) | [案例](zh-CN/examples/cases.md) |

**It builds up as you use it.** The more you use it, the more your evidence bank knows about your experience. The follow-up questions and capability facets on each card can surface strengths you hadn't fully put into words, and each new job can draw on a different part of the same facts. Everything you've confirmed is kept, and when you correct something, what depended on it is flagged. How much it surfaces still depends on your answers and the AI you use.

## Get started

Resume-Gate is a folder of files that an AI reads and follows. Setup is three steps: pick an AI tool, get the files, start the first session.

### 1. Pick where to run it

It works best with an AI that can open and edit files in a folder on your computer.

| If you… | Use | Setup guide |
|---|---|---|
| don't use a terminal (most people) | **Claude desktop app**, Code tab | [Download](https://claude.com/download) · [Claude Code docs](https://code.claude.com/docs/en/overview) |
| already use a terminal | **Claude Code** or **Codex** | [Claude Code quickstart](https://code.claude.com/docs/en/quickstart) · [Codex quickstart](https://developers.openai.com/codex/quickstart) |
| already use an AI code editor | **Cursor** or similar | [Download Cursor](https://cursor.com/download) |
| only use a chat AI | a **Claude Project** or ChatGPT Project | [Claude Projects](https://support.claude.com/en/articles/9517075-what-are-projects). Works, but the scripts won't run, so their checks are done by hand |

Most of these tools need a paid plan or limit what a free one can do; check each setup guide for current terms. Claude Code and Codex read the kit's `AGENTS.md` on their own. In other tools, tell the AI to read it first.

**Using Codex?** It runs without network access by default and asks before any download ([why](https://developers.openai.com/codex/agent-approvals-security)). The easy way: download the zip in step 2 yourself, then open the unzipped folder in Codex as a local project. No GitHub connection needed.

### 2. Get the files

Pick **one** kit and download it. No Git and no GitHub account needed.

- **English**: [resume-gate-en.zip](https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-en.zip)
- **简体中文**: [resume-gate-zh-CN.zip](https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-zh-CN.zip)

Unzip it and open the folder in your AI tool. Rename the folder if you like.

**Prefer to let the AI do it?** Open an empty folder in your AI tool and paste:

```text
Set up Resume-Gate in this folder. Download https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-en.zip (use resume-gate-zh-CN.zip if I want Chinese), unzip it, copy everything inside its resume-gate-en/ folder into this folder, and delete the zip and the extra folder. It's a public download: no GitHub account or connector is needed. If you need my approval to use the network, ask once for this download. Then check that AGENTS.md is here and run git init if git is installed.
```

**With Git:**

```bash
git clone https://github.com/weareheya/Resume-Gate.git
mkdir my-job-search
cp -R Resume-Gate/en/. my-job-search/      # or Resume-Gate/zh-CN/.
cd my-job-search && git init
```

### 3. Start the first session

Open the folder in your AI tool and say **"start"**. Any first message works: the AI checks where you are and walks you through Step 0, starting with a scored checkup of your current resume. In Claude Code you can also type `/start`. If your tool doesn't read `AGENTS.md` by itself, paste prompt 0 from [PROMPTS](en/docs/PROMPTS.md#0-first-session). The full walkthrough is in the kit's quick start: [en/README.md](en/README.md#quick-start) · [zh-CN/README.md](zh-CN/README.md#快速开始).

### What else you might need

| For | Needed | How to get it |
|---|---|---|
| `check_claims.py` (sourcing check) | Python 3 | macOS and Linux usually have it. Windows: [python.org](https://www.python.org/downloads/), and tick "Add python.exe to PATH" during install. On Windows the command is `python`, not `python3` |
| `pdf_fill.swift` (layout check) | macOS + Xcode command line tools | Run `xcode-select --install` once. Not on a Mac? Check the page count and last page of the PDF by eye |
| Version history and backup (optional) | Git, a **private** GitHub repo | [Git](https://git-scm.com/downloads) or [GitHub Desktop](https://desktop.github.com/download/) if you'd rather not use a terminal; [create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) and set it to Private |

Not sure about any of this? Ask the AI tool you picked in step 1. It can check what's installed and walk you through the rest.

**Tools are your choice.** Evidence can live in Markdown files or a database such as Notion; layout can happen in [Reactive Resume](https://rxresu.me) (open source, with MCP), in Word, or in a PDF your AI generates. See [Tools: your choice](en/README.md#tools-your-choice).

**Privacy:** your evidence bank will hold your real work history, so keep your working copy private. Copy a kit into your own folder or private repo; don't fork this repo and fill it in publicly. What is and isn't covered:

| Where | What you get |
|---|---|
| Files on your computer | They stay in your folder |
| Git | `.gitignore` keeps your cards, resumes, jobs, interview notes, reports and `docs/MY-DECISIONS.md` out by default. It's a safety net, not a guarantee: check what you commit |
| The AI you use | Whatever you paste or let it read goes to that AI service, under its data policy. Resume-Gate doesn't run a model locally |
| Outside resume tools | Only what you choose to upload, under their own policy |

**Changing the kits?** Edit both `en/` and `zh-CN/`, then run `python3 tools/check_sync.py`. It catches files, IDs or headings that differ between them, and also checks that `VERSION`, the top CHANGELOG entry, the root README's "New in" line and the rule counts all agree, so a release can't ship with stale numbers.

---

## 简体中文

[开始使用](#开始使用) · [查看完整示例](zh-CN/examples/jordan-lee/README.md)

> 用 AI 讲对你的职业故事：它体现你如何消化自己的经历，也经得起面试的追问。每句话有出处，每一版可追溯，每处改动都经过你。

**你的职业故事就是你。** 你怎么讲自己的经历，体现你是谁、你如何消化自己做过的事：你认领什么、学到什么、哪些话你敢担保。AI 可以把这个故事打磨得更好，也可能悄悄换成一个更漂亮、却不是你的故事。Resume-Gate 让故事保持是你的：从你确认过的事实出发，每处改动都经过你。

**编出来的经历也许能换到面试，代价却可能无法挽回。** AI 会产生幻觉：把数字写大、把职责写宽、把没做完的事写成已经做成，甚至编出根本没发生过的细节。纸面上很好看，然后面试官问「这个数字怎么算的？」「你自己具体做了什么？」，一句答不上来的话，损失可能比整份简历带来的好处还大，还会伤到你的可信度。Resume-Gate 从这一刻倒推，尽力避免 AI 幻觉进入你的简历：每句话都要追溯到你确认过的事实，脚本检查出处和数字，每张 Claim Card 记着数字怎么算的、哪部分是你做的哪部分是团队的、哪些说法不能用。

**对的故事不是最保守的故事。** 一味保守也是失败。在事实支持的范围内，工具包追求最强又站得住的写法：把你能证明的成果放前面，共同完成的事写成协作。AI 在删掉或写弱任何内容之前会先追问，每个岗位都把每张卡过一遍，这样可以帮助挖掘你可能忽略的优势。面试前，追问卡会列出每条经历可能被问到的问题，答案只取自你的卡片。

**再好的产品也有局限，用之前请先了解 Resume-Gate 的局限。**

- 它不能保证你拿到面试或 offer。
- 它尽力抓住 AI 的错误，但不可能全部抓住。脚本检查出处、数字和一些已知的高风险措辞；脚本认不出来的错误归属或夸大，仍可能漏过去，所以每处改动你批准之前都要自己读一遍。
- 它的准确度取决于你确认过的事实。Claim Card 写错了，由它生成的一切都会跟着错。
- 故事打不打动人，是人的判断。脚本不判断，我们自己测试里的盲评也是由 AI 来读，不是真正的招聘经理。
- AI 能挖出什么、写得多好，在一定程度上取决于你用的模型、你的材料和你的回答。
- 你交给 AI 的内容会交给那家 AI 服务（见下面的隐私说明）。

一套给长期求职用的简历工作流。几周、几个月、几十版改下来不乱：**证据库 → 基线 → 按岗位改 Delta → AI 自审 → 本人审核 → 冻结 → 面试准备**。文档 + 模板 + 几个小脚本，不绑定任何 AI 或简历工具。

**适合**：用 AI 改过简历，遇到过它把确认过的成果弄丢、把数字写大，或者把最强的经历悄悄写弱。**用不上**：只要一份简历，投一次。

**为什么不直接让 AI 改？** 随便一个 AI 都能把简历改得更好看。它不知道的是：这个数字当时怎么算的，哪部分是你做的，哪句话一被追问就会卡壳。这些只有你知道。Resume-Gate 把它们写进证据库，只写一次，之后的一切都从同一套事实里长出来：每一版简历、每一次体检，还有每场面试前的追问卡。新开一个对话，AI 不一定可靠地记得你确认过的事；这个文件夹把它们存在文件里。

![Resume-Gate 总览：事实只写一次，简历和面试都从这里来](assets/overview-zh.svg)

**0.7.0 新增（2026-11-21）：** 事实改一次就够。你纠正一张 Claim Card 后，脚本会标出用过旧版本的每份简历、追问卡和已存回答，纠正过的错误不会悄悄回来。这是提醒你去复核，不是保证 AI 以后一定不会写错；已投递的简历保持原样。AI 提出的修改还能逐条接受或拒绝，你批准过的回答可以留着复用（`interview/answers/`）。[详情](zh-CN/CHANGELOG.md)

**0.6.0 新增（2026-11-20）：** 卡片和简历默认不进 Git；分快改 / 定制 / 定稿三种模式，小改动不再走整套流程；Windows 和 Linux 上也能做排版检查（由你确认最后一页）；证据表更轻，并由脚本把关；报告上标出硬性要求。没有删掉任何硬规则。[详情](zh-CN/CHANGELOG.md)

**0.5.0 新增（2026-11-20）：** 已投递的简历可以冻结（`scripts/freeze.py`），仓库里加了[评测集](evals/README.md)和 A/B/C 盲评，用来确认工具的改动真的让简历变好。0.4.0 开始查漏写了什么，0.3.0 让证据检查更难被绕过。[全部更新记录](zh-CN/CHANGELOG.md)

## 里面有什么

| 功能 | 做什么 | 中文 | English |
|---|---|---|---|
| Claim Card | 一个成果一个文件：事实、每个数字量的是什么、你的部分和团队的部分、不能用的说法 | [模板](zh-CN/evidence/claims/_TEMPLATE.md) · [示例](zh-CN/examples/jordan-lee/evidence/claims/C-001.md) | [template](en/evidence/claims/_TEMPLATE.md) |
| 工作流 | Step 0（冷启动）和每个岗位的七步，每步都有必须拿得出的产出 | [WORKFLOW](zh-CN/docs/WORKFLOW.md) | [WORKFLOW](en/docs/WORKFLOW.md) |
| 追问清单 | AI 在删掉或写弱任何内容之前要问的 7 个问题 | [追问清单](zh-CN/docs/WORKFLOW.md#追问清单) | [Probing questions](en/docs/WORKFLOW.md#probing-questions) |
| 决策登记簿 | 20 条起步规则，从「不随意删强成果」到「选最强又站得住的写法」 | [DECISIONS](zh-CN/docs/DECISIONS.md) | [DECISIONS](en/docs/DECISIONS.md) |
| AI 自审 | 给你看之前，AI 先过一遍事实、写法、排版和交付格式 | [自审清单](zh-CN/docs/REVIEW-CHECKLIST.md) | [REVIEW-CHECKLIST](en/docs/REVIEW-CHECKLIST.md) |
| 失误记录 | 真实踩过的过程性错误，以及每条带来的防线 | [LESSONS](zh-CN/docs/LESSONS.md) | [LESSONS](en/docs/LESSONS.md) |
| 面试追问卡 | 面试前：每条经历最可能被问什么、怎么答站得住、哪些话别说，全部来自你的 Claim Card | [WORKFLOW](zh-CN/docs/WORKFLOW.md#拿到面试之后追问卡) · [示例](zh-CN/examples/jordan-lee/interview/ACME-01.md) | [WORKFLOW](en/docs/WORKFLOW.md#after-you-get-an-interview-follow-up-cards) · [example](en/examples/jordan-lee/interview/ACME-01.md) |
| 提示词 | 第一次使用、Step 0、新岗位、自审、面试准备时可直接复制的提示词 | [PROMPTS](zh-CN/docs/PROMPTS.md) | [PROMPTS](en/docs/PROMPTS.md) |
| 体检报告 | 带分数的可视化简历报告，可以只看简历，也可以对照 JD，附分享卡 | [REPORT](zh-CN/docs/REPORT.md) · [示例](zh-CN/report/template.html) | [REPORT](en/docs/REPORT.md) · [sample](en/report/template.html) |
| 脚本 | `check_claims.py`（每条 bullet 有出处）、`report_score.py`（报告分数）、`report_png.py`（报告存成图片）和 `pdf_fill.swift`（页面填满） | [scripts](zh-CN/scripts/) | [scripts](en/scripts/) |
| 更新 | 你的规则单独放一个文件，更新永远不会冲掉；一句提示词就能检查新版本 | [更新记录](zh-CN/CHANGELOG.md) | [CHANGELOG](en/CHANGELOG.md) |
| 案例 | 10 个虚构的改前改后案例，每个演示一两条规则 | [案例](zh-CN/examples/cases.md) | [cases](en/examples/cases.md) |

**用得越久，它越了解你的经历。** 每张卡上的追问和能力切面，可以帮你把没想清楚的强项说出来；换一个岗位，可以从同一套事实里调出不同的部分。你确认过的一切都会保留，你纠正某件事时，依赖它的文件会被标出来。能挖出多少，仍取决于你的回答和所用的 AI。

## 开始使用

Resume-Gate 是一个文件夹，AI 读了照着做。上手三步：选 AI 工具，拿到文件，开第一次会话。

### 1. 选在哪里用

最好用能直接打开、修改你电脑上文件夹的 AI。

| 情况 | 用什么 | 安装说明 |
|---|---|---|
| 不用终端（大多数人） | **Claude 桌面版**的 Code 页 | [下载](https://claude.com/download) · [Claude Code 文档](https://code.claude.com/docs/en/overview) |
| 平时用终端 | **Claude Code** 或 **Codex** | [Claude Code 快速上手](https://code.claude.com/docs/en/quickstart) · [Codex 快速上手](https://developers.openai.com/codex/quickstart) |
| 平时用 AI 编辑器 | **Cursor** 这类 | [下载 Cursor](https://cursor.com/download) |
| 只用网页版聊天 AI | **Claude Project** 或 ChatGPT Project | [Claude Projects 说明](https://support.claude.com/en/articles/9517075-what-are-projects)。能用，但脚本跑不了，检查要手动做 |

这些工具大多需要付费方案，或者免费版有限制，具体看各自安装说明里的最新说明。Claude Code 和 Codex 会自己读 `AGENTS.md`；别的工具，先让 AI 读它。

**用 Codex？** 它默认不联网，下载前会先问你（[官方说明](https://developers.openai.com/codex/agent-approvals-security)）。最省事的做法：第 2 步的压缩包自己下载，解压后在 Codex 里把这个文件夹当本地项目打开。不用连 GitHub。

### 2. 拿到文件

两套选**一套**下载。不用 Git，也不用 GitHub 账号。

- **简体中文**：[resume-gate-zh-CN.zip](https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-zh-CN.zip)
- **English**：[resume-gate-en.zip](https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-en.zip)

解压，用 AI 工具打开这个文件夹就行。文件夹名可以随便改。

**想让 AI 来做？** 在 AI 工具里打开一个空文件夹，贴这段：

```text
在这个文件夹里装好 Resume-Gate。下载 https://github.com/weareheya/Resume-Gate/releases/latest/download/resume-gate-zh-CN.zip（要英文版就用 resume-gate-en.zip），解压，把里面 resume-gate-zh-CN/ 文件夹的全部内容复制到这个文件夹，再删掉压缩包和多出来的文件夹。这是公开下载，不需要 GitHub 账号或连接器。如果联网要我批准，就为这次下载问我一次。最后确认 AGENTS.md 在这里；如果装了 git，再运行 git init。
```

**用 Git：**

```bash
git clone https://github.com/weareheya/Resume-Gate.git
mkdir my-job-search
cp -R Resume-Gate/zh-CN/. my-job-search/   # 或 Resume-Gate/en/.
cd my-job-search && git init
```

### 3. 开第一次会话

在 AI 工具里打开这个文件夹，说一句 **「开始」**。说什么都行：AI 会先看你进行到哪，再带着你一步一步做 Step 0，第一步就是给现在的简历做一份带分数的体检。Claude Code 里也可以输入 `/start`。如果你的工具不会自己读 `AGENTS.md`，就贴 [PROMPTS](zh-CN/docs/PROMPTS.md#0-第一次使用) 里的提示词 0。完整步骤见那一套的快速开始：[zh-CN/README.md](zh-CN/README.md#快速开始) · [en/README.md](en/README.md#quick-start)。

### 可能还需要

| 用途 | 需要 | 怎么装 |
|---|---|---|
| `check_claims.py`（出处检查） | Python 3 | macOS、Linux 一般自带。Windows：[python.org](https://www.python.org/downloads/)，安装时勾选「Add python.exe to PATH」。Windows 上命令是 `python`，不是 `python3` |
| `pdf_fill.swift`（排版检查） | macOS + Xcode 命令行工具 | 运行一次 `xcode-select --install`。不用 Mac？打开 PDF，自己看页数和最后一页 |
| 版本记录和备份（可选） | Git、一个**私有** GitHub 仓库 | [Git](https://git-scm.com/downloads)，不想用终端就装 [GitHub Desktop](https://desktop.github.com/download/)；[新建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)时选 Private |

哪一步拿不准，直接问第 1 步选的 AI。它能查你电脑上装了什么，带着把剩下的做完。

**工具自己选。** 证据库可以是 Markdown 文件，也可以放在 Notion 这类数据库里；排版可以用 [Reactive Resume](https://rxresu.me)（开源，支持 MCP）、Word，或让 AI 直接生成 PDF。详见[工具：自己选](zh-CN/README.md#工具自己选)。

**隐私：** 证据库里会放真实的工作经历，所以工作副本要保持私有。把一套内容复制到自己的文件夹或私有仓库，不要 fork 本仓库后公开填写。哪些有保障、哪些没有：

| 位置 | 实际情况 |
|---|---|
| 电脑上的文件 | 留在你自己的文件夹里 |
| Git | `.gitignore` 默认把卡片、简历、岗位、面试记录、报告和 `docs/MY-DECISIONS.md` 挡在外面。这只是保险，不是保证：提交前自己看一眼 |
| 你用的 AI | 你贴给它或让它读的内容，会交给那家 AI 服务，按它的数据政策处理。Resume-Gate 不在本地运行模型 |
| 外部简历工具 | 只有你主动上传的部分，按对方的政策处理 |

**要改这两套内容？** `en/` 和 `zh-CN/` 都要改，然后跑 `python3 tools/check_sync.py`。它检查两边的文件、编号和标题有没有对不上，也检查 `VERSION`、CHANGELOG 最新一条、根 README 的「新增」和规则条数是不是一致，发版时数字不会过期。
