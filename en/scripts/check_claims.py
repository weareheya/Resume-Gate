#!/usr/bin/env python3
"""Check a resume file against the evidence bank. Standard library only; works on macOS, Linux, and Windows.

What it checks (these are the checks a script can do for certain):
  1. The resume has a Summary and/or Experience section the script recognizes (common names in
     English and Chinese are accepted, e.g. "Professional Summary", "Work Experience", "工作经历").
     If it recognizes neither, or finds nothing to check, the check FAILS instead of passing.
  2. Every line under Summary and Projects/Achievements, and every bullet under Experience, carries
     a Claim ID in an HTML comment, e.g.  - Rebuilt the partner program ... <!-- C-001 -->
     A line indented under a bullet is read as part of it. A plain line in Experience needs a
     Claim ID only if it holds a number; otherwise it's listed as not verified.
  3. Every Claim ID points to exactly one card in evidence/claims/ whose status is "Safe to draft".
     Numbers the card marks "to verify" (or anything other than ✓ or blank) can't be used.
  4. Every number on a checked line (counts, %, money, multiples) comes from the Claim Card(s) the
     line cites. Numbers in "Don't rephrase as", Source, To fill or the Claim ID itself don't count.
     Scaled amounts are compared by value (US$2.1M = US$2,100,000, but not US$2.1B), and a currency
     must match the card's. A lone digit or "two"–"twenty" not on the card is only a warning.
  5. No checked line uses a word listed on a cited card's "Banned words:" line (e.g. revenue).
  6. Once evidence/profile.md is filled in, role headings in Experience (### Title · Company · Years)
     and every Education line must match it.
  7. Baseline: a new version must name its baseline (`base:`) when cv/CV-INDEX.md already has a
     starting point for its type. If it has one, every claim marked `protected: true` that the
     baseline uses in Summary or Experience is still used there (unless the card's `keep-for` lists
     other job types only), with the same confirmed numbers,
     unless the user approved the change (`protected-ok: C-001` in the front matter).
  Other non-empty sections (Skills, …) are reported as NOT verified, and a line there holding a
  number no card backs is named. Languages, Contact and References are skipped.
  Errors fail the check; WARN lines are worth a look but don't.

What it does NOT check: whether a sentence is actually supported by its card (a valid ID can
still sit on an invented sentence), or layout. Those still need a human (and the checklist).

Usage:
  python3 scripts/check_claims.py cv/resumes/<id>.md [--base cv/resumes/<base-id>.md]
                                  [--claims evidence/claims] [--profile evidence/profile.md]
                                  [--lang en|zh]

Exit code: 0 = no errors, 1 = errors found, 2 = could not run (missing file, bad usage).
"""
import argparse
import math
import re
import sys
from pathlib import Path

DEFAULT_LANG = "en"

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
    source_text, banned, section = [], [], ""
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
            continue
        if line.strip().startswith("|") and section in ("numbers and what they mean", "数字与口径"):
            numbers_lines.append(line)
        else:
            source_text.append(line)

    card = {"status": fm.get("status", ""), "protected": fm.get("protected", "").lower() == "true",
            "keep_for": {x.strip() for x in re.split(r"[,，、\s]+", fm.get("keep-for", "")) if x.strip()},
            "vals": [], "years": set(), "currency": [], "pending": [], "banned": banned}

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


def frozen_changed(resume):
    """True if cv/frozen.txt (written by scripts/freeze.py) lists this file with a different hash."""
    import hashlib
    record = resume.parent.parent / "frozen.txt"
    if not record.is_file():
        return False
    root, me = resume.resolve().parent.parent.parent, resume.resolve()
    for line in record.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and (root / parts[1].lstrip("*").strip()).resolve() == me:
            return hashlib.sha256(resume.read_bytes()).hexdigest() != parts[0]
    return False


def numbers_for(needs, cid):
    vals = []
    for _, text, ids in needs:
        if cid in ids:
            vals += [t[2] for t in tokens(text) if not is_year(t)]
    return vals


def main():
    ap = argparse.ArgumentParser(description="Check a resume against the evidence bank.")
    ap.add_argument("resume")
    ap.add_argument("--base", help="baseline resume file (default: `base:` in the front matter)")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--profile", help="profile file (default: profile.md next to the claims folder)")
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

    if errors:
        print(t["fail"].format(e=errors, f=resume.name))
    else:
        print(t["ok"].format(n=checked, c=len(used), w=(f" ({warns} WARN)" if a.lang == "en" else f"（{warns} 条提醒）") if warns else ""))
    print(t["scope"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
