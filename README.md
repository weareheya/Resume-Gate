# Resume-Gate

**English** · [简体中文](#简体中文)

> Use AI to build your resume, but make sure every line has a source, every version can be traced, and every change goes through you.

A resume workflow for a long job search, where you tailor many versions over weeks or months: **evidence bank → baseline resume → per-job delta → AI self-review → your sign-off → freeze**. It's docs, templates, and two small check scripts, and it isn't tied to any AI or resume tool.

**It's for you if** you use AI to tailor resumes and have seen it drop results you already confirmed, inflate a number, or quietly water down your strongest experience. **It's probably overkill if** you need one resume, once.

![Resume-Gate overview: one fact, one card, every version traces back](assets/overview-en.svg)

## What's inside

| Feature | What it does | English | 中文 |
|---|---|---|---|
| Claim Cards | One file per accomplishment: facts, what each number measures, your share vs the team's, wording you can't use | [template](en/evidence/claims/_TEMPLATE.md) · [example](en/examples/jordan-lee/evidence/claims/C-001.md) | [模板](zh-CN/evidence/claims/_TEMPLATE.md) · [示例](zh-CN/examples/jordan-lee/evidence/claims/C-001.md) |
| Workflow | Step 0 (cold start) and seven steps per job, each with an output you must show | [WORKFLOW](en/docs/WORKFLOW.md) | [WORKFLOW](zh-CN/docs/WORKFLOW.md) |
| Probing questions | Seven questions the AI asks before it drops or weakens anything | [WORKFLOW](en/docs/WORKFLOW.md#probing-questions) | [追问清单](zh-CN/docs/WORKFLOW.md#追问清单) |
| Decision register | 16 starter rules, from "don't cut strong results" to "pick the strongest defensible wording" | [DECISIONS](en/docs/DECISIONS.md) | [DECISIONS](zh-CN/docs/DECISIONS.md) |
| AI self-review | Facts, writing, layout, and handoff checks the AI runs before you see anything | [REVIEW-CHECKLIST](en/docs/REVIEW-CHECKLIST.md) | [自审清单](zh-CN/docs/REVIEW-CHECKLIST.md) |
| Lessons | Real process mistakes and the guardrail each one led to | [LESSONS](en/docs/LESSONS.md) | [LESSONS](zh-CN/docs/LESSONS.md) |
| Prompts | Copy-paste prompts for the first session, Step 0, a new job, and self-review | [PROMPTS](en/docs/PROMPTS.md) | [PROMPTS](zh-CN/docs/PROMPTS.md) |
| Scripts | `check_claims.py` (every bullet has a source) and `pdf_fill.swift` (pages are full) | [scripts](en/scripts/) | [scripts](zh-CN/scripts/) |
| Cases | Ten made-up before-and-after cases, one or two rules each | [cases](en/examples/cases.md) | [案例](zh-CN/examples/cases.md) |

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

These tools need a paid plan; each setup guide lists which. Claude Code and Codex read the kit's `AGENTS.md` on their own. In other tools, tell the AI to read it first.

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

Open the folder in your AI tool and paste prompt 0 from the kit's [PROMPTS](en/docs/PROMPTS.md#0-first-session). It walks you through Step 0 one step at a time. The full walkthrough is in the kit's quick start: [en/README.md](en/README.md#quick-start) · [zh-CN/README.md](zh-CN/README.md#快速开始).

### What else you might need

| For | Needed | How to get it |
|---|---|---|
| `check_claims.py` (sourcing check) | Python 3 | macOS and Linux usually have it. Windows: [python.org](https://www.python.org/downloads/), and tick "Add python.exe to PATH" during install. On Windows the command is `python`, not `python3` |
| `pdf_fill.swift` (layout check) | macOS + Xcode command line tools | Run `xcode-select --install` once. Not on a Mac? Check the page count and last page of the PDF by eye |
| Version history and backup (optional) | Git, a **private** GitHub repo | [Git](https://git-scm.com/downloads) or [GitHub Desktop](https://desktop.github.com/download/) if you'd rather not use a terminal; [create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) and set it to Private |

Not sure about any of this? Ask the AI tool you picked in step 1. It can check what's installed and walk you through the rest.

**Tools are your choice.** Evidence can live in Markdown files or a database such as Notion; layout can happen in [Reactive Resume](https://rxresu.me) (open source, with MCP), in Word, or in a PDF your AI generates. See [Tools: your choice](en/README.md#tools-your-choice).

**Privacy:** your evidence bank will hold your real work history, so keep your working copy private. Copy a kit into your own folder or private repo; don't fork this repo and fill it in publicly.

**Changing the kits?** Edit both `en/` and `zh-CN/`, then run `python3 tools/check_sync.py` to catch files, IDs or headings that differ between them.

---

## 简体中文

> 用 AI 改简历可以，前提是每句话都有出处。

一套给长期求职用的简历工作流。几周、几个月、几十版改下来不乱：**证据库 → 基线 → 按岗位改 Delta → AI 自审 → 本人审核 → 冻结**。文档 + 模板 + 两个检查脚本，不绑定任何 AI 或简历工具。

**适合**：用 AI 改过简历，遇到过它把确认过的成果弄丢、把数字写大，或者把最强的经历悄悄写弱。**用不上**：只要一份简历，投一次。

![Resume-Gate 总览：事实只写一次，每一版都能追回出处](assets/overview-zh.svg)

## 里面有什么

| 功能 | 做什么 | 中文 | English |
|---|---|---|---|
| Claim Card | 一个成果一个文件：事实、每个数字量的是什么、你的部分和团队的部分、不能用的说法 | [模板](zh-CN/evidence/claims/_TEMPLATE.md) · [示例](zh-CN/examples/jordan-lee/evidence/claims/C-001.md) | [template](en/evidence/claims/_TEMPLATE.md) |
| 工作流 | Step 0（冷启动）和每个岗位的七步，每步都有必须拿得出的产出 | [WORKFLOW](zh-CN/docs/WORKFLOW.md) | [WORKFLOW](en/docs/WORKFLOW.md) |
| 追问清单 | AI 在删掉或写弱任何内容之前要问的 7 个问题 | [追问清单](zh-CN/docs/WORKFLOW.md#追问清单) | [Probing questions](en/docs/WORKFLOW.md#probing-questions) |
| 决策登记簿 | 16 条起步规则，从「不随意删强成果」到「选最强又站得住的写法」 | [DECISIONS](zh-CN/docs/DECISIONS.md) | [DECISIONS](en/docs/DECISIONS.md) |
| AI 自审 | 给你看之前，AI 先过一遍事实、写法、排版和交付格式 | [自审清单](zh-CN/docs/REVIEW-CHECKLIST.md) | [REVIEW-CHECKLIST](en/docs/REVIEW-CHECKLIST.md) |
| 失误记录 | 真实踩过的过程性错误，以及每条带来的防线 | [LESSONS](zh-CN/docs/LESSONS.md) | [LESSONS](en/docs/LESSONS.md) |
| 提示词 | 第一次使用、Step 0、新岗位、自审时可直接复制的提示词 | [PROMPTS](zh-CN/docs/PROMPTS.md) | [PROMPTS](en/docs/PROMPTS.md) |
| 脚本 | `check_claims.py`（每条 bullet 有出处）和 `pdf_fill.swift`（页面填满） | [scripts](zh-CN/scripts/) | [scripts](en/scripts/) |
| 案例 | 10 个虚构的改前改后案例，每个演示一两条规则 | [案例](zh-CN/examples/cases.md) | [cases](en/examples/cases.md) |

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

这些工具都要付费方案，具体看各自的安装说明。Claude Code 和 Codex 会自己读 `AGENTS.md`；别的工具，先让 AI 读它。

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

在 AI 工具里打开这个文件夹，贴上 [PROMPTS](zh-CN/docs/PROMPTS.md#0-第一次使用) 里的提示词 0。它会带着一步一步做 Step 0。完整步骤见那一套的快速开始：[zh-CN/README.md](zh-CN/README.md#快速开始) · [en/README.md](en/README.md#quick-start)。

### 可能还需要

| 用途 | 需要 | 怎么装 |
|---|---|---|
| `check_claims.py`（出处检查） | Python 3 | macOS、Linux 一般自带。Windows：[python.org](https://www.python.org/downloads/)，安装时勾选「Add python.exe to PATH」。Windows 上命令是 `python`，不是 `python3` |
| `pdf_fill.swift`（排版检查） | macOS + Xcode 命令行工具 | 运行一次 `xcode-select --install`。不用 Mac？打开 PDF，自己看页数和最后一页 |
| 版本记录和备份（可选） | Git、一个**私有** GitHub 仓库 | [Git](https://git-scm.com/downloads)，不想用终端就装 [GitHub Desktop](https://desktop.github.com/download/)；[新建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)时选 Private |

哪一步拿不准，直接问第 1 步选的 AI。它能查你电脑上装了什么，带着把剩下的做完。

**工具自己选。** 证据库可以是 Markdown 文件，也可以放在 Notion 这类数据库里；排版可以用 [Reactive Resume](https://rxresu.me)（开源，支持 MCP）、Word，或让 AI 直接生成 PDF。详见[工具：自己选](zh-CN/README.md#工具自己选)。

**隐私：** 证据库里会放真实的工作经历，所以工作副本要保持私有。把一套内容复制到自己的文件夹或私有仓库，不要 fork 本仓库后公开填写。

**要改这两套内容？** `en/` 和 `zh-CN/` 都要改，然后跑 `python3 tools/check_sync.py`，检查两边的文件、编号和标题有没有对不上。
