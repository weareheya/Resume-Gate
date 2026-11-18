# Jordan Lee：一套完整的示例

一个小型的虚构求职项目，结构和你自己的项目一模一样。Jordan Lee、Northwind Labs、Acme Cloud 和所有数字都是编的。不要把这里的任何内容抄进自己的简历。简历正文用英文，Claim Card 用中文。

| 路径 | 展示什么 |
|---|---|
| [evidence/claims/](evidence/claims/) | 五张 Claim Card。C-001 是 `protected: true`。C-005 是 `需复核`，暂时不能用 |
| [cv/resumes/channel-baseline.md](cv/resumes/channel-baseline.md) | 第一份批准的基线，Step 0 做的 |
| [cv/resumes/acme-pdm.md](cv/resumes/acme-pdm.md) | 针对一个岗位、从基线改出来的新版本 |
| [cv/changelogs/ACME-01.md](cv/changelogs/ACME-01.md) | 它的 Change Log：读了什么、Delta、Coverage Report、自审 |
| [cv/CV-INDEX.md](cv/CV-INDEX.md) | 做完这一版之后的索引 |
| [cv/resumes/acme-pdm-with-traps.md](cv/resumes/acme-pdm-with-traps.md) | 同一版本，故意埋了七个错误 |

## 自己跑一遍

在这套内容的根目录运行（Windows 上把 `python3` 换成 `python`）：

```bash
cd examples/jordan-lee
python3 ../../scripts/check_claims.py cv/resumes/acme-pdm.md
python3 ../../scripts/check_claims.py cv/resumes/acme-pdm-with-traps.md
```

**`acme-pdm.md` 通过**（退出码 0）：

```text
WARN  acme-pdm.md：栏目「Skills」有 1 行，这个脚本不验证
NOTE  C-002 在基线（channel-baseline.md）里用到了，这里没有
通过：检查了 5 行，用到 3 个 Claim ID，没有错误
```

NOTE 是预期内的：C-002 不受保护，Change Log 里写了为什么删。

**`acme-pdm-with-traps.md` 未通过**（退出码 1），五个错误：

```text
ERROR acme-pdm-with-traps.md:17：这一行没有 Claim ID：Partner development leader with a track record of buildin...
ERROR acme-pdm-with-traps.md:18：C-005 的状态是「需复核」，只有「Safe to draft」才能使用
ERROR acme-pdm-with-traps.md:26：数字「420」在 C-004 里找不到。……
ERROR acme-pdm-with-traps.md:27：C-009 找不到对应的 Claim Card
ERROR 受保护的 claim C-001 在基线（channel-baseline.md）里用到了，这里的 Summary/Experience 却没有。……
未通过：acme-pdm-with-traps.md 里有 5 个错误
```

## 七个陷阱

| # | 位置 | 错误 | 谁能发现 |
|---|---|---|---|
| 1 | Summary 第 1 行 | 没有出处的说法 | 脚本 |
| 2 | Summary 第 2 行 | 用了还是 `需复核` 的 C-005 | 脚本 |
| 3 | 研讨会那条 | 420 人报名，卡上写的是 380 | 脚本 |
| 4 | 联合销售那条 | 引用了不存在的 C-009 | 脚本 |
| 5 | 整份文件 | 受保护的 C-001（12 → 40 家伙伴）被删了 | 脚本 |
| 6 | 门户那条 | 写成 "Built and launched" 门户。C-002 写明是工程团队做的，Jordan 写的是需求 | **你。** ID 和数字都对 |
| 7 | 营收那条 | "Generated US$2.1M in partner revenue"。C-003 写明这是 pipeline，不是营收 | **你。** 数字在卡上，脚本会放行 |

重点在第 6、7 个：脚本检查每一行有没有出处、数字对不对得上，但判断不了措辞有没有越过卡上的「禁止改写」。这要靠自审清单和你自己读一遍。
