#!/usr/bin/env python3
"""对照证据库检查一份简历。只用标准库，macOS、Linux、Windows 都能跑。

它检查什么（脚本能确定性判断的部分）：
  1. 简历里有脚本认得的 Summary 和/或 Experience 栏目（中英文常见写法都认，例如
     "Professional Summary"、"Work Experience"、"工作经历"）。一个都认不出来，或者里面没有
     可检查的内容时，判为未通过，不会再显示"通过"。
  2. Summary、Projects/Achievements 下的每一行，以及 Experience 下的每条 bullet，末尾都有
     HTML 注释形式的 Claim ID，例如：  - 重建了伙伴计划 ... <!-- C-001 -->
     缩进在 bullet 下面的续行算作同一条。Experience 里的普通行只有带数字时才需要 Claim ID，
     否则只提示"未验证"。
  3. 每个 Claim ID 都恰好对上 evidence/claims/ 里的一张卡，且卡的状态是 "Safe to draft"。
     卡上标「待核实」的数字（或 ✓ 和空白以外的任何值）不能用。
  4. 被检查的行里出现的每个数字（数量、百分比、金额、倍数）都来自它引用的卡。「禁止改写」
     「出处」「待补」里的数字和 Claim ID 本身都不算。带量级的金额按数值比较（US$2.1M =
     US$2,100,000，但不等于 US$2.1B），币种也必须和卡上一致。卡上没有的个位数或英文
     two–twenty 只给提醒。
  5. 被检查的行不能出现所引用卡上「禁用词：」一行列出的词（例如 revenue、营收）。
  6. evidence/profile.md 填好之后，Experience 里的职位标题（### 职位 · 公司 · 年份）和
     Education 的每一行都要和它对得上。
  7. 基线：如果 cv/CV-INDEX.md 里这份简历的类型已经有起点，新版本必须写 `base:`。有基线时，
     基线 Summary/Experience 里用到的 `protected: true` claim，这里也必须还在（卡上的 `keep-for` 只列了其他岗位类型时除外），而且已确认的
     数字不能少，除非本人同意（front matter 里写 `protected-ok: C-001`）。
  8. 批准后改过的卡（D-020，scripts/evidence_deps.py）：这一版引用的卡在 `--record` 之后改过，会指出
     是哪张卡、改了哪些区块、算不算重大变化。原样复制自基线、而基线批准时卡还没改的行，也会指出。
     这些都是 WARN；加 --finalize 时，重大变化或从没记录过的卡是 ERROR。已投递的版本只给 NOTE。
     没有记录的旧版本只汇总成一行提示。
  其他非空栏目（Skills 等）会提示"未验证"，其中没有卡片支撑的数字会单独指出。
  Languages、联系方式、References 直接跳过。ERROR 判为未通过；WARN 值得看一眼，但不影响通过。

它不检查什么：每句话是否真的由所引用的卡支持（合法的 ID 仍然可能挂在编造的句子上）、排版。
这些仍然要靠人和自审清单。

用法：
  python3 scripts/check_claims.py cv/resumes/<id>.md [--base cv/resumes/<基线id>.md]
                                  [--claims evidence/claims] [--profile evidence/profile.md]
                                  [--finalize] [--lang en|zh]
  python3 scripts/check_claims.py <简历或追问卡> --record all|C-001,C-002
      本人批准（或确认复核）之后运行：记下它对照的是每张卡的哪个版本

退出码：0 = 没有错误，1 = 发现错误，2 = 没能运行（缺文件、用法错误）。
"""
import argparse
import importlib.util
import math
import re
import sys
from pathlib import Path

DEFAULT_LANG = "zh"

_spec = importlib.util.spec_from_file_location("evidence_deps", Path(__file__).with_name("evidence_deps.py"))
deps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(deps)

BLOCK_NAMES = {
    "en": {"removed": "card removed", "facts": "what happened", "numbers": "numbers", "attribution": "attribution",
           "meta": "status/evidence/role", "dont": "don't rephrase as", "protect": "protection",
           "wording": "approved wording", "facets": "facets", "source": "source", "other": "other text"},
    "zh": {"removed": "卡片已删除", "facts": "事实", "numbers": "数字与口径", "attribution": "归因",
           "meta": "状态/证据/职位", "dont": "禁止改写", "protect": "保护设置",
           "wording": "已批准措辞", "facets": "能力切面", "source": "出处", "other": "其他内容"},
}

