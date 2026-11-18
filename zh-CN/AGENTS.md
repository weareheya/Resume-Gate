# AGENTS.md — AI 接手规范

任何 AI 开始在本仓库做简历相关的工作前，按顺序读：

1. `docs/DECISIONS.md` — 状态为 **Active** 的决策必须遵守
2. `docs/WORKFLOW.md` — 七步流程，每步的「产出」写不出来就不进下一步
3. `cv/CV-INDEX.md` — 定岗位类型，选基线简历
4. `docs/LESSONS.md` — 过去犯过的错，扫一眼
5. 具体写简历时：`evidence/claims/`（只能用这里的事实）、`docs/REVIEW-CHECKLIST.md`（自审）

## 硬规则

**事实**
- 简历里的每条经历、每个数字都必须能追到 `evidence/claims/` 里的一张 Claim Card，或已批准 / 已投递的版本。没有出处的，不写。
- 数字保留单位、币种、时间窗口和限定词（「潜在」「累计」「单个项目」等）。不把团队成果写成个人成果。
- JD 要求但没有证据的能力，**不写**，记进 Coverage Report，由本人决定怎么补。
- 不确定的事实标「未核实」，不猜。

**流程**
- 生成任何简历前先过 Evidence Retrieval Gate：读相关 Claim Card，并**列出读了哪些**。
- 从最近批准的版本改起（Delta），不从空白开始；改动写进 `cv/changelogs/`。
- 宣称「检查完成」时附 Coverage Report：查了什么范围、没查什么。
- 给本人看之前先按 `docs/REVIEW-CHECKLIST.md` 自审。
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

每次会话结束前：更新 `cv/CV-INDEX.md`（如有新版本），补全对应 changelog，并 `git commit`。一次提交只做一件事。

## 不要提交

身份证号、薪资单、密码、API key，以及任何你不想公开的个人信息。证据库里是真实工作经历，所以本项目应当是私有仓库。如果必须公开，把 `evidence/` 和 `cv/` 加进 `.gitignore`。
