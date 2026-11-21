#!/usr/bin/env python3
"""哪些简历、追问卡和答案，和它们引用的 Claim Card 还对得上。只用标准库。

这是「事实只纠正一次，所有用过旧事实的地方都知道」（D-020）的共享部分。check_claims.py 和
list_claims.py 都调用它；它自己没有命令行，也不打印任何东西。

怎么工作：
  * 每张 Claim Card 拆成几个区块（事实、数字、归因、状态/证据/职位、禁止改写、已批准措辞、能力切面、
    出处、保护设置）。每个区块在谨慎清理之后算一个短指纹：空格、换行、加粗/斜体、横线写法和千分位
    逗号不算，其余每个字符都算，所以「$2.1M」和「$21M」不同，「$200,000」和「$200000」相同。
    「备注」和「待补」永远不算。
  * 本人批准一份简历（或确认复核）时，`check_claims.py <文件> --record` 把它当时对照的卡片指纹写进
    cv/reviewed.txt，同时记下引用每张卡的那几行的指纹。追问卡和答案在写好时记录。一条记录的意思是
    「这几行对照过这张卡的这个版本」。
  * 状态每次现场算，从不写回文件本身：
    current       引用的每张卡都和记录一致
    changed       记录之后，引用的某张卡改过（改了哪些区块、算不算重大）
    not checked   还没有记录，或者记录之后引用这张卡的行被改过
  * 重大区块：事实、数字（含核实列）、归因、状态/证据/职位/时间、禁止改写，以及影响这份文件岗位
    类型的保护设置。一般区块：已批准措辞、能力切面、出处，以及模板里没有的区块。

记录文件只有路径、卡片 ID 和指纹，不含卡片或简历里的任何文字。
"""
import hashlib
import os
import re
from datetime import date
from pathlib import Path

RECORD = Path("cv/reviewed.txt")

# block name -> heading prefixes (lower case) in the English and Chinese card templates
BLOCKS = {
    "facts": ("what happened", "事实"),
    "numbers": ("numbers and what they mean", "数字与口径"),
    "attribution": ("attribution", "归因"),
    "dont": ("don't rephrase as", "don’t rephrase as", "dont rephrase as", "禁止改写"),
    "wording": ("approved wording", "已批准措辞"),
    "facets": ("capability facets", "能力切面"),
    "source": ("source", "出处"),
}
IGNORED = ("notes", "to fill", "备注", "待补")
META_KEYS = ("status", "evidence", "role", "period")
MAJOR = {"facts", "numbers", "attribution", "meta", "dont", "removed"}
ORDER = ("removed", "facts", "numbers", "attribution", "meta", "dont", "protect", "wording", "facets", "source", "other")

ID_RE = re.compile(r"\b[A-Za-z]+-\d+\b")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def normalize(text):
    """Conservative clean-up before fingerprinting. Only changes that can't alter a fact."""
    out = []
    for line in text.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if not s or set(s) <= set("|-: "):
            continue  # blank lines and table rules
        s = re.sub(r"^>\s?", "", s)                      # blockquote marker
        s = re.sub(r"^[*+]\s+", "- ", s)                 # bullet style
        s = re.sub(r"\*\*|__|`", "", s)                  # bold and code marks
        s = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"\1", s)  # *italic*
        s = re.sub(r"\s*[–—―‐‑]\s*", "-", s)            # en/em dashes, with or without spaces
        s = re.sub(r"(?<=\S)\s+-\s+(?=\S)", "-", s)      # " - " used as a dash
        s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)    # thousands separators: 200,000 = 200000
        s = re.sub(r"\s*\|\s*", "|", s)                  # table cell padding
        s = re.sub(r"\s+", " ", s)
        out.append(s)
    return "\n".join(out)