T = {
    "en": {
        "no_file": "File not found: {p}",
        "no_claims": "No claim cards found in {p}",
        "dup_id": "{c} is defined by more than one card ({f}). Give each card its own ID",
        "untagged": "{f}:{n}: no Claim ID on this line: {t}",
        "unknown": "{f}:{n}: {c} does not match any Claim Card",
        "status": "{f}:{n}: {c} has status \"{s}\"; only \"Safe to draft\" can be used",
        "interview_only": "{f}:{n}: {c} is \"Interview only\": fine to talk about in an interview, but it doesn't go on a resume",
        "pending": "{f}:{n}: the number \"{x}\" is not marked ✓ on {c}. Confirm it and mark it ✓ on the card, or remove it",
        "number": "{f}:{n}: the number \"{x}\" doesn't appear in {c}. Add it to the card's Numbers table (with its unit and basis), or remove it",
        "currency": "{f}:{n}: \"{x}\" is in {cur}, but {c} gives it in {want}",
        "banned": "{f}:{n}: \"{w}\" is a banned word on {c} (see its \"Don't rephrase as\")",
        "dont": "{f}:{n}: \"{w}\" is wording {c}'s \"Don't rephrase as\" warns about. Re-read that note and check this line still says what the card says",
        "no_sections": "{f}: no Summary or Experience section recognized (level-2 headings found: {h}). Nothing could be checked",
        "nothing": "{f}: Summary/Experience sections found but they contain no lines to check",
        "unchecked": "{f}: section \"{s}\" has {k} line(s) this script does not verify",
        "no_profile": "{f}: role headings / Education not checked yet: {p} is missing or empty. Fill in your roles and education there to turn this check on",
        "weak_number": "{f}:{n}: \"{x}\" isn't on {c}. Fine if it's just wording; if it's a count, add it to the card",
        "no_currency": "{f}:{n}: \"{x}\" has a currency, but {c} doesn't say which. Add the currency to the card's Numbers table",
        "loose_number": "{f}: section \"{s}\", line {n} has a number no card backs: {t}",
        "waived": "{c}: dropped or shortened with the user's approval (protected-ok in the front matter). Say why in the Change Log",
        "role": "{f}:{n}: role heading doesn't match any role in {p} (title, company and years): {t}",
        "education": "{f}:{n}: Education line doesn't match {p} (degree, school and year): {t}",
        "dropped_protected": "Protected claim {c} is used in the baseline ({b}) but missing from Summary/Experience here. Restore it, or with the user's approval add `protected-ok: {c}` to the front matter and explain why in the Change Log",
        "weakened": "Protected claim {c}: the baseline ({b}) states {x} but this version no longer does. Restore it, or with the user's approval add `protected-ok: {c}` to the front matter and explain why in the Change Log",
        "dropped": "{c} is used in the baseline ({b}) but not here",
        "keep_for": "Protected claim {c} is kept for type(s) {k}; this resume is type {ty}, so leaving it out is allowed. Say why in the Change Log",
        "base_missing": "Baseline file not found: {p}. The protected-claims check can't run. Fix `base:` or pass --base",
        "base_required": "{f}: no `base:`, but CV-INDEX already has a starting point for type {ty} ({s}). Set `base:` to the version this was copied from",
        "frozen": "{f} was frozen when it was sent (cv/frozen.txt) and has been edited since. Restore it, and make any change in a new version (D-010)",
        "table_gap": "{f}: the evidence table in {cl} doesn't mention {cs}. Look at them, or add them as unused with a reason; unused cards can share one line (D-019)",
        "dep_changed": "{f}: {c} changed after this version was {how} ({b}). Needs recheck: read the lines citing {c} against the card, then with the user's OK run --record {c}",
        "dep_changed_final": "{f}: {c} has an unresolved major change since this version was approved ({b}). This doesn't mean the resume is wrong, only that nobody has checked it against the corrected card yet. Show the user the lines citing {c}; once they confirm, run --record {c}",
        "dep_historical": "{f} was sent before {c} changed ({b}). The sent file stays as it is; prepare for the interview from the current card",
        "dep_inherited": "{f}:{n}: copied unchanged from {base}, which was approved before {c} changed ({b}). Check this line against the current card",
        "dep_unchecked": "{f}: not checked against the current cards yet ({cs}). Older versions start this way; nothing to do until you reuse or send this one",
        "dep_unchecked_final": "{f}: {cs} not checked against the current cards. Before sending, show the user the lines citing them; once they confirm, run --record {cs}",
        "dep_edited": "edited after it was recorded",
        "rec_frozen": "{f} is frozen (sent). Its record can't change; make a new version instead",
        "rec_none": "{f}: none of {cs} is cited here, nothing recorded",
        "rec_skipped": "{f}: not recorded: {cs} (not cited here, or no longer a card)",
        "rec_blocked": "{f} has {e} error(s), so nothing was recorded. A record means the user approved these lines; fix the errors first",
        "dep_edited_final": "{f}: {c} changed since this version was approved ({b}), and the lines citing it were edited after that. Show the user those lines next to the card; once they confirm, run --record {c}",
        "rec_done": "Recorded {f} against the current version of {cs} (cv/reviewed.txt). Record only what the user has looked at",
        "delta_rejected": "{cl}: proposal #{k} was rejected, but its new text is in {f}:{n}. Take it out, or ask the user again",
        "delta_pending": "{cl}: {f} is Approved but proposal(s) {ks} are still Pending. Mark each Accepted or Rejected",
        "delta_stale": "{cl}: proposal #{k} is stale ({why}). Don't apply it as it is: propose it again against the current text and card",
        "stale_target": "its Before text is no longer in {b}",
        "stale_card": "{c} changed after it was proposed: {x}",
        "delta_rejected_short": "{cl}: proposal #{k} was rejected, and its short new text appears in {f} under \"{loc}\". A short phrase can change who did what: check that line",
        "delta_short_unsure": "{cl}: proposal #{k} was rejected, but its new text is too short to look for without a clear Location. Check by eye that it isn't in {f}",
        "delta_unquoted": "{cl}: proposal #{k} was rejected but has no quoted After text, so the script can't look for it. Check by eye that it isn't in {f}",
        "delta_conflict": "{cl}: proposals {ks} change the same text. Accept one; the others are stale once it's applied",
        "delta_unverified": "{cl}: proposal #{k} hasn't been checked against {cs}. Show the user the row next to the card; once they confirm, run --record P{k}",
        "in_section": "{b}, under \"{loc}\"",
        "how_approved": "approved",
        "how_recorded": "recorded",
        "major": "major",
        "minor": "minor",
        "ok": "OK: {n} lines checked, {c} Claim IDs used, no errors{w}",
        "fail": "FAILED: {e} error(s) in {f}",
        "scope": "Scope: this checks sourcing, numbers, banned words, roles/education and protected claims. It does not verify that each sentence is supported by its card, or check layout.",
    },
    "zh": {
        "no_file": "找不到文件：{p}",
        "no_claims": "在 {p} 里没有找到 Claim Card",
        "dup_id": "{c} 被多张卡使用（{f}），请给每张卡一个独立的 ID",
        "untagged": "{f}:{n}：这一行没有 Claim ID：{t}",
        "unknown": "{f}:{n}：{c} 找不到对应的 Claim Card",
        "status": "{f}:{n}：{c} 的状态是「{s}」，只有「Safe to draft」才能使用",
        "interview_only": "{f}:{n}：{c} 是「仅面试」：面试时可以讲，但不写进简历",
        "pending": "{f}:{n}：数字「{x}」在 {c} 上没有标 ✓。请本人确认后在卡上改成 ✓，或者删掉",
        "number": "{f}:{n}：数字「{x}」在 {c} 里找不到。请把它补进卡片的数字表（写明单位和口径），或者删掉",
        "currency": "{f}:{n}：「{x}」用的币种是 {cur}，但 {c} 上是 {want}",
        "banned": "{f}:{n}：「{w}」是 {c} 的禁用词（见卡上的「禁止改写」）",
        "dont": "{f}:{n}：「{w}」是 {c} 的「禁止改写」里提醒过的说法。请重读那条提醒，确认这一行说的还是卡上的事实",
        "no_sections": "{f}：没有识别到 Summary 或 Experience 栏目（找到的二级标题：{h}），什么都没检查",
        "nothing": "{f}：找到了 Summary/Experience 栏目，但里面没有可检查的行",
        "unchecked": "{f}：栏目「{s}」有 {k} 行，这个脚本不验证",
        "no_profile": "{f}：职位标题和教育背景还没检查：{p} 不存在或是空的。在那里填好任职和教育信息后，这项检查就会生效",
        "weak_number": "{f}:{n}：「{x}」不在 {c} 上。如果只是措辞可以不管；如果是数量，请补进卡片",
        "no_currency": "{f}:{n}：「{x}」带了币种，但 {c} 上没写是哪种。请在卡片的数字表里补上币种",
        "loose_number": "{f}：栏目「{s}」第 {n} 行有没有卡片支撑的数字：{t}",
        "waived": "{c}：本人已同意删减（front matter 里的 protected-ok），请在 Change Log 里写明原因",
        "role": "{f}:{n}：职位标题和 {p} 里的任职对不上（职位、公司、年份）：{t}",
        "education": "{f}:{n}：教育这一行和 {p} 对不上（学位、学校、年份）：{t}",
        "dropped_protected": "受保护的 claim {c} 在基线（{b}）里用到了，这里的 Summary/Experience 却没有。请补回；或经本人同意后在 front matter 里加 `protected-ok: {c}`，并在 Change Log 里说明原因",
        "weakened": "受保护的 claim {c}：基线（{b}）里写了 {x}，这一版没有了。请补回；或经本人同意后在 front matter 里加 `protected-ok: {c}`，并在 Change Log 里说明原因",
        "dropped": "{c} 在基线（{b}）里用到了，这里没有",
        "keep_for": "受保护的 claim {c} 只要求在类型 {k} 里保留；这份简历是类型 {ty}，可以不放。请在 Change Log 里写明原因",
        "base_missing": "找不到基线文件：{p}，受保护 claim 检查无法进行。请修正 `base:` 或用 --base 指定",
        "base_required": "{f}：没有写 `base:`，但 CV-INDEX 里类型 {ty} 已经有起点（{s}）。请把 `base:` 设为这份简历复制自的版本",
        "frozen": "{f} 投递时已冻结（cv/frozen.txt），之后又被改过。请恢复原样，要改就复制成一个新版本（D-010）",
        "table_gap": "{f}：{cl} 的证据表没有提到 {cs}。请看一下这些卡；用不上的写进表里并说明原因，没用的卡可以合成一行（D-019）",
        "dep_changed": "{f}：这一版{how}之后，{c} 改过（{b}）。需要复核：对照卡片看一遍引用 {c} 的行，本人确认后运行 --record {c}",
        "dep_changed_final": "{f}：这一版批准之后，{c} 有尚未处理的重大变化（{b}）。这不代表简历有错，只是还没人对照改过的卡检查过。请把引用 {c} 的行给本人看，确认后运行 --record {c}",
        "dep_historical": "{f} 是在 {c} 改动（{b}）之前投出去的。已投递的文件保持原样；准备面试时以现在的卡为准",
        "dep_inherited": "{f}:{n}：这一行原样复制自 {base}，而那一版批准时 {c} 还没改（{b}）。请对照现在的卡检查这一行",
        "dep_unchecked": "{f}：还没有对照现在的卡记录过（{cs}）。旧版本一开始都是这样，等再次复用或投递时再处理",
        "dep_unchecked_final": "{f}：{cs} 还没有对照现在的卡确认过。投递前请把引用它们的行给本人看，确认后运行 --record {cs}",
        "dep_edited": "记录之后被改过",
        "rec_frozen": "{f} 已冻结（已投递），它的记录不能再改；要改请复制成新版本",
        "rec_none": "{f}：这里没有引用 {cs}，没有记录任何内容",
        "rec_skipped": "{f}：没有记录 {cs}（这里没有引用，或者已经不是一张卡）",
        "rec_blocked": "{f} 有 {e} 个错误，所以没有记录。记录的意思是本人批准了这些行；请先改掉错误",
        "dep_edited_final": "{f}：这一版批准之后 {c} 改过（{b}），而且引用它的行在那之后也改过。请把这些行和卡一起给本人看，确认后运行 --record {c}",
        "rec_done": "已记录：{f} 对照的是 {cs} 的当前版本（cv/reviewed.txt）。只记录本人看过的内容",
        "delta_rejected": "{cl}：第 {k} 条修改提案已被拒绝，但它的新文本出现在 {f}:{n}。请删掉，或者再问一次本人",
        "delta_pending": "{cl}：{f} 已是 Approved，但第 {ks} 条提案还是待定。请把每条标成接受或拒绝",
        "delta_stale": "{cl}：第 {k} 条提案已过期（{why}）。不要照原样采用：请对照现在的文本和卡重新提",
        "stale_target": "它的 Before 原文已经不在 {b} 里",
        "stale_card": "{c} 在提案之后改过：{x}",
        "delta_rejected_short": "{cl}：第 {k} 条提案已被拒绝，它很短的新文本出现在 {f} 的「{loc}」里。一个短词也可能改变谁做了什么：请看一下那一行",
        "delta_short_unsure": "{cl}：第 {k} 条提案已被拒绝，但新文本太短，位置又不明确，脚本没法查。请自己看一下 {f} 里有没有",
        "delta_unquoted": "{cl}：第 {k} 条提案已被拒绝，但没有引号里的 After 文本，脚本没法查。请自己看一下 {f} 里有没有",
        "delta_conflict": "{cl}：第 {ks} 条提案改的是同一段文字。只接受一条；采用之后其余的就过期了",
        "delta_unverified": "{cl}：第 {k} 条提案还没有对照 {cs} 检查过。请把这一行和卡一起给本人看，确认后运行 --record P{k}",
        "in_section": "{b} 的「{loc}」里",
        "how_approved": "批准",
        "how_recorded": "记录",
        "major": "重大",
        "minor": "一般",
        "ok": "通过：检查了 {n} 行，用到 {c} 个 Claim ID，没有错误{w}",
        "fail": "未通过：{f} 里有 {e} 个错误",
        "scope": "范围：这里检查出处、数字、禁用词、职位/教育和受保护的 claim，不验证每句话是否真的由对应的卡支持，也不检查排版。",
    },
}

