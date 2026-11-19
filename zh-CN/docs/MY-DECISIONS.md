# MY-DECISIONS · 我自己的规则

> 你定下的规则（「以后都这样」）。**状态为 Active 的，AI 必须遵守**；和 [DECISIONS.md](DECISIONS.md) 里的起步规则冲突时，以这里为准。
> 这个文件归你：更新工具时永远不会动它。
> 从 D-101 开始编号。新增前先 `grep "^## D-" docs/MY-DECISIONS.md` 取最大号 +1（还没有就从 D-101 开始）。推翻时把旧条目改成 `Superseded by D-xxx`，不删除。

字段和起步规则一样：**scope** 为 `cv` · `process` · `strategy`，**applies-to** 为 `all`、`type: 01` 或 `job: ACME-01`。要改或停用某条起步规则，写明是哪一条：`overrides: D-009`。

---

<!-- 模板：
## D-101 · 一句话标题
- scope: cv|process|strategy · status: Active · applies-to: all · date: YYYY-MM-DD
- overrides:（可选，例如 D-009）
- 具体规则、适用范围、例外。
-->
