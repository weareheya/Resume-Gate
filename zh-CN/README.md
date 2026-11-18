# Resume-Gate

> 让 AI 帮你做简历，但每一句话都有出处、每一版都能追溯、每次改动都经你点头。

一套给「长期求职」用的简历生产工作流：**证据库 → 基线简历 → 按岗位改 Delta → AI 自审 → 人工审核 → 冻结**。它是文档 + 模板 + 一个排版检查脚本，不绑定任何 AI 或简历工具；任何能读你文件的 AI 都能照着做：Claude Code、Codex 会自动读取 `AGENTS.md`，其他工具让 AI 先读它就行。

## 它解决什么问题

用 AI 改简历反复出现的几类错：

| 问题 | 机制 |
|---|---|
| 已确认的成果在新版里又丢了 | **Evidence Retrieval Gate**：生成前必须读证据库，并列出读了哪些 |
| 新版本退回旧版，旧错误复活 | **基线 + Delta + Change Log**：永远从最近批准的版本改起 |
| 数字被夸大、口径混淆 | **Claim Card**：每个数字有单位、范围、归因和禁止改写 |
| AI 说「检查完了」其实有遗漏 | **Coverage Report**：写明查了什么、没查什么 |
| 排版多出几行孤页 | **整页规则 + `pdf_fill`**：PDF 必须整页满，脚本量化检查 |
| AI 自作主张定稿 | **人工审核关卡**：你说通过才算 Approved，投出的版本冻结 |
| 你说得太简略，强经历被丢掉或写弱 | **追问清单 + D-011～D-016**：AI 先问再过滤，并在事实允许的范围内选最有竞争力的写法 |
| 纠正过的强项悄悄又被写弱 | **自审里的语义对比**：protected claim 要和已批准措辞对比，不只检查还在不在 |

## 流程一览

```
JD ─▶ 选类型与基线 ─▶ 读证据（Gate）─▶ JD 映射 ─▶ 改 Delta ─▶ Change Log
                                                                 │
      冻结（Sent）◀─ 你审核通过（Approved）◀─ AI 自审 + 排版检查 ◀─┘
```

详见 [docs/WORKFLOW.md](docs/WORKFLOW.md)。

## 目录

```
AGENTS.md                 AI 接手规范（先读这个）
docs/
  WORKFLOW.md             七步流程与每步的产出
  REVIEW-CHECKLIST.md     AI 自审清单（事实 / 写法 / 排版 / 交付格式）
  DECISIONS.md            决策登记簿（含 10 条起步规则，按你的情况改）
  LESSONS.md              常见过程性失误与防线
  PROMPTS.md              常用时刻的可复制提示词
evidence/claims/          证据库：一个成果一张 Claim Card
cv/
  CV-INDEX.md             岗位类型 → 当前起点简历的检索表
  resumes/                简历正文本身，一个版本一个 Markdown 文件
  changelogs/             每份简历相对基线的改动记录
scripts/
  check_claims.py         检查每条 bullet 有出处、claim 可用、受保护的没丢（Python 3）
  pdf_fill.swift          渲染 PDF 每页为 PNG，检查页数，并报告内容延伸到页面多低的位置（macOS）
examples/                 一套虚构数据的填写示范
```

## 快速开始

1. 把本目录（`zh-CN/`）里的内容复制到你自己的求职项目根目录。
2. 先做 `docs/WORKFLOW.md` 里的 **Step 0**：把你现有的简历变成 Claim Card 和第一份已批准的基线。
3. 把 `cv/CV-INDEX.md` 里的岗位类型改成你自己的。
4. 每来一个新岗位，用 `docs/PROMPTS.md` 里的提示词 3，并贴上 JD。
5. 每版简历结束后：写 Change Log、更新 `CV-INDEX.md`、在 `docs/DECISIONS.md` 记下你新定的规则。

检查出处（任何系统，需要 Python 3）：

```bash
python3 scripts/check_claims.py cv/resumes/<id>.md
```

检查排版（macOS，需要 Xcode 命令行工具）：

```bash
mkdir -p /tmp/cv-check && swift scripts/pdf_fill.swift your-cv.pdf /tmp/cv-check
```