ID_RE = re.compile(r"\b[A-Za-z]+-\d+\b")
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")

CUR = r"US\$|USD|EUR|€|£|GBP|HK\$|HKD|S\$|SGD|RMB|CNY|¥|\$"
CUR_SUFFIX = r"USD|EUR|GBP|HKD|SGD|RMB|CNY|美元|欧元|英镑|港币|港元|新币|人民币|元"
NUM_RE = re.compile(
    r"(?<![\w.$€£¥])(" + CUR + r")?\s?(\d[\d,]*(?:\.\d+)?)"
    r"(\s*(?:%|x|X|×|倍|万|亿|千|[kKmMbB](?![a-zA-Z])))?"
    r"(?:\s?(" + CUR_SUFFIX + r")(?![a-zA-Z]))?")
CURRENCY = {"us$": "USD", "usd": "USD", "$": "USD", "美元": "USD", "eur": "EUR", "€": "EUR", "欧元": "EUR",
            "£": "GBP", "gbp": "GBP", "英镑": "GBP", "hk$": "HKD", "hkd": "HKD", "港币": "HKD", "港元": "HKD",
            "s$": "SGD", "sgd": "SGD", "新币": "SGD", "rmb": "CNY", "cny": "CNY", "¥": "CNY", "人民币": "CNY", "元": "CNY"}
SCALE = {"k": 1e3, "千": 1e3, "m": 1e6, "b": 1e9, "万": 1e4, "亿": 1e8}
WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}
WORD_RE = re.compile(r"\b(" + "|".join(WORDS) + r")\b", re.I)

SECTIONS = {
    "summary": {
        "summary", "profile", "professional summary", "executive summary", "career summary",
        "professional profile", "about", "about me", "overview",
        "概要", "简介", "个人简介", "个人概要", "个人总结", "职业概要", "摘要", "自我评价",
    },
    "experience": {
        "experience", "work experience", "professional experience", "employment",
        "employment history", "work history", "career history", "relevant experience",
        "工作经历", "工作经验", "职业经历", "从业经历", "经历", "经验", "实习经历",
    },
    "claims": {
        "projects", "selected projects", "key projects", "achievements", "key achievements",
        "selected achievements", "accomplishments", "highlights", "career highlights", "awards",
        "项目", "项目经历", "项目经验", "主要成就", "成就", "主要业绩", "业绩", "获奖", "荣誉",
    },
}
EDUCATION_SECTIONS = {"education", "教育", "教育背景", "教育经历"}
SKIP_SECTIONS = {
    "languages", "language", "contact", "references",
    "语言", "语言能力", "联系方式",
}

