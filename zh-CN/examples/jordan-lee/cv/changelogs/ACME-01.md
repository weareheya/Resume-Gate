---
job_id: ACME-01
role: Acme Cloud · Partner Development Manager（虚构）
status: Approved
base: channel-baseline
date: 2026-05-10
---

# Acme Cloud · Partner Development Manager · CV Change Log

新版本：`cv/resumes/acme-pdm.md`。JD 来源：（虚构，未附）

## Evidence Retrieval Gate · 读了什么

| 来源 | 用途 |
|---|---|
| C-001 · 渠道伙伴扩张与分层（受保护） | Summary 和第 1 条 bullet；「禁止改写」的边界 |
| C-002 · 自助伙伴门户 | 读了；这一版删掉（见 Delta） |
| C-003 · 伙伴来源 pipeline US$2.1M | 移进 Summary；保持 pipeline 口径，不写成营收 |
| C-004 · 联合研讨会 | 往前挪；作为联合销售的相邻证据 |
| C-005 · 伙伴峰会发言 | 没用：状态是「需复核」 |
| DECISIONS D-001 到 D-004 | 继承基线、不删强成果、Claim Card、无证据不写 |

## Delta（对基线）

| 位置 | 改动（Before → After） | 依据 |
|---|---|---|
| Summary 第 1 行 | "Partnerships manager who builds partner programs…" → "Partner development manager who recruits and tiers partners, then gets them selling…" | 对齐 JD 用词，事实不变（C-001） |
| Summary 第 2 行 | 加入 US$2.1M 伙伴来源 pipeline | C-003 |
| Northwind 第 2 条（门户） | 删除 | JD 不要求伙伴工具；保持一页。C-002 不受保护 |
| Northwind 研讨会 | 从第 4 条挪到第 2 条 | JD 要求联合销售，最接近的证据是联合营销 |
| Skills | 加 `partner recruitment`、`co-marketing` | C-001、C-004 |

## JD Coverage Report

| JD 要求 | 覆盖 | 说明 / 怎么补 |
|---|---|---|
| 伙伴招募与分层 | 直接 | C-001 |
| 和伙伴联合销售 | 部分 | C-004 是联合营销，不是联合销售，按联合营销写。面试准备一个联合客户规划的故事 |
| 云市场经验 | 无 | 没有证据，不写。可以表达学习意愿，不暗示有经验 |

**主要缺口**：没有直接的联合销售或云市场成果。

## 检查范围

- 查了：整份基线、C-001 到 C-005、上面的 JD 要求。
- 没查：简历工具里的实际页数（见下方排版）；C-005 的出处（仍缺）。

## AI 自审

| 发现 | 修正 |
|---|---|
| 初稿写成 "generated US$2.1M in revenue" | 改回 C-003 的措辞：伙伴来源 pipeline |
| Summary 写了 4 行 | 压到 2 行 |
| `check_claims.py` 给出 NOTE：C-002 相对基线被删 | 符合预期，已在 Delta 说明。C-002 不受保护 |

脚本结果：`通过：检查了 5 行，用到 3 个 Claim ID，没有错误`（外加上面的 NOTE）。
排版：1 页，内容延伸到页面高度的 93%。

## 需要本人确认的问题

1. 这个岗位不写门户（C-002）可以吗？

## 审核结果

本人 2026-05-10 批准，状态改为 Approved。
