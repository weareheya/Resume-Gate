# DECISIONS · 决策登记簿

> 本人确认过的规则。**状态为 Active 的，AI 必须遵守**；推翻时把旧条目改成 `Superseded by D-xxx`，不删除。
> 新增前先 `grep "^## D-" docs/DECISIONS.md` 取最大号 +1。

**scope**：`cv`（简历生产）· `process`（协作流程）· `strategy`（求职方向）

下面 D-001 ~ D-010 是起步规则，来自实际踩过的坑。按你的情况增删改。

---

## D-001 · 新岗位版本继承最近批准的版本，不从空白开始
- scope: cv · status: Active
- 同类没有基线时，从最近的相邻类型派生，并在 Change Log 说明。

## D-002 · 不随意删减已有的强成果
- scope: cv · status: Active
- 删除要过相关性、真实性、篇幅三关，并在 Change Log 写理由。

## D-003 · 每个数字有口径卡
- scope: cv · status: Active
- 数字必须能追到 `evidence/claims/` 里的 Claim Card，保留单位、币种、时间窗口和限定词；改写不得越过卡上的「禁止改写」。

## D-004 · JD 要但没有证据的能力不写
- scope: cv · status: Active
- 写进 Coverage Report 的「无」一栏，由本人决定怎么处理。

## D-005 · 署名与联系方式按岗位类型选
- scope: cv · status: Active
- 如果你有多个署名 / 邮箱 / 社交账号变体（例如本名与常用名），在 `cv/CV-INDEX.md` 的「署名」表里写清楚各自用在哪类岗位，不混用。

## D-006 · Evidence Retrieval Gate
- scope: process · status: Active
- 生成任何简历前，先读相关 Claim Card，并列出读了哪些 Claim ID。

## D-007 · AI 先自审再给本人看
- scope: process · status: Active
- 按 `docs/REVIEW-CHECKLIST.md` 自审并修改；交付时附截图、填充率、自审改动、Highlights、风险。

## D-008 · 人工审核关卡
- scope: process · status: Active
- 本人说「通过」之前，版本状态保持 `Draft`；通过后改 `Approved`。AI 不自行定稿。

## D-009 · PDF 正好 1 页满或 2 页满
- scope: cv · status: Active
- 最后一页填充率 ≥ 85%；先改内容再调排版参数；不为凑页数加没有证据的内容。

## D-010 · 已投递的版本冻结
- scope: process · status: Active
- 状态改为 `Sent` 后不再修改；要改就复制成新版本。`CV-INDEX` 里记录导出文件的 SHA-256。

---

<!-- 新决策模板：
## D-0xx · 一句话标题
- scope: cv|process|strategy · status: Active · date: YYYY-MM-DD
- 具体规则、适用范围、例外。
-->