# Claim Card sections whose numbers are NOT a source for a resume line.
CARD_NOT_SOURCE = {"don't rephrase as", "don’t rephrase as", "dont rephrase as", "source", "to fill",
                   "禁止改写", "出处", "待补"}
DONT_SECTIONS = {"don't rephrase as", "don’t rephrase as", "dont rephrase as", "禁止改写"}
QUOTED_RE = re.compile(r'"([^"\n]{2,60})"|“([^”\n]{2,60})”|「([^」\n]{1,60})」')
BANNED_RE = re.compile(r"^\s*(?:[-*]\s*)?\**(?:banned words|禁用词)\**\s*[:：]\s*(.+)$", re.I)
VERIFIED_OK = {"✓", "✔", "✔️", "✅", "confirmed", "yes", "已核实", "已确认", "是"}
VERIFY_HEADERS = {"核实", "verified"}


def section_kind(title):
    t = re.sub(r"\s+", " ", title.strip().strip(":：").lower())
    for kind, names in SECTIONS.items():
        if t in names:
            return kind
    if t in EDUCATION_SECTIONS:
        return "education"
    if t in SKIP_SECTIONS:
        return "skip"
    return "other"


def front_matter(text):
    """Return (dict, body_start_line_index). Parses simple `key: value` lines; `# …` is a comment."""
    lines = text.split("\n")
    data, end = {}, 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i + 1
                break
            m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", lines[i])
            if m:
                value = m.group(2)
                value = "" if value.startswith("#") else re.sub(r"\s+#.*$", "", value)
                data[m.group(1)] = value.strip()
    return data, end


def normalize_number(n):
    return n.replace(",", "")


def tokens(text):
    """Numbers in a piece of text: list of (shown, plain, value, scaled, currency, kind)."""
    out = []
    for m in NUM_RE.finditer(text):
        cur, n, unit, cur2 = m.group(1) or "", m.group(2), (m.group(3) or "").strip(), m.group(4) or ""
        plain = normalize_number(n)
        try:
            v = float(plain)
        except ValueError:
            continue
        scale = SCALE.get(unit.lower(), 1)
        currency = CURRENCY.get((cur or cur2).lower(), "")
        kind = "pct" if unit == "%" else "mult" if unit.lower() in ("x", "×", "倍") else ""
        out.append((m.group(0).strip(), plain, v * scale, scale != 1, currency, kind))
    for m in WORD_RE.finditer(text):
        v = WORDS[m.group(1).lower()]
        out.append((m.group(1), str(v), float(v), False, "", "word"))
    return out


def is_year(tok):
    _, plain, v, scaled, currency, kind = tok
    return not scaled and not currency and not kind and plain.isdigit() and len(plain) == 4 and 1900 <= v <= 2099


def same(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def parse_tables(lines):
    """Yield (header_cells_lower, [row_cells]) for each markdown table in lines."""
    tables, cur = [], None
    for line in lines + [""]:
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cur is None:
                cur = ([c.lower() for c in cells], [])
            elif not set(s) <= set("|-: "):
                cur[1].append(cells)
        elif cur is not None:
            tables.append(cur)
            cur = None
    return tables


def load_card(text):
    fm, start = front_matter(text)
    cid = fm.get("id", "")
    lines = text.split("\n")[start:]
    source_text, banned, warned, section = [], [], [], ""
    numbers_lines = []
    for line in lines:
        h = HEADING_RE.match(line.strip())
        if h:
            if len(h.group(1)) == 1:
                source_text.append(h.group(2).replace(cid, " ") if cid else h.group(2))
            else:
                section = h.group(2).strip().lower()
            continue
        if section in CARD_NOT_SOURCE:
            b = BANNED_RE.match(line)
            if b:
                banned += [w.strip().strip("\"'“”「」`").lower() for w in re.split(r"[,，、;；]", b.group(1)) if w.strip()]
            elif section in DONT_SECTIONS:
                # quoted wording the card warns against, e.g. Don't write "built" -> a WARN, not an error
                for m in QUOTED_RE.finditer(line):
                    q = next(g for g in m.groups() if g).strip(" .,;:，。；：").lower()
                    if re.search(r"[a-z\u4e00-\u9fff]", q) and q not in warned:
                        warned.append(q)
            continue
        if line.strip().startswith("|") and section in ("numbers and what they mean", "数字与口径"):
            numbers_lines.append(line)
        else:
            source_text.append(line)

    card = {"status": fm.get("status", ""), "protected": fm.get("protected", "").lower() == "true",
            "keep_for": {x.strip() for x in re.split(r"[,，、\s]+", fm.get("keep-for", "")) if x.strip()},
            "vals": [], "years": set(), "currency": [], "pending": [], "banned": banned, "warned": warned}

    def add(toks, pending=False, currency=""):
        for t in toks:
            card["vals"].append(t[2])
            if pending:
                card["pending"].append(t[2])
            cur = t[4] or currency
            if cur:
                card["currency"].append((t[2], cur))

    add(tokens("\n".join(source_text)))
    for part in re.findall(r"\d+", fm.get("period", "")):
        card["years"].add(part)
    for header, rows in parse_tables(numbers_lines):
        vcol = next((i for i, c in enumerate(header) if c in VERIFY_HEADERS), None)
        tcol = next((i for i, c in enumerate(header) if "time" in c or "时间" in c or "period" in c), None)
        ucol = next((i for i, c in enumerate(header) if "unit" in c or "currency" in c or "单位" in c or "币种" in c), None)
        for cells in rows:
            if not cells:
                continue
            # A blank Verified cell counts as confirmed: the user gave the number (validate_evidence.py
            # reminds them to tick it). Only an explicit other value, like "to verify", holds it back.
            ok = vcol is None or vcol >= len(cells) or not cells[vcol].strip() or cells[vcol].strip().lower() in VERIFIED_OK
            unit_cur = ""
            if ucol is not None and ucol < len(cells):
                for word, code in CURRENCY.items():
                    if re.search(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])", cells[ucol].lower()):
                        unit_cur = code
                        break
            add(tokens(cells[0]), pending=not ok, currency=unit_cur)
            if tcol is not None and tcol < len(cells):
                card["years"].update(re.findall(r"\d+", cells[tcol]))
    # A value is pending only if no confirmed source on the card also gives it.
    confirmed = [v for v in card["vals"] if not any(same(v, p) for p in card["pending"])]
    card["pending"] = [p for p in card["pending"] if not any(same(p, c) for c in confirmed)]
    return cid, card


def load_claims(folder):
    claims, files, dups = {}, {}, {}
    for f in sorted(Path(folder).glob("*.md")):
        if f.name.startswith("_"):
            continue
        cid, card = load_card(f.read_text(encoding="utf-8"))
        if not cid:
            continue
        if cid in claims:
            dups.setdefault(cid, [files[cid]]).append(f.name)
        claims[cid], files[cid] = card, f.name
    return claims, dups


