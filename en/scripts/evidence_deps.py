#!/usr/bin/env python3
"""Which resumes, follow-up cards and answers still match the Claim Cards they cite. Standard library only.

This is the shared part of "correct once, and everything that used the old fact knows" (D-020).
check_claims.py and list_claims.py import it; it has no command line of its own and prints nothing.

How it works:
  * Each Claim Card is split into blocks (what happened, numbers, attribution, status/evidence/role,
    don't-rephrase-as, approved wording, facets, source, protection). Each block gets a
    fingerprint (SHA-256) of its text after a careful clean-up: spacing, a line wrapped inside a
    paragraph, bold/italic marks, dash styles and 1,234-style thousands separators don't count, but every other character does, so "$2.1M" and
    "$21M" differ while "$200,000" and "$200000" don't. Notes and To fill never count.
  * When the user approves a resume (or confirms a recheck), `check_claims.py <file> --record`
    writes the card fingerprints it was approved against to cv/reviewed.txt, together with a
    fingerprint of the lines that cite each card. Follow-up cards and answers are recorded when
    they're written. A record says "these lines were checked against this version of the card".
  * Health is worked out fresh every time and never written into the files themselves:
    current       every cited card matches its record
    changed       a cited card changed after the record (which blocks, and whether that's major)
    not checked   no record yet (or an incomplete one), or the lines citing the card were edited after it
  * Major blocks: what happened, numbers (and their Verified column), attribution, status /
    evidence / role / period, don't rephrase as, and protection when it touches this file's job
    type. Minor: approved wording, facets, source, and any block the template doesn't have.

The record file holds paths, card IDs and fingerprints only, no text from your cards or resumes.
"""
import hashlib
import os
import re
from datetime import date
from pathlib import Path

RECORD = Path("cv/reviewed.txt")
FORMAT = "1"  # bump when normalize() or the blocks change, so old records read as "not checked", not "changed"

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
CARD_ID_RE = re.compile(r"C-\d+")  # the kit's card ID convention (C-001); C-000 is the templates' placeholder
PLACEHOLDER = "C-000"
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


NEW_LINE_RE = re.compile(r"^(?:[-*+]\s|\d+[.)]\s|\||#|>)")
THOUSANDS_RE = re.compile(r"(?<![\d.,])\d{1,3}(?:,\d{3})+(?![\d,])")


def normalize(text):
    """Conservative clean-up before fingerprinting. Only changes that can't alter a fact.
    Convention: a comma between digits followed by exactly three digits is a thousands separator
    (€2,100 = €2100); cards write decimals with a point. Not touched on purpose: "1.234" or "1 234" style thousands, a decimal comma ("2,5"), number lists
    ("2022,2023"), the minus sign, any letter or punctuation. Those count as changes, which is the safe side."""
    out = []
    for line in text.replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if not s or set(s) <= set("|-: "):
            out.append("")  # blank lines and table rules end a paragraph
            continue
        s = re.sub(r"^>\s?", "", s)                      # blockquote marker
        s = re.sub(r"^[*+]\s+", "- ", s)                 # bullet style
        s = re.sub(r"\*\*|__|`", "", s)                  # bold and code marks
        s = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"\1", s)  # *italic*
        s = re.sub(r"\s*[–—―‐‑]\s*", "-", s)            # en/em dashes, with or without spaces
        s = re.sub(r"(?<=\S)\s+-\s+(?=\S)", "-", s)      # " - " used as a dash
        s = THOUSANDS_RE.sub(lambda m: m.group(0).replace(",", ""), s)  # 200,000 = 200000; 1,234,567 = 1234567
        s = re.sub(r"\s*\|\s*", "|", s)                  # table cell padding
        s = re.sub(r"\s+", " ", s)
        if out and out[-1] and not NEW_LINE_RE.match(line.strip()) and not out[-1].startswith(("|", "#")):
            out[-1] += " " + s  # a wrapped line inside a paragraph or bullet: same text
        else:
            out.append(s)
    return "\n".join(x for x in out if x)


def short_hash(text):
    """Full SHA-256 of the normalized text. (Nothing shows it; the record file is the only place it's kept.)"""
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


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
            fields = [f"v={FORMAT}", f"date={date.today().isoformat()}"] + [f"{k}={v}" for k, v in sorted(entries[cid].items())]
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
    Returns ("not_checked", reason) | ("current", None) | ("changed", {"blocks": [...], "major": bool, "edited": bool}).
    A record that is incomplete or from another format version is "not checked", never "current".
    "edited" is reported with a change too, so a card change can't hide an unreviewed edit to the lines."""
    if blocks is None:  # cited, but there's no such card now
        if record is None:
            return "missing", None  # never recorded: a typo, or a card deleted before 0.7.0
        return "changed", {"blocks": ["removed"], "major": True, "edited": False}
    if record is None:
        return "not_checked", "no_record"
    if record.get("v") != FORMAT or "lines" not in record or "meta" not in record:
        return "not_checked", "no_record"
    edited = lines is not None and record["lines"] != lines_hash(lines)
    changed, major = [], False
    for name in set(record) | set(blocks):
        if name in ("lines", "date", "v"):
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
        return "changed", {"blocks": sorted(changed, key=lambda n: ORDER.index(n) if n in ORDER else 99), "major": major, "edited": edited}
    if edited:
        return "not_checked", "edited"
    return "current", None


def asset_health(states):
    """Overall health from {card id: (state, detail)}: changed, then missing, then not_checked, then current."""
    kinds = {s for s, _ in states.values()}
    if "changed" in kinds:
        return "changed"
    if "missing" in kinds:
        return "missing"
    if "not_checked" in kinds:
        return "not_checked"
    return "current"


def is_cited(cid, known, recorded, tagged=False):
    """Does this ID refer to a card? Worked out without needing the card to exist, so a deleted card
    shows up as "removed" (it was recorded) or "missing" (it wasn't) instead of vanishing.
    Yes if: it's a card now; it was one when this file was recorded; it's in a resume's <!-- --> tag
    (tagged: those hold card IDs only); or it follows the C-001 convention. A job ID such as ACME-01
    or the templates' C-000 doesn't count."""
    if cid == PLACEHOLDER and cid not in known:
        return False
    return tagged or cid in known or cid in recorded or bool(CARD_ID_RE.fullmatch(cid))


def binding_lines(text):
    """What an answer's approval is bound to besides its text: the question and the scope. Changing
    who an answer may be used for is a change to what the user approved."""
    fm = _front_matter(text)[0]
    return [f"question: {fm.get('question', '')}", f"scope: {fm.get('scope', '')}"]


def asset_citations(asset_rel, text, known, recorded=()):
    """{card: [lines]} for a follow-up card or an answer. For an answer the lines include its question
    and scope, so editing either needs a new confirmation."""
    cites = generic_citations(text, known, recorded)
    if asset_rel.startswith("interview/answers/"):
        bind = binding_lines(text)
        cites = {c: lines + bind for c, lines in cites.items()}
    return cites


def generic_citations(text, known, recorded=()):
    """Claim IDs a follow-up card or answer cites: {id: [lines]}. A card counts as cited by every
    level-2 section that names it, and those whole sections are its lines. See is_cited for which
    IDs count."""
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
            if is_cited(cid, known, recorded):
                out.setdefault(cid, []).extend(sec)
    return out
