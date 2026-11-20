# REVIEW-CHECKLIST · AI 自审清单

简历写完、给本人看之前，AI 必须先按这份清单自审并修改。交付时附上：改了什么、还剩什么问题、Highlights。

写法依据有两类，各管一件事：

- **简历写法**：Harvard 就业指导中心的简历指南：[Harvard College](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/)、[Harvard Extension School](https://careerservices.fas.harvard.edu/resources/hes-create-impactful-resumes-and-cover-letters/)、[Harvard Law School 简历工作坊](https://hls.harvard.edu/wp-content/uploads/2024/06/Resume-Workshop-for-Website.pdf)。共同的几条：每条用行动动词开头，能量化就量化，用具体动作代替「responsible for」，不用空泛形容词，写给几秒内扫读的人。
- **自查一条经历讲没讲完整**：STAR（Situation / Task / Action / Result）。它出自 DDI 1974 年的结构化行为面试法 Targeted Selection（[DDI 的说明](https://www.ddi.com/blog/what-is-the-star-format)），本来是面试官用来收集完整回答的，不是简历格式。这里只拿它当检查框架，见 B 节。

另加常见的 ATS 建议（单栏、标准栏目名）。第三方博客里的具体统计数字不可靠，不作依据。

## A. 事实（先过这一关，不通过不往下看）

先跑 `python3 scripts/validate_evidence.py` 和 `python3 scripts/check_claims.py cv/resumes/<id>.md`。它们能机械地检查下面的前两项，并核对：被检查行里的每个数字都来自所引用的卡（数值、量级、币种一致）；没有用卡上的禁用词（「禁止改写」里加了引号的说法会给提醒）；职位标题和教育背景与 `evidence/profile.md` 一致；受保护的 claim 已确认的数字还在。找不到 Summary 或 Experience 栏目时会判为未通过；其他栏目（Skills、Projects 等）会标为未验证，需要人工检查。其余仍要靠判断。

- [ ] 每条都能追到 Claim Card。已批准 / 已投递的简历不是证据，只是已批准的措辞
- [ ] 每条 bullet 末尾都有 Claim ID 注释，且指向的卡状态是 `Safe to draft`；用到的数字在卡上没有标 `待核实`
- [ ] 数字带单位和口径（币种、时间窗口、「潜在」「累计」等限定词没丢）
- [ ] 每一行都守住卡上的「禁止改写」。要看的是：这一行有没有把别人的工作说成是自己独立做的（「搭建了门户」）。「和工程团队一起搭建」这类共享的说法是合理包装，适度模糊也没问题。`check_claims.py` 会对「禁止改写」里加了引号的说法给出提醒：每条都读一下，只有在这一行独占了功劳时才改。不要为了躲提醒，对真实的合作避而不谈（D-015、LESSONS L-14）
- [ ] 个人贡献和团队成果分开；职称按雇佣记录，不抬高
- [ ] 起止日期、公司性质、角色正确
- [ ] 同期结果没有被写成全由本人带来（因果）；能说明的连接已经写出来，没有被一律拆开（D-014）
- [ ] 标了 `protected` 的 claim 不只是还在，**含义也没有被写弱**：和已批准措辞逐句对比。`check_claims.py` 会检查 ID 和已确认的数字还在不在，但判断不了措辞（LESSONS L-12）
- [ ] JD 要但没有证据的能力**没写**，已记进 Coverage Report
- [ ] 没有无意中漏掉强项：每张 Claim Card 都在证据表里，比简历已有内容更强的未用卡，要么换进来了，要么写了原因（D-019）
- [ ] 没有敏感信息（前雇主保密内容、他人隐私）

## B. 写法

以下是默认值。本人已经批准过的结构，优先于它们。

- [ ] Summary 简短（约 3–4 行）：定位 + 2–4 个最强证据；不用「results-oriented」「team player」类空话
- [ ] bullet 在准确的前提下用有力动词开头；避免「Responsible for」「Duties included」这类职责式开头。「Helped」「Served as」如果是如实描述，可以用：措辞绝不能说得比实际角色更大
- [ ] 每条尽量是「做了什么 + 怎么做 + 结果」，有数字就放进去
- [ ] 用 STAR 自查每条强 bullet：本人的动作（A）和结果（R）都在；背景（S）和任务（T）只在不写就看不懂时才写。落到纸面压缩成「动作 + 关键判断或交付物 + 结果」，不写成四句话。完整的 STAR 留给面试
- [ ] 每条 ≤ 3 行（排版后）；最近两段经历各 2–5 条，更早的 1–3 条
- [ ] 与目标 JD 最相关的 bullet 排在每段第一
- [ ] 没有写成免责声明：在准确的前提下，篇幅花在证明做了什么，而不是解释没做什么（D-015）
- [ ] 大小写、标点、货币写法统一
- [ ] 联系方式干净：不带 `https://`，链接文字可读
- [ ] 栏目名用标准写法（Summary / Experience / Education / Skills）

## C. 排版

- [ ] 导出 PDF 要填满页面：默认**1 页满或 2 页满**，最后一页的内容到达页面高度的 85% 以上（这两个默认值可在 D-009 里改），不能只多出几行
- [ ] 分页落在两段经历之间，不把一段经历的标题和 bullet 拆开
- [ ] 没有只有一两个词的孤行（能改措辞就改）
- [ ] 如用简历工具自带的检查，error / warning 为 0

调整顺序：先改内容，再动排版参数（字号 10.5–12.5、行距 1.3–1.5、页边距、段间距）。

检查工具：

```bash
swift scripts/pdf_fill.swift <cv.pdf> <输出目录>
```

它检查页数（默认 1 页或 2 页）和最后一页的内容延伸到哪里（默认 85%）。「到达位置」是最后一处内容结束的地方，不是页面的使用面积，所以页脚里的页码会让一张几乎空白的页面看起来是满的。如果你的简历有页脚，加上 `--ignore-bottom=4`（只填页脚的高度；这个区域里真正的内容也会被忽略）。一定要同时看生成的 PNG。

## D. 交给本人时的格式

1. **每页截图**：直接贴 `pdf_fill` 生成的 PNG，不让本人自己去找文件
2. **排版结果**：页数、每页内容延伸到的位置
3. **自审发现与改动**（表格）
4. **Highlights**：这版最强的 3–5 个卖点，对应 JD 哪条
5. **风险 / 缺口**：JD 要但没证据的、面试要讲清楚的
6. **改动对照**：相对基线改了什么。第一次给某个岗位看时附完整文字，之后只列改动