def load_profile(path):
    """evidence/profile.md: tables of roles (title, company, start, end) and education (degree, school, year)."""
    roles, edu = [], []
    if not path or not path.is_file():
        return None
    for header, rows in parse_tables(path.read_text(encoding="utf-8").split("\n")):
        def col(*names):
            return next((i for i, c in enumerate(header) if any(n in c for n in names)), None)
        title, company, school, degree = col("title", "职位"), col("company", "公司"), col("school", "学校"), col("degree", "学位")
        for cells in rows:
            get = lambda i: cells[i].strip() if i is not None and i < len(cells) else ""
            nums = set(re.findall(r"\d+(?:\.\d+)?", " ".join(cells)))
            nums |= set(re.findall(r"\d+", " ".join(cells)))
            if title is not None and company is not None and get(title) and get(company):
                roles.append((alts(get(title)), alts(get(company)), nums))
            elif school is not None and degree is not None and get(school) and get(degree):
                edu.append((alts(get(degree)), alts(get(school)), nums))
    return roles, edu


def squash(text):
    """Lower case, letters and digits only: "B.A., Economics" and "BA Economics" compare equal."""
    return re.sub(r"[\W_]+", "", text.lower())


def alts(cell):
    """A profile cell may list accepted variants separated by ";" (e.g. a title in English and Chinese)."""
    return [squash(x) for x in re.split(r"[;；]", cell) if squash(x)]


def matches_profile(text, entries):
    low = squash(text)
    nums = set(re.findall(r"\d+(?:\.\d+)?", text))
    return any(any(x in low for x in a) and any(x in low for x in b) and nums <= n for a, b, n in entries)


def scan_resume(path):
    """Return dict with:
    needs: [line_no, text, ids] lines that must carry Claim IDs;
    used: ids used in Summary/Experience/Projects; recognized: count of recognized sections;
    headings: level-2 headings; unchecked: {section: lines}; roles / education: [(line_no, text)]."""
    text = path.read_text(encoding="utf-8")
    fm, start = front_matter(text)
    lines = text.split("\n")
    needs, used = [], set()
    headings, recognized, unchecked = [], 0, {}
    roles, education, loose = [], [], []
    kind, title, in_comment, last_bullet = "", "", False, None
    for idx in range(start, len(lines)):
        raw = lines[idx]
        line = raw
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
            else:
                continue
        ids = []
        for m in COMMENT_RE.finditer(line):
            ids += ID_RE.findall(m.group(1))
        line_no_comments = COMMENT_RE.sub("", line)
        if "<!--" in line_no_comments:  # a comment that opens here and closes later
            line_no_comments = line_no_comments.split("<!--", 1)[0]
            in_comment = True
        text_only = line_no_comments.strip()
        h = HEADING_RE.match(text_only)
        if h:
            last_bullet = None
            level = len(h.group(1))
            if level <= 2:
                title = h.group(2).strip()
                kind = section_kind(title) if level == 2 else ""
                if level == 2:
                    headings.append(title)
                    if kind in SECTIONS:
                        recognized += 1
            elif kind in ("experience", "claims") and not ids:
                roles.append((idx + 1, h.group(2).strip()))
            elif kind == "education":
                education.append((idx + 1, h.group(2).strip()))
            continue
        if not text_only:
            if not ids:
                last_bullet = None
            continue
        is_bullet = bool(BULLET_RE.match(raw))
        body = BULLET_RE.sub("", text_only) if is_bullet else text_only
        if kind in ("summary", "experience", "claims"):
            if not is_bullet and raw[:1] in (" ", "\t") and last_bullet is not None:
                # continuation of the bullet above: read as one claim
                entry = needs[last_bullet]
                entry[1] = entry[1] + " " + body
                entry[2] = entry[2] + ids
                used.update(ids)
                continue
            if kind == "experience" and not is_bullet and not ids and not tokens(body):
                # a plain line with no number and no tag (company blurb, location): listed, not an error
                unchecked[title] = unchecked.get(title, 0) + 1
                last_bullet = None
                continue
            needs.append([idx + 1, body, ids])
            used.update(ids)
            last_bullet = len(needs) - 1 if is_bullet else None
        elif kind == "education":
            education.append((idx + 1, body))
        elif kind == "other":
            if ids:  # tagged lines are validated
                needs.append([idx + 1, body, ids])
            else:
                unchecked[title] = unchecked.get(title, 0) + 1
                if tokens(body):
                    loose.append((idx + 1, title, body))
    return {"fm": fm, "needs": needs, "used": used, "recognized": recognized, "headings": headings,
            "unchecked": unchecked, "roles": roles, "education": education, "loose": loose}


def cv_index_rule(resume, fm):
    """If cv/CV-INDEX.md lists a starting point for this resume's type and this file isn't in its
    resume list, the resume must name a baseline. Returns (type, starting point) or None."""
    index = resume.parent.parent / "CV-INDEX.md"
    if not index.is_file():
        return None
    starts, listed = {}, set()
    for header, rows in parse_tables(index.read_text(encoding="utf-8").split("\n")):
        joined = " ".join(header)
        if "starting point" in joined or "当前起点" in joined:
            for cells in rows:
                if len(cells) >= 2:
                    starts[cells[0].strip()] = cells[1].strip()
        elif header and header[0] in ("file", "文件"):
            for cells in rows:
                if cells and cells[0].strip():
                    listed.add(Path(cells[0].strip().strip("`")).stem)
    if resume.stem in listed or fm.get("id", "") in listed:
        return None
    wanted = [fm["type"]] if fm.get("type") else list(starts)
    for ty in wanted:
        s = starts.get(ty, "")
        if s and not s.startswith(("(", "（", "-")):
            return ty, s
    return None


def frozen_entry(resume):
    """The hash cv/frozen.txt (written by scripts/freeze.py) records for this file, or None."""
    record = resume.parent.parent / "frozen.txt"
    if not record.is_file():
        return None
    root, me = resume.resolve().parent.parent.parent, resume.resolve()
    for line in record.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and (root / parts[1].lstrip("*").strip()).resolve() == me:
            return parts[0]
    return None


EVIDENCE_HEADINGS = ("evidence table", "证据表")


