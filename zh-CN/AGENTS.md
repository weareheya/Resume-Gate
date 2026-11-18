# AGENTS.md — AI 接手规范

任何 AI 开始在本仓库做简历相关的工作前，按顺序读：

1. `docs/DECISIONS.md` — 状态为 **Active** 的决策必须遵守
2. `docs/WORKFLOW.md` — 七步流程，每步的「产出」写不出来就不进下一步
3. `cv/CV-INDEX.md` — 定岗位类型，选基线简历
4. `docs/LESSONS.md` — 过去犯过的错，扫一眼
5. 具体写简历时：`evidence/claims/`（只能用这里的事实）、`docs/REVIEW-CHECKLIST.md`（自审）

## 硬规则

**事实**
- 只能用状态为 `Safe to draft` 的 claim。`需复核` 的 claim 只能拿来问本人，不能写进简历。
- 每条简历 bullet 末尾用 HTML 注释标上 Claim ID（`<!-- C-001 -->`）。没有标签的 bullet 就是没有出处，按错误处理。
- 简历里的每条经历、每个数字都必须能追到 `evidence/claims/` 里的一张 Claim Card，并通过这张卡追到原始出处。没有出处的，不写。
- 已批准 / 已投递的简历**不是证据**，它只记录本人批准过哪些措辞和结构。旧简历里的某条 bullet 如果没有 Claim Card 支撑，就当作未核实：不往新版本里照抄，先补写这张卡并经本人确认。
- 数字保留单位、币种、时间窗口和限定词（「潜在」「累计」「单个项目」等）。不把团队成果写成个人成果。
- JD 要求但没有证据的能力，**不写**，记进 Coverage Report，由本人决定怎么补。但标「没有证据」之前，先用 `docs/WORKFLOW.md` 的追问清单问过本人（D-014）。
- 在所有站得住的写法里选最有竞争力的那个：既不夸大，也不写成免责声明（D-015）。
- 不确定的事实标「未核实」，不猜。

**流程**
- 如果 `cv/CV-INDEX.md` 里还没有 Approved 的起点，先做 `docs/WORKFLOW.md` 里的 Step 0，再做别的。
- 生成任何简历前先过 Evidence Retrieval Gate：读相关 Claim Card，并**列出读了哪些**。
- 从匹配度最高的已批准版本改起（Delta），不从空白开始；改动写进 `cv/changelogs/`。
- 标了 `protected: true` 的 claim，未经本人批准，不能删除或削弱。新版本里如果漏了一条，要明说并解释原因。
- 宣称「检查完成」时附 Coverage Report：查了什么范围、没查什么。
- 给本人看之前先按 `docs/REVIEW-CHECKLIST.md` 自审。
- 给本人看简历之前，先跑 `python3 scripts/check_claims.py cv/resumes/<id>.md`，修掉所有错误，并报告结果。
- **人工审核关卡**：本人说「通过」之前，版本状态保持 `Draft`；已投递（`Sent`）的版本不再修改。

**权限**
| 等级 | 例子 | AI 能否直接做 |
|---|---|---|
| L1 只读 | 读 JD、读证据、分析匹配度 | 可以 |
| L2 可逆的内部修改 | 写草稿、改本仓库文档 | 可以，写进 changelog |
| L3 对外行动 / 不可逆 | 提交申请、联系招聘方、修改已确认的事实 | **先得到本人明确批准** |

**决策**
- 本人说「以后都这样」「就按这个来」时，**当场**写进 `docs/DECISIONS.md`，不要只留在对话里。
- 编号前先 `grep "^## D-" docs/DECISIONS.md` 取最大号 +1，防止多个会话撞号（见 LESSONS L-06）。
- 推翻旧决策：把旧条目状态改成 `Superseded by D-xxx`，不删除。

## 交接

每次会话结束前：更新 `cv/CV-INDEX.md`（如有新版本），补全对应 changelog，如果有被追踪的文件改动，就 `git commit`。一次提交只做一件事。

## 不要提交

身份证号、薪资单、密码、API key，以及任何你不想公开的个人信息。证据库里是真实工作经历，所以本项目应当是私有仓库。如果必须公开，把 `evidence/` 和 `cv/` 加进 `.gitignore`。
