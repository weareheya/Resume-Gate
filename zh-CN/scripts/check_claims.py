#!/usr/bin/env python3
"""对照证据库检查一份简历。只用标准库，macOS、Linux、Windows 都能跑。

它检查什么（脚本能确定性判断的部分）：
  1. 简历里有脚本认得的 Summary 和/或 Experience 栏目（中英文常见写法都认，例如
     "Professional Summary"、"Work Experience"、"工作经历"）。一个都认不出来，或者里面没有
     可检查的内容时，判为未通过，不会再显示"通过"。
  2. "Experience" 下的每条 bullet、"Summary" 下的每一行，末尾都有 HTML 注释形式的 Claim ID，
     例如：  - 重建了伙伴计划 ... <!-- C-001 -->
  3. 每个 Claim ID 都能对上 evidence/claims/ 里的一张卡，且卡的状态是 "Safe to draft"。
  4. 被检查的行里出现的每个数字（数量、百分比、金额、倍数）都能在它引用的卡里找到。
     卡里没有的数字就是没有出处。
  5. 如果简历有基线（front matter 里的 `base:`，或 --base），基线文件必须存在；基线的
     Summary/Experience 里用到的 `protected: true` claim，在这份的 Summary/Experience 里也必须还在。
     把 Claim ID 塞在其他地方（Skills、零散注释）不算。
  其他非空栏目（Skills、Projects 等）会提示"未验证"，避免把通过误读成全面检查。
  Education、Languages、联系方式等栏目直接跳过。

它不检查什么：claim 是否属实、措辞有没有越过卡的「Don't rephrase as」限制、排版。
这些仍然要靠人和自审清单。

用法：
  python3 scripts/check_claims.py cv/resumes/<id>.md [--base cv/resumes/<基线id>.md]
                                  [--claims evidence/claims] [--lang en|zh]

退出码：0 = 没有错误，1 = 发现错误，2 = 没能运行（缺文件、用法错误）。
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_LANG = "zh"

T = {
    "en": {
        "no_file": "File not found: {p}",
        "no_claims": "No claim cards found in {p}",
        "untagged": "{f}:{n}: no Claim ID on this line: {t}",
        "unknown": "{f}:{n}: {c} does not match any Claim Card",
        "status": "{f}:{n}: {c} has status \"{s}\"; only \"Safe to draft\" can be used",
        "number": "{f}:{n}: the number \"{x}\" doesn't appear in {c}. Add it to the card's Numbers table (with its unit and basis), or remove it",
        "no_sections": "{f}: no Summary or Experience section recognized (level-2 headings found: {h}). Nothing could be checked",
        "nothing": "{f}: Summary/Experience sections found but they contain no lines to check",
        "unchecked": "{f}: section \"{s}\" has {k} line(s) this script does not verify",
        "dropped_protected": "Protected claim {c} is used in the baseline ({b}) but missing from Summary/Experience here. Restore it, or get the user's approval and explain why in the Change Log",
        "dropped": "{c} is used in the baseline ({b}) but not here",
        "base_missing": "Baseline file not found: {p}. The protected-claims check can't run. Fix `base:` or pass --base",
        "ok": "OK: {n} lines checked, {c} Claim IDs used, no errors",
        "fail": "FAILED: {e} error(s) in {f}",
        "scope": "Scope: this checks sourcing, numbers and protected claims only. It does not verify that claims are true, or check wording or layout.",
    },
    "zh": {
        "no_file": "找不到文件：{p}",
        "no_claims": "在 {p} 里没有找到 Claim Card",
        "untagged": "{f}:{n}：这一行没有 Claim ID：{t}",
        "unknown": "{f}:{n}：{c} 找不到对应的 Claim Card",
        "status": "{f}:{n}：{c} 的状态是「{s}」，只有「Safe to draft」才能使用",
        "number": "{f}:{n}：数字「{x}」在 {c} 里找不到。请把它补进卡片的数字表（写明单位和口径），或者删掉",
        "no_sections": "{f}：没有识别到 Summary 或 Experience 栏目（找到的二级标题：{h}），什么都没检查",
        "nothing": "{f}：找到了 Summary/Experience 栏目，但里面没有可检查的行",
        "unchecked": "{f}：栏目「{s}」有 {k} 行，这个脚本不验证",
        "dropped_protected": "受保护的 claim {c} 在基线（{b}）里用到了，这里的 Summary/Experience 却没有。请补回，或取得本人批准并在 Change Log 里说明原因",
        "dropped": "{c} 在基线（{b}）里用到了，这里没有",
        "base_missing": "找不到基线文件：{p}，受保护 claim 检查无法进行。请修正 `base:` 或用 --base 指定",
        "ok": "通过：检查了 {n} 行，用到 {c} 个 Claim ID，没有错误",
        "fail": "未通过：{f} 里有 {e} 个错误",
        "scope": "范围：这里只检查出处、数字和受保护的 claim，不验证 claim 是否属实，也不检查措辞和排版。",
    },
}

ID_RE = re.compile(r"\b[A-Za-z]+-\d+\b")
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# A number worth checking: has 2+ digits, a decimal point, or a unit/multiplier right after it.
NUM_RE = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(\s*(?:%|x|X|×|倍|万|亿|千|[kKmMbB](?![a-zA-Z])))?")

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
}
SKIP_SECTIONS = {
    "education", "languages", "language", "contact", "references",
    "教育", "教育背景", "教育经历", "语言", "语言能力", "联系方式",
}


def section_kind(title):
    t = re.sub(r"\s+", " ", title.strip().strip(":：").lower())
    for kind, names in SECTIONS.items():
        if t in names:
            return kind
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


def load_claims(folder):
    claims = {}
    for f in sorted(Path(folder).glob("*.md")):
        if f.name.startswith("_"):
            continue
        text = f.read_text(encoding="utf-8")
        fm, _ = front_matter(text)
        cid = fm.get("id")
        if cid:
            claims[cid] = {
                "status": fm.get("status", ""),
                "protected": fm.get("protected", "").lower() == "true",
                # every number written anywhere on the card, plus its integer parts ("2022.03" → 2022, 03)
                "numbers": {normalize_number(n) for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)}
                | set(re.findall(r"\d+", text)),
            }
    return claims


def normalize_number(n):
    return n.replace(",", "")


def numbers_in(text):
    """Numbers on a resume line that need a source."""
    out = []
    for n, unit in NUM_RE.findall(text):
        plain = normalize_number(n)
        if len(plain.replace(".", "")) >= 2 or "." in plain or unit.strip():
            out.append(plain)
    return out


def scan_resume(path):
    """Return (lines_to_check, ids_used_in_checked_sections, recognized_section_count,
    level2_headings, unchecked_sections).
    lines_to_check: (line_no, text_without_comments, ids_in_comments, checked)."""
    text = path.read_text(encoding="utf-8")
    _, start = front_matter(text)
    lines = text.split("\n")
    needs, used = [], set()
    headings, recognized, unchecked = [], 0, {}
    kind, title, in_comment = "", "", False
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
            if len(h.group(1)) <= 2:
                title = h.group(2).strip()
                kind = section_kind(title) if len(h.group(1)) == 2 else ""
                if len(h.group(1)) == 2:
                    headings.append(title)
                    if kind in SECTIONS:
                        recognized += 1
            continue
        if not text_only:
            continue
        if kind == "summary" or (kind == "experience" and BULLET_RE.match(raw)):
            needs.append((idx + 1, text_only, ids))
            used.update(ids)
        elif kind == "other":
            unchecked[title] = unchecked.get(title, 0) + 1
            if ids:  # tags outside Summary/Experience are still validated, but don't count as "used"
                needs.append((idx + 1, text_only, ids))
    return needs, used, recognized, headings, unchecked


def main():
    ap = argparse.ArgumentParser(description="对照证据库检查一份简历。")
    ap.add_argument("resume")
    ap.add_argument("--base", help="baseline resume file (default: `base:` in the front matter)")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]

    resume = Path(a.resume)
    if not resume.is_file():
        print(t["no_file"].format(p=a.resume)); return 2
    claims = load_claims(a.claims) if Path(a.claims).is_dir() else {}
    if not claims:
        print(t["no_claims"].format(p=a.claims)); return 2

    needs, used, recognized, headings, unchecked = scan_resume(resume)
    errors = 0
    checked = 0
    if not recognized:
        print("ERROR " + t["no_sections"].format(f=resume.name, h=", ".join(headings) or "-")); errors += 1
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
            elif claims[c]["status"].strip().lower() != "safe to draft":
                print("ERROR " + t["status"].format(f=resume.name, n=n, c=c, s=claims[c]["status"])); errors += 1
            else:
                known.append(c)
        if known:
            pool = set().union(*(claims[c]["numbers"] for c in known))
            for x in numbers_in(text):
                if x not in pool:
                    print("ERROR " + t["number"].format(f=resume.name, n=n, x=x, c=", ".join(known))); errors += 1
    if recognized and not checked:
        print("ERROR " + t["nothing"].format(f=resume.name)); errors += 1
    for s, k in unchecked.items():
        print("WARN  " + t["unchecked"].format(f=resume.name, s=s, k=k))

    # protected claims vs the baseline
    fm, _ = front_matter(resume.read_text(encoding="utf-8"))
    base = Path(a.base) if a.base else (resume.parent / (fm["base"] + ".md") if fm.get("base") else None)
    if base is not None:
        if not base.is_file():
            print("ERROR " + t["base_missing"].format(p=base)); errors += 1
        else:
            _, base_used, _, _, _ = scan_resume(base)
            for c in sorted(base_used - used):
                if c in claims and claims[c]["protected"]:
                    print("ERROR " + t["dropped_protected"].format(c=c, b=base.name)); errors += 1
                else:
                    print("NOTE  " + t["dropped"].format(c=c, b=base.name))

    if errors:
        print(t["fail"].format(e=errors, f=resume.name))
    else:
        print(t["ok"].format(n=checked, c=len(used)))
    print(t["scope"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