def find_changelog(resume, fm):
    """The Change Log for this resume: one whose front matter says `resume: <id>`, or that names
    cv/resumes/<id>.md. None if there isn't exactly one."""
    folder = resume.parent.parent / "changelogs"
    if not folder.is_dir():
        return None
    rid = fm.get("id") or resume.stem
    hits = []
    for p in sorted(folder.glob("*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        if front_matter(text)[0].get("resume", "").strip() == rid or f"cv/resumes/{resume.name}" in text:
            hits.append(p)
    return hits[0] if len(hits) == 1 else None


def evidence_table_ids(path):
    """IDs mentioned in a Change Log's evidence-table section, or None if it has no such section."""
    ids, inside, found = set(), False, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith(EVIDENCE_HEADINGS)
            found = found or inside
        elif inside:
            ids |= set(ID_RE.findall(line))
    return ids if found else None


DELTA_HEADINGS = ("delta",)
PROPOSAL_STATUS = {"pending": "pending", "待定": "pending", "accepted": "accepted", "接受": "accepted", "已接受": "accepted",
                   "rejected": "rejected", "拒绝": "rejected", "已拒绝": "rejected"}


def quoted(cell):
    """Text in quotes in a cell ("…", “…” or 「…」), or "" if there's none."""
    found = [next(g for g in m.groups() if g) for m in QUOTED_LONG_RE.finditer(cell)]
    return " ".join(found)


QUOTED_LONG_RE = re.compile(r'"([^"\n]+)"|“([^”\n]+)”|「([^」\n]+)」')


def sections_of(text):
    """[(normalized heading, normalized text under it)] for every ##-or-deeper heading; a section holds
    its sub-sections too. Used to look for a proposal's text where its Location says."""
    lines = text.split("\n")
    heads = [(i, len(m.group(1)), deps.normalize(m.group(2)).lower())
             for i, l in enumerate(lines) if (m := re.match(r"^(#{2,6})\s+(.*?)\s*$", l))]
    out = []
    for n, (i, level, title) in enumerate(heads):
        end = next((j for j, lv, _ in heads[n + 1:] if lv <= level), len(lines))
        out.append((title, deps.normalize("\n".join(lines[i + 1:end]))))
    return out


def section_for(loc, secs):
    """The one section whose heading contains the Location, or None when it can't be told which."""
    key = deps.normalize(loc).lower()
    hits = [body for title, body in secs if key and key in title]
    return hits[0] if len(hits) == 1 else None


def delta_rows(path):
    """Proposals in a Change Log's Delta table: [{n, loc, before, after, ids, status, text}]. Only a table with a
    Status column counts; an older Change Log without one returns []. Before/After are the quoted text on each
    side of the arrow, so they can be looked up in a file; unquoted descriptions are left empty."""
    lines, inside = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith(DELTA_HEADINGS)
        elif inside:
            lines.append(line)
    out = []
    for header, rows in parse_tables(lines):
        scol = next((i for i, c in enumerate(header) if c in ("status", "状态")), None)
        if scol is None:
            continue
        ncol = next((i for i, c in enumerate(header) if c in ("#", "no.", "编号")), None)
        lcol = next((i for i, c in enumerate(header) if "location" in c or "位置" in c), None)
        ccol = next((i for i, c in enumerate(header) if "change" in c or "改动" in c), None)
        bcol = next((i for i, c in enumerate(header) if "basis" in c or "依据" in c), None)
        for k, cells in enumerate(rows, 1):
            get = lambda i: cells[i].strip() if i is not None and i < len(cells) else ""
            status = PROPOSAL_STATUS.get(get(scol).strip("* ").lower(), "")
            change = get(ccol)
            before, _, after = change.partition("→")
            out.append({"n": get(ncol) or str(k), "loc": get(lcol), "before": quoted(before), "after": quoted(after),
                        "ids": ID_RE.findall(get(bcol) + " " + change), "status": status,
                        "text": "\n".join([get(lcol), change, get(bcol)])})
    return out


def frozen_changed(resume):
    """True if cv/frozen.txt (written by scripts/freeze.py) lists this file with a different hash."""
    import hashlib
    want = frozen_entry(resume)
    return want is not None and hashlib.sha256(resume.read_bytes()).hexdigest() != want


def lines_for(needs, cid):
    """The checked lines that cite this card."""
    return [text for _, text, ids in needs if cid in ids]


def numbers_for(needs, cid):
    vals = []
    for _, text, ids in needs:
        if cid in ids:
            vals += [t[2] for t in tokens(text) if not is_year(t)]
    return vals


def main():
    ap = argparse.ArgumentParser(description="对照证据库检查一份简历。")
    ap.add_argument("resume")
    ap.add_argument("--base", help="baseline resume file (default: `base:` in the front matter)")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--profile", help="profile file (default: profile.md next to the claims folder)")
    ap.add_argument("--changelog", help="this version's Change Log (default: the one in cv/changelogs/ that names this resume)")
    ap.add_argument("--finalize", action="store_true", help="准备投递：卡片有未处理的重大变化，或有卡没检查过，就算错误（D-020）")
    ap.add_argument("--record", metavar="IDS", help="本人批准或确认复核之后：把这些 Claim ID（或 all）当前的卡片版本记到 cv/reviewed.txt")
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]

    resume = Path(a.resume)
    if not resume.is_file():
        print(t["no_file"].format(p=a.resume)); return 2
    claims, dups = load_claims(a.claims) if Path(a.claims).is_dir() else ({}, {})
    if not claims:
        print(t["no_claims"].format(p=a.claims)); return 2

    errors, warns = 0, 0
    if frozen_changed(resume):
        print("ERROR " + t["frozen"].format(f=resume.name)); errors += 1
    for c, files in sorted(dups.items()):
        print("ERROR " + t["dup_id"].format(c=c, f=", ".join(files))); errors += 1

    r = scan_resume(resume)
    needs, used = r["needs"], r["used"]
    checked = 0
    fps, root = deps.load_cards(a.claims), deps.kit_root(a.claims)
    me = deps.rel(resume, root)

    # D-020: which cards this file cites. Every tagged line counts (Summary, Experience and any other
    # section), and so does a card that was deleted after this file was recorded.
    records = deps.read_records(root)
    mine = {c for p, c in records if p == me}
    is_resume = resume.parent.name == "resumes"
    if is_resume:
        cites = {c: lines_for(needs, c) for c in sorted({c for _, _, ids in needs for c in ids}) if deps.is_cited(c, fps, mine, tagged=True)}
    else:  # a follow-up card or an answer: the sections that name each card
        cites = deps.asset_citations(me, resume.read_text(encoding="utf-8"), set(fps), ())

    def record():
        # A record says "the user has looked at these lines against this version of the card".
        want = set(cites) if a.record.strip().lower() in ("all", "全部") else set(ID_RE.findall(a.record))
        cited = sorted(want & set(cites) & set(fps))
        if not cited:
            print(t["rec_none"].format(f=resume.name, cs=", ".join(sorted(want)) or "-")); return 1
        deps.write_records(root, me, {c: dict(fps[c], lines=deps.lines_hash(cites[c])) for c in cited})
        print(t["rec_done"].format(f=resume.name, cs=", ".join(cited)))
        if want - set(cited):
            print(t["rec_skipped"].format(f=resume.name, cs=", ".join(sorted(want - set(cited)))))
        return 0

    def record_rows(rows):
        # one record per proposal row, so confirming one never refreshes another: --record P2, --record all
        every = a.record.strip().lower() in ("all", "全部")
        sel = {m for m in re.findall(r"(?<![A-Za-z])[Pp]?(\d+)\b", a.record)}
        done, skipped = [], []
        for r_ in rows:
            if not every and r_["n"] not in sel:
                continue
            cards_ = sorted({c for c in r_["ids"] if c in fps})
            if not cards_:
                skipped.append("P" + r_["n"]); continue
            lh = deps.lines_hash(r_["text"].split("\n"))
            deps.write_records(root, f"{me}#{r_['n']}", {c: dict(fps[c], lines=lh) for c in cards_})
            done.append("P" + r_["n"])
        if not done:
            print(t["rec_none"].format(f=resume.name, cs=", ".join(skipped) or a.record)); return 1
        print(t["rec_done"].format(f=resume.name, cs=", ".join(done)))
        if skipped:
            print(t["rec_skipped"].format(f=resume.name, cs=", ".join(skipped)))
        return 0

    if a.record:
        if frozen_entry(resume) is not None or r["fm"].get("status", "").strip().lower() == "sent":
            print(t["rec_frozen"].format(f=resume.name)); return 1
        if not is_resume:
            if errors:  # e.g. a duplicate card ID: which card the file means is unknowable
                print(t["rec_blocked"].format(f=resume.name, e=errors)); return 1
            rows_ = delta_rows(resume)
            return record_rows(rows_) if rows_ else record()
        # a resume is recorded only if it passes the check below
    if not r["recognized"]:
        print("ERROR " + t["no_sections"].format(f=resume.name, h=", ".join(r["headings"]) or "-")); errors += 1
    for n, text, ids in needs:
        short = text if len(text) <= 60 else text[:57] + "..."
        checked += 1
        if not ids:
            print("ERROR " + t["untagged"].format(f=resume.name, n=n, t=short)); errors += 1
            continue
        known = []
        for c in ids:
            if c not in claims:
                print("ERROR " + t["unknown"].format(f=resume.name, n=n, c=c)); errors += 1
            elif c in dups:
                pass  # already reported; which card is meant is unknowable
            elif claims[c]["status"].strip().lower() in ("仅面试", "interview only"):
                print("ERROR " + t["interview_only"].format(f=resume.name, n=n, c=c)); errors += 1
            elif claims[c]["status"].strip().lower() != "safe to draft":
                print("ERROR " + t["status"].format(f=resume.name, n=n, c=c, s=claims[c]["status"])); errors += 1
            else:
                known.append(c)
        if not known:
            continue
        cards = [claims[c] for c in known]
        cited = ", ".join(known)
        low = text.lower()
        for c in known:
            for w in claims[c]["banned"]:
                hit = (w in low) if re.search(r"[^\x00-\x7f]", w) else re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)
                if w and hit:
                    print("ERROR " + t["banned"].format(f=resume.name, n=n, w=w, c=c)); errors += 1
            for w in claims[c].get("warned", []):
                if w in claims[c]["banned"]:
                    continue
                hit = (w in low) if re.search(r"[^\x00-\x7f]", w) else re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)
                if hit:
                    print("WARN  " + t["dont"].format(f=resume.name, n=n, w=w, c=c)); warns += 1
        for tok in tokens(text):
            shown, plain, v, scaled, currency, kind = tok
            if kind == "word" and v < 2:
                continue  # "one"/"zero" are too common in plain prose to check
            found = [card for card in cards if any(same(v, x) for x in card["vals"])]
            if not found and is_year(tok) and any(plain in card["years"] for card in cards):
                continue
            if not found:
                if kind == "word" or (plain.isdigit() and len(plain) == 1 and not scaled and not currency and not kind):
                    # a lone digit or number word is often just wording ("two teams", "3-tier")
                    print("WARN  " + t["weak_number"].format(f=resume.name, n=n, x=shown, c=cited)); warns += 1
                else:
                    print("ERROR " + t["number"].format(f=resume.name, n=n, x=shown, c=cited)); errors += 1
                continue
            if all(any(same(v, p) for p in card["pending"]) for card in found):
                hold = ", ".join(c for c in known if claims[c] in found)
                print("ERROR " + t["pending"].format(f=resume.name, n=n, x=shown, c=hold)); errors += 1
                continue
            if currency:
                want = {cur for card in found for (x, cur) in card["currency"] if same(x, v)}
                if not want:
                    print("WARN  " + t["no_currency"].format(f=resume.name, n=n, x=shown, c=cited)); warns += 1
                elif currency not in want:
                    print("ERROR " + t["currency"].format(f=resume.name, n=n, x=shown, cur=currency,
                                                          c=cited, want="/".join(sorted(want)))); errors += 1
    if r["recognized"] and not checked:
        print("ERROR " + t["nothing"].format(f=resume.name)); errors += 1
    for s, k in r["unchecked"].items():
        print("WARN  " + t["unchecked"].format(f=resume.name, s=s, k=k)); warns += 1
    for n, s, text in r["loose"]:
        print("WARN  " + t["loose_number"].format(f=resume.name, s=s, n=n, t=text)); warns += 1

    # roles and education vs evidence/profile.md
    if r["roles"] or r["education"]:
        ppath = Path(a.profile) if a.profile else Path(a.claims).parent / "profile.md"
        profile = load_profile(ppath)
        if not profile or not (profile[0] or profile[1]):
            print("WARN  " + t["no_profile"].format(f=resume.name, p=ppath)); warns += 1
        else:
            for n, text in r["roles"]:
                if not matches_profile(text, profile[0]):
                    print("ERROR " + t["role"].format(f=resume.name, n=n, p=ppath.name, t=text)); errors += 1
            for n, text in r["education"]:
                if not matches_profile(text, profile[1]):
                    print("ERROR " + t["education"].format(f=resume.name, n=n, p=ppath.name, t=text)); errors += 1

    # protected claims vs the baseline
    fm = r["fm"]
    b = None
    base = Path(a.base) if a.base else (resume.parent / (fm["base"] + ".md") if fm.get("base") else None)
    if base is None:
        rule = cv_index_rule(resume, fm)
        if rule:
            print("ERROR " + t["base_required"].format(f=resume.name, ty=rule[0], s=rule[1])); errors += 1
    elif not base.is_file():
        print("ERROR " + t["base_missing"].format(p=base)); errors += 1
    else:
        b = scan_resume(base)
        waived = set(ID_RE.findall(fm.get("protected-ok", "")))
        for c in sorted(waived & b["used"]):
            print("NOTE  " + t["waived"].format(c=c))
        for c in sorted(b["used"] - used):
            if c in waived:
                continue
            if c in claims and claims[c]["protected"] and claims[c]["keep_for"] and fm.get("type", "") not in claims[c]["keep_for"]:
                print("NOTE  " + t["keep_for"].format(c=c, k=", ".join(sorted(claims[c]["keep_for"])), ty=fm.get("type", "") or "-"))
            elif c in claims and claims[c]["protected"]:
                print("ERROR " + t["dropped_protected"].format(c=c, b=base.name)); errors += 1
            else:
                print("NOTE  " + t["dropped"].format(c=c, b=base.name))
        for c in sorted(b["used"] & used):
            if c not in claims or not claims[c]["protected"] or c in waived:
                continue
            now = numbers_for(needs, c)
            gone = []
            for v in numbers_for(b["needs"], c):
                # only this card's own numbers: a line citing two cards also holds the other card's
                if not any(same(v, x) for x in claims[c]["vals"]):
                    continue
                if not any(same(v, x) for x in now) and not any(same(v, g) for g in gone):
                    gone.append(v)
            if gone:
                shown = ", ".join(("%g" % v) for v in gone)
                print("ERROR " + t["weakened"].format(c=c, b=base.name, x=shown)); errors += 1

    # D-019: every card is looked at for every job. Only a reminder: a sent (frozen) version and a
    # Change Log without an evidence table (older versions) are skipped.
    cl = Path(a.changelog) if a.changelog else find_changelog(resume, fm)
    if cl and cl.is_file() and frozen_entry(resume) is None:
        listed = evidence_table_ids(cl)
        if listed is not None:
            missing = sorted(c for c in claims if c not in listed)
            if missing:
                print("WARN  " + t["table_gap"].format(f=resume.name, cl=cl.name, cs=", ".join(missing))); warns += 1

    if a.record:
        if errors:
            print(t["rec_blocked"].format(f=resume.name, e=errors)); return 1
        return record()

    # D-020: did a card this version cites change after it was approved? Worked out fresh each run;
    # nothing is written to the resume. A sent version is history: it's only noted.
    status = fm.get("status", "").strip().lower()
    frozen = frozen_entry(resume) is not None or status == "sent"
    names = BLOCK_NAMES[a.lang]
    how = t["how_approved"] if status in ("approved", "sent") else t["how_recorded"]

    def what(d):
        return ", ".join(names.get(x, x) for x in d["blocks"]) + " · " + (t["major"] if d["major"] else t["minor"]) + \
            (" · " + t["dep_edited"] if d.get("edited") else "")

    unchecked, settled = [], set()
    for c in sorted(set(cites) & set(claims) & set(fps)):  # an unknown or deleted card is already an error above
        st, d = deps.card_state(records.get((me, c)), fps[c], cites[c], fm.get("type", ""))
        if st != "not_checked":
            settled.add(c)  # current, or already reported above: the copied-lines check below would repeat it
        if st == "current":
            pass
        elif st == "changed":
            if frozen:
                print("NOTE  " + t["dep_historical"].format(f=resume.name, c=c, b=what(d)))
            elif a.finalize and d["major"]:
                print("ERROR " + t["dep_changed_final"].format(f=resume.name, c=c, b=what(d))); errors += 1
            elif a.finalize and d["edited"]:
                print("ERROR " + t["dep_edited_final"].format(f=resume.name, c=c, b=what(d))); errors += 1
            else:
                print("WARN  " + t["dep_changed"].format(f=resume.name, c=c, how=how, b=what(d))); warns += 1
        else:
            unchecked.append(c)
    if unchecked and not frozen:
        if a.finalize:
            print("ERROR " + t["dep_unchecked_final"].format(f=resume.name, cs=", ".join(unchecked))); errors += 1
        elif status == "approved":
            print("NOTE  " + t["dep_unchecked"].format(f=resume.name, cs=", ".join(unchecked)))
    # A new version copied from its baseline carries the baseline's lines. If the baseline was
    # approved before a card changed, the copied lines still say what the old card said.
    if b is not None and not frozen:
        bme = deps.rel(base, root)
        for c in sorted((set(cites) & set(fps)) - settled):
            st, d = deps.card_state(records.get((bme, c)), fps[c], None, fm.get("type", ""))
            if st != "changed":
                continue
            old = {deps.normalize(x) for x in lines_for(b["needs"], c)}
            for n, text, ids in needs:
                if c in ids and deps.normalize(text) in old:
                    msg = t["dep_inherited"].format(f=resume.name, n=n, base=base.name, c=c, b=what(d))
                    if a.finalize and d["major"]:
                        print("ERROR " + msg); errors += 1
                    else:
                        print("WARN  " + msg); warns += 1

    # Proposals (the Change Log's Delta table, when it has a Status column). A rejected change must not be in
    # the resume, an Approved version has no undecided proposal, and a pending one is only valid while its
    # Before text (looked for under its Location when that names one section) is still in the baseline and
    # each card it rests on was checked for that row and hasn't had a major change since. Each row is recorded
    # on its own in cv/reviewed.txt as <change log>#<row>, so confirming one row never refreshes another.
    # All of this is worked out here, never written into the Change Log.
    if cl and cl.is_file() and not frozen:
        rows = delta_rows(cl)
        clme = deps.rel(cl, root)
        resume_lines = [(n, deps.normalize(text)) for n, text, _ in needs]
        resume_secs = sections_of(resume.read_text(encoding="utf-8"))
        base_ok = base is not None and base.is_file()
        base_text = deps.normalize(base.read_text(encoding="utf-8")) if base_ok else None
        base_secs = sections_of(base.read_text(encoding="utf-8")) if base_ok else []
        for r_ in rows:
            k, st = r_["n"], r_["status"]
            after = deps.normalize(r_["after"])
            if st == "rejected":
                if not after:
                    print("NOTE  " + t["delta_unquoted"].format(cl=cl.name, k=k, f=resume.name))
                elif len(after) >= 10:
                    hit = next((n for n, text in resume_lines if after in text), None)
                    if hit:
                        print("WARN  " + t["delta_rejected"].format(cl=cl.name, k=k, f=resume.name, n=hit)); warns += 1
                else:
                    where = section_for(r_["loc"], resume_secs)
                    if where is None:
                        print("NOTE  " + t["delta_short_unsure"].format(cl=cl.name, k=k, f=resume.name))
                    elif after in where:
                        print("WARN  " + t["delta_rejected_short"].format(cl=cl.name, k=k, f=resume.name, loc=r_["loc"])); warns += 1
            if st != "pending":
                continue
            whys, unchecked_cards = [], []
            before = deps.normalize(r_["before"])
            if before and base_text is not None:
                where = section_for(r_["loc"], base_secs)
                if before not in (base_text if where is None else where):
                    whys.append(t["stale_target"].format(b=base.name if where is None else t["in_section"].format(b=base.name, loc=r_["loc"])))
            key = f"{clme}#{r_['n']}"
            mine_row = {c for p_, c in records if p_ == key}
            for c in sorted({c for c in r_["ids"] if deps.is_cited(c, fps, mine_row)}):
                cst, d = deps.card_state(records.get((key, c)), fps.get(c), r_["text"].split("\n"), fm.get("type", ""))
                if cst == "changed" and d["major"]:  # a wording-only change to the card doesn't void the proposal
                    whys.append(t["stale_card"].format(c=c, x=what(d)))
                elif cst in ("missing", "not_checked") or (cst == "changed" and d["edited"]):
                    unchecked_cards.append(c)
            if whys:
                print("WARN  " + t["delta_stale"].format(cl=cl.name, k=k, why="; ".join(whys))); warns += 1
            elif unchecked_cards:  # not checked or no such card: not a valid proposal yet
                print("WARN  " + t["delta_unverified"].format(cl=cl.name, k=k, cs=", ".join(unchecked_cards))); warns += 1
        live = {}
        for r_ in rows:
            if r_["status"] in ("pending", "accepted") and r_["before"]:
                live.setdefault((deps.normalize(r_["loc"]).lower(), deps.normalize(r_["before"])), []).append(r_["n"])
        for ns in live.values():
            if len(ns) > 1:
                print("WARN  " + t["delta_conflict"].format(cl=cl.name, ks=", ".join("#" + n for n in ns))); warns += 1
        pending = [r_["n"] for r_ in rows if r_["status"] == "pending"]
        if pending and status == "approved":
            print("WARN  " + t["delta_pending"].format(cl=cl.name, f=resume.name, ks=", ".join(pending))); warns += 1

    if errors:
        print(t["fail"].format(e=errors, f=resume.name))
    else:
        print(t["ok"].format(n=checked, c=len(used), w=(f" ({warns} WARN)" if a.lang == "en" else f"（{warns} 条提醒）") if warns else ""))
    print(t["scope"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