输出页数、每页内容延伸到的位置，并为每页生成 `p1.png`、`p2.png`……方便贴给 AI 或自己看。页数不是 1 或 2，或最后一页的内容没到页面高度的 85% 时，退出码为 2，可接进脚本。

## 脚本检查什么，不检查什么

`check_claims.py` 机械地检查出处：每条 bullet 都有 Claim ID，每个 ID 都指向一张 `Safe to draft` 的卡，受保护的 claim 没丢。`pdf_fill.swift` 检查页数和内容延伸到的位置。它量不出每页用了多少面积，所以也要看生成的图。其余都是 AI 靠读规则来执行的：claim 是否属实、措辞有没有越过卡的限制、选择是否贴合岗位。这些靠你来把关。

## 工具：自己选

本套方法不绑定任何 AI、简历工具或数据库。每一层用什么都行，只要满足「最低要求」：

| 层 | 本套默认 | 其他选择 | 最低要求 |
|---|---|---|---|
| 证据库（Claim Card） | `evidence/claims/` 里的 Markdown 文件 | Notion、Airtable 这类数据库或表格，AI 能通过 MCP 或导出读到 | AI 能读；每条 claim 有 ID 和 Claim Card 的字段；同一事实只写在一个地方 |
| 简历版本 | `cv/resumes/` 里的 Markdown，用任意工具排版 | Reactive Resume；让 AI 直接生成 PDF 或 DOCX；LaTeX、Typst；Word、Google Docs；其他支持 MCP 的简历工具 | 投出去的版本能冻结；保留投递时的原文件 |
| 投递记录 | 你自己维护的一张表或 CSV | Reactive Resume 的申请追踪；Notion 数据库 | 每条申请指向一个具体版本；只有一处为准 |

如果证据库放在数据库里而不是 `evidence/claims/`，`check_claims.py` 读不到。先把卡片导出成 Markdown 再跑，或者手动做这项检查。

### Reactive Resume

[Reactive Resume](https://rxresu.me) 是免费的开源简历工具（MIT 许可，[源码在 GitHub](https://github.com/amruthpillai/reactive-resume)）。可以直接用官方托管版，也可以用 Docker 自托管，功能相同。它有官方 MCP（`https://rxresu.me/mcp`，OAuth 登录），Claude、Cursor、Codex 等 MCP 客户端可以直接改你的简历。可导出 PDF、Word、Markdown、JSON，JSON 能导回任何一个 Reactive Resume，数据不会被锁住。它也有申请追踪。用它时，建议约定：

- 命名：`类型编号 · 类型名 · 公司/用途 · 署名`
- 标签三类：类型、状态（`Draft` / `Approved` / `Sent` / `Unused`）、岗位 ID
- 已投递的版本**锁定**，不再改；不确定是哪一版的，不要关联进投递记录

### 不用简历工具

让 AI 直接生成 PDF 或 DOCX 完全可以。这时冻结要自己管：文件名带日期和岗位，在 `cv/CV-INDEX.md` 记下文件的 SHA-256，再配一张投递表。

### 其他支持 MCP 的工具

用之前先确认三件事：能不能导出全部数据、能不能锁定已投递的版本、它把你的工作经历存在哪里你能不能接受。

## 工作副本务必保持私有

证据库里是你真实的工作经历：雇主、数字、合作过的人。**把本套内容复制到你自己的项目里，并让那个项目保持私有仓库。** 不要 fork 本仓库后公开填写。如果一定要用公开仓库，先把 `evidence/` 和 `cv/` 加进 `.gitignore`。

## 设计取舍

- **文档优先，不写框架。** 规则靠 AI 读文档执行，所以文档要短、具体、有勾选项。
- **事实比文采重要。** 流程里每一道关都是为了防止「写得漂亮但不是真的」。
- **写太弱也是失败。** 防夸大不能把简历写成免责声明。先把价值挖出来，再判断能写到什么程度。
- **你是最后一道关。** AI 可以起草、自审，但定稿和对外动作由你决定。

## 来源

从一个真实求职项目里抽出来的。原项目里的个人事实、公司名和岗位数据都没有带进来，`examples/` 里全是虚构的。