def short_hash(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()[:10]


def _front_matter(text):
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


def _keep_for(value):
    return sorted({x.strip() for x in re.split(r"[,，、\s]+", value or "") if x.strip()})


def card_blocks(text):
    """{block: fingerprint} for one Claim Card, plus "protect" as plain text (it's short and the
    check needs the old value to tell whether a change touches a given job type)."""
    fm, start = _front_matter(text)
    parts = {name: [] for name in BLOCKS}
    parts["other"] = []
    current = "facts"  # the "# C-001 · summary" title line counts as part of what happened
    for line in text.split("\n")[start:]:
        h = re.match(r"^(#{1,6})\s+(.*?)\s*$", line.strip())
        if h and len(h.group(1)) >= 2:
            title = h.group(2).strip().lower()
            if title.startswith(IGNORED):
                current = None
            else:
                current = next((n for n, keys in BLOCKS.items() if title.startswith(keys)), "other")
            continue
        if current is not None:
            parts[current].append(COMMENT_RE.sub("", line))
    out = {name: short_hash("\n".join(lines)) for name, lines in parts.items() if normalize("\n".join(lines))}
    out["meta"] = short_hash("\n".join(f"{k}={fm.get(k, '')}" for k in META_KEYS))
    out["protect"] = "%s:%s" % (fm.get("protected", "").strip().lower() == "true", ",".join(_keep_for(fm.get("keep-for", ""))))
    return out


def load_cards(folder):
    """{card id: blocks} for every card in the folder (templates skipped)."""
    cards = {}
    for f in sorted(Path(folder).glob("*.md")):
        if f.name.startswith("_"):
            continue
        text = f.read_text(encoding="utf-8")
        cid = _front_matter(text)[0].get("id", "")
        if cid:
            cards[cid] = card_blocks(text)
    return cards


def kit_root(claims_folder):
    return Path(claims_folder).resolve().parent.parent


def rel(path, root):
    return Path(os.path.relpath(Path(path).resolve(), root)).as_posix()


def read_records(root):
    """{(asset path, card id): {"lines": h, "date": d, block: h, ...}}. The newest line wins."""
    records = {}
    f = Path(root) / RECORD
    if not f.is_file():
        return records
    for line in f.read_text(encoding="utf-8").splitlines():
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3 or line.startswith("#"):
            continue
        entry = dict(p.split("=", 1) for p in parts[2:] if "=" in p)
        records[(parts[0], parts[1])] = entry
    return records


def write_records(root, asset_rel, entries):
    """Append one line per card. entries: {card id: {"lines": h, block: h, ...}}."""
    f = Path(root) / RECORD
    f.parent.mkdir(parents=True, exist_ok=True)
    new = not f.is_file()
    with f.open("a", encoding="utf-8") as out:
        if new:
            out.write("# Written by check_claims.py --record. Paths, card IDs and fingerprints only (D-020).\n")
        for cid in sorted(entries):
            fields = [f"date={date.today().isoformat()}"] + [f"{k}={v}" for k, v in sorted(entries[cid].items())]
            out.write("\t".join([asset_rel, cid] + fields) + "\n")


def lines_hash(lines):
    return short_hash("\n".join(sorted(normalize(x) for x in lines)))


def protect_is_major(old, new, job_type):
    """A change to protected / keep-for is major only if it changes what this file must keep."""
    if old == new:
        return None
    op, ok = (old.split(":", 1) + [""])[:2]
    np_, nk = (new.split(":", 1) + [""])[:2]
    if op != np_:
        return True
    a, b = set(filter(None, ok.split(","))), set(filter(None, nk.split(",")))
    return (not job_type) or (job_type in (a ^ b)) or (not a) != (not b)


def card_state(record, blocks, lines, job_type=""):
    """State of one card for one file.
    Returns ("not_checked", reason) | ("current", None) | ("changed", {"blocks": [...], "major": bool})."""
    if record is None:
        return "not_checked", "no_record"
    if blocks is None:
        return "changed", {"blocks": ["removed"], "major": True}
    changed, major = [], False
    for name in set(record) | set(blocks):
        if name in ("lines", "date"):
            continue
        old, now = record.get(name), blocks.get(name)
        if old == now:
            continue
        if name == "protect":
            m = protect_is_major(old or "False:", now or "False:", job_type)
            if m is None:
                continue
            major = major or m
        else:
            major = major or name in MAJOR
        changed.append(name)
    if changed:
        return "changed", {"blocks": sorted(changed, key=lambda n: ORDER.index(n) if n in ORDER else 99), "major": major}
    if record.get("lines") and lines is not None and record["lines"] != lines_hash(lines):
        return "not_checked", "edited"
    return "current", None


def asset_health(states):
    """Overall health from {card id: (state, detail)}: changed beats not_checked beats current."""
    kinds = {s for s, _ in states.values()}
    if "changed" in kinds:
        return "changed"
    if "not_checked" in kinds:
        return "not_checked"
    return "current"


def generic_citations(text, known):
    """Claim IDs a follow-up card or answer cites: {id: [lines]}. A card counts as cited by every
    level-2 section that names it, and those whole sections are its lines. Only IDs that match a
    real card count, so a template's C-000 is ignored."""
    _, start = _front_matter(text)
    sections, cur = [], []
    for line in text.split("\n")[start:]:
        if line.startswith("## ") and cur:
            sections.append(cur)
            cur = []
        cur.append(line)
    if cur:
        sections.append(cur)
    out = {}
    for sec in sections:
        for cid in sorted(set(ID_RE.findall("\n".join(sec)))):
            if cid in known:
                out.setdefault(cid, []).extend(sec)
    return out
