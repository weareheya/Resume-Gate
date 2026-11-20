---
job_id: ACME-01
role: Acme Cloud · Partner Development Manager（虚构）
status: Approved
base: channel-baseline
date: 2026-05-10
---

# Acme Cloud · Partner Development Manager · CV Change Log

新版本：`cv/resumes/acme-pdm.md`。JD：`jobs/ACME-01.md`

## 定位

和类型 01（渠道与合作伙伴）很接近，所以一句话：搭建伙伴计划、再让伙伴卖起来的伙伴拓展负责人。事实和措辞来自基线 `channel-baseline`。

## 证据表（每张卡）

| 卡 | 和这个岗位的相关度 | 用了吗 | 用在哪里，或为什么没用 |
|---|---|---|---|
| C-001 · 渠道伙伴扩张与分层（受保护） | 高 | 用 | Summary 和第 1 条 bullet；「禁止改写」的边界 |
| C-002 · 自助伙伴门户 | 中 | 没用 | 能证明伙伴赋能，但 JD 不要求工具，一页也排满了 |
| C-003 · 伙伴来源 pipeline US$2.1M | 高 | 用 | 移进 Summary；保持 pipeline 口径，不写成营收 |
| C-004 · 联合研讨会 | 高 | 用 | 往前挪；最接近联合市场推广的证据 |
| C-005 · 伙伴峰会发言 | 中 | 没用 | 状态是「需复核」 |

**没用上但很强的？** C-002 能证明赋能，但 C-004 更贴近 R2（联合销售），篇幅也紧。已问本人（见下）。

## Delta（对基线）

| 位置 | 改动（Before → After） | 依据 |
|---|---|---|
| Summary 第 1 行 | "Partnerships manager who builds partner programs…" → "Partner development manager who recruits and tiers partners, then gets them selling…" | 对齐 JD 用词，事实不变（C-001） |
| Summary 第 2 行 | 加入 US$2.1M 伙伴来源 pipeline | C-003 |
| Northwind 第 2 条（门户） | 删除 | JD 不要求伙伴工具；保持一页。C-002 不受保护 |
| Northwind 研讨会 | 从第 4 条挪到第 2 条 | JD 要求联合销售，最接近的证据是联合营销 |
| Skills | 加 `partner recruitment`、`co-marketing` | C-001、C-004 |

## JD Coverage Report

| # | JD 要求 | 门槛 | 类别 | 证据 | 下一步 |
|---|---|---|---|---|---|
| R1 | 伙伴招募与分层 | 是 | 直接 | C-001 | 无需 |
| R2 | 和伙伴联合销售 | | 可迁移或组合 | C-004（联合营销）+ C-003（商机报备） | 按联合营销写，不写成联合销售。面试准备一个联合客户规划的故事 |
| R3 | 云市场经验 | | 可补足 | 无 | 不写。一门云市场上架的短课程能补上一部分；可以表达学习意愿，不暗示有经验 |

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
