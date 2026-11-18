#!/usr/bin/env python3
"""对照证据库检查一份简历。只用标准库，macOS、Linux、Windows 都能跑。

它检查什么（脚本能确定性判断的部分）：
  1. "Experience"（或「工作经历」）下的每条 bullet、"Summary"（或「摘要」）下的每一行，末尾都有 HTML 注释形式的 Claim ID，
     例如：  - 重建了伙伴计划 ... <!-- C-001 -->
  2. 每个 Claim ID 都能对上 evidence/claims/ 里的一张卡，且卡的状态是 "Safe to draft"。
  3. 如果简历有基线（front matter 里的 `base:`，或 --base），基线里标了 `protected: true` 的 claim 在这份里还在。

它不检查什么：claim 是否属实、措辞有没有越过卡的限制、排版。这些仍然要靠人和自审清单。

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
        "dropped_protected": "Protected claim {c} is used in the baseline ({b}) but missing here. Restore it, or get the user's approval and explain why in the Change Log",
        "dropped": "{c} is used in the baseline ({b}) but not here",
        "base_missing": "Baseline file not found: {p} (skipping the protected-claims check)",
        "ok": "OK: {n} lines checked, {c} Claim IDs used, no errors",
        "fail": "FAILED: {e} error(s) in {f}",
        "scope": "Scope: this checks sourcing and protected claims only. It does not verify that claims are true, or check wording or layout.",
    },
    "zh": {
        "no_file": "找不到文件：{p}",
        "no_claims": "在 {p} 里没有找到 Claim Card",
        "untagged": "{f}:{n}：这一行没有 Claim ID：{t}",
        "unknown": "{f}:{n}：{c} 找不到对应的 Claim Card",
        "status": "{f}:{n}：{c} 的状态是「{s}」，只有「Safe to draft」才能使用",
        "dropped_protected": "受保护的 claim {c} 在基线（{b}）里用到了，这里却没有。请补回，或取得本人批准并在 Change Log 里说明原因",
        "dropped": "{c} 在基线（{b}）里用到了，这里没有",
        "base_missing": "找不到基线文件：{p}（跳过受保护 claim 检查）",
        "ok": "通过：检查了 {n} 行，用到 {c} 个 Claim ID，没有错误",
        "fail": "未通过：{f} 里有 {e} 个错误",
        "scope": "范围：这里只检查出处和受保护的 claim，不验证 claim 是否属实，也不检查措辞和排版。",
    },
}

SUMMARY_HEADINGS = {"summary", "profile", "摘要", "简介", "个人简介", "个人总结"}
EXPERIENCE_HEADINGS = {"experience", "work experience", "经历", "工作经历", "经验", "项目经历"}
ID_RE = re.compile(r"\b[A-Za-z]+-\d+\b")
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+")


def front_matter(text):
    """Return (dict, body_start_line_index). Parses simple `key: value` lines."""
    lines = text.split("\n")
    data, end = {}, 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i + 1
                break
            m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", lines[i])
            if m:
                data[m.group(1)] = re.sub(r"\s+#.*$", "", m.group(2)).strip()
    return data, end


def load_claims(folder):
    claims = {}
    for f in sorted(Path(folder).glob("*.md")):
        if f.name.startswith("_"):
            continue
        fm, _ = front_matter(f.read_text(encoding="utf-8"))
        cid = fm.get("id")
        if cid:
            claims[cid] = {
                "status": fm.get("status", ""),
                "protected": fm.get("protected", "").lower() == "true",
            }
    return claims


def scan_resume(path):
    """Yield (line_no, text_without_comments, ids_in_comments) for each line that needs a claim,
    and return the set of all IDs used."""
    text = path.read_text(encoding="utf-8")
    _, start = front_matter(text)
    lines = text.split("\n")
    needs, used = [], set()
    section, in_comment = "", False
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
        used.update(ids)
        text_only = line_no_comments.strip()
        h = HEADING_RE.match(text_only)
        if h:
            if len(h.group(1)) == 2:
                section = h.group(2).strip().lower()
            continue
        if not text_only:
            continue
        in_summary = section in SUMMARY_HEADINGS
        in_experience = section in EXPERIENCE_HEADINGS
        if (in_summary) or (in_experience and BULLET_RE.match(raw)):
            needs.append((idx + 1, text_only, ids))
    return needs, used


def main():
    ap = argparse.ArgumentParser(description="对照证据库检查一份简历。")
    ap.add_argument("resume")
    ap.add_argument("--base", help="基线简历文件（默认用 front matter 里的 `base:`）")
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

    needs, used = scan_resume(resume)
    errors = 0
    for n, text, ids in needs:
        short = text if len(text) <= 60 else text[:57] + "..."
        if not ids:
            print("ERROR " + t["untagged"].format(f=resume.name, n=n, t=short)); errors += 1
            continue
        for c in ids:
            if c not in claims:
                print("ERROR " + t["unknown"].format(f=resume.name, n=n, c=c)); errors += 1
            elif claims[c]["status"].strip().lower() != "safe to draft":
                print("ERROR " + t["status"].format(f=resume.name, n=n, c=c, s=claims[c]["status"])); errors += 1

    # protected claims vs the baseline
    fm, _ = front_matter(resume.read_text(encoding="utf-8"))
    base = Path(a.base) if a.base else (resume.parent / (fm["base"] + ".md") if fm.get("base") else None)
    if base is not None:
        if not base.is_file():
            print("WARN  " + t["base_missing"].format(p=base))
        else:
            _, base_used = scan_resume(base)
            for c in sorted(base_used - used):
                if c in claims and claims[c]["protected"]:
                    print("ERROR " + t["dropped_protected"].format(c=c, b=base.name)); errors += 1
                else:
                    print("NOTE  " + t["dropped"].format(c=c, b=base.name))

    if errors:
        print(t["fail"].format(e=errors, f=resume.name))
    else:
        print(t["ok"].format(n=len(needs), c=len(used)))
    print(t["scope"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
