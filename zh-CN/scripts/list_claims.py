#!/usr/bin/env python3
"""每张 Claim Card 列一行，证据库很大时 AI 也能低成本地过一遍。只用标准库。

输出一张表：ID、卡片的一句话、状态、是否受保护、职位、能力切面。
每次运行都现场读卡、不写任何文件，所以清单不会过期，也不会多出一个要保护隐私的文件。

AI 怎么用（WORKFLOW S2）：卡片不超过 15 张时，照旧每张读全文。超过时，先读这份清单，再打开所有受保护的卡，
以及一句话、职位或能力切面和岗位沾边的卡读全文。每张卡仍要写进证据表（D-019），没用的可以合成一行。

用法：  python3 scripts/list_claims.py [--claims evidence/claims] [--lang en|zh]
        python3 scripts/list_claims.py --used-by C-001   哪些简历、追问卡、答案引用了这张卡，各自要不要复核（D-020）
        python3 scripts/list_claims.py --health          只列出引用的卡改过、需要复核的文件
        python3 scripts/list_claims.py --answers ACME-01 适合这个岗位的已审核答案，以及哪些可以直接复用
        python3 scripts/list_claims.py --sources         evidence/sources/ 里的文件：新文件、读过、读过之后变了、改名、已跳过（D-021）
        python3 scripts/list_claims.py --sources --no-hash   同一份列表，只列文件名和大小，不打开任何文件
        python3 scripts/list_claims.py --fingerprint FILE    单个文件的指纹，写卡之前用来确认它没变
退出码：0 = 已列出，2 = 没找到卡片。
"""
import argparse
import hashlib
import importlib.util
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path

DEFAULT_LANG = "zh"
FULL_READ_UP_TO = 15

spec = importlib.util.spec_from_file_location("check_claims", Path(__file__).with_name("check_claims.py"))
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)
deps = cc.deps

T = {
    "en": {
        "head": "| ID | Summary | Status | Protected | Role | Facets |",
        "yes": "yes",
        "none": "No claim cards found in {p}",
        "few": "{n} cards: few enough to read every card in full.",
        "dep_head": "| File | Status | Check | What changed |",
        "current": "current",
        "changed": "needs recheck",
        "historical": "sent before the change",
        "not_checked": "not checked",
        "missing": "card missing",
        "no_card": "no such card (never recorded here)",
        "edited": "edited after it was recorded",
        "health_ok": "{n} file(s) cite cards; none needs a recheck.",
        "health_counts": "{c} current, {k} need a recheck, {h} sent before a change.",
        "health_unchecked": "Not checked yet ({n}): {fs}. Normal for versions made before 0.7.0; check one when you reuse or send it.",
        "no_assets": "No resumes, follow-up cards or answers cite {c}.",
        "used_by": "{n} file(s) cite {c}:",
        "major": "major",
        "minor": "minor",
        "ans_head": "| Answer | Question | Scope | Status | Check | Reuse? |",
        "ans_yes": "yes",
        "ans_missing": "a card it cites doesn't exist: fix that first",
        "ans_nocite": "cites no card: tag the cards it uses, then record it",
        "ans_recheck": "recheck first",
        "ans_unchecked": "check against the cards first",
        "ans_draft": "not approved yet",
        "ans_none": "No reviewed answers fit {j}. Write new ones in interview/answers/ (copy _TEMPLATE.md).",
        "ans_skipped": "{n} other answer(s) are for another employer or job, so they're left out.",
        "no_job": "No job file jobs/{j}.md: employer-specific answers can't be matched, so only reusable ones are listed.",
        "src_head": "| File | Fingerprint | Size | State | Note |",
        "st_new": "new",
        "st_read": "read before",
        "st_changed": "changed since read",
        "st_renamed": "renamed",
        "st_skipped": "skipped",
        "st_cloud": "not downloaded",
        "st_unreadable": "unreadable",
        "st_nonreg": "not a regular file (not read)",
        "st_gone": "gone",
        "st_listed": "listed only",
        "n_renamed": "was {p}",
        "n_dup": "same content as {p}",
        "n_ambig": "same content as {p}; not matched automatically",
        "n_gone": "recorded, but the file is no longer here",
        "n_cloud": "a cloud-sync placeholder; not opened",
        "n_listed_rec": "has a record",
        "st_link": "a link (not followed)",
        "n_pipe": "the name contains \"|\", which can't be written in the INTAKE table: rename it, or skip its folder",
        "src_link_root": "{d} is, or sits inside, a link: not scanned. Links are never followed; use a real folder.",
        "src_intake_bad": "The skip list in evidence/INTAKE.md can't be read ({e}), so the skip rules can't be verified. No file was listed, opened or fingerprinted. Do not read any raw source until this is fixed.",
        "fp_link": "{p} is, or sits behind, a link: links are never followed, so it wasn't opened.",
        "src_none": "No {d} folder: nothing to list.",
        "src_empty": "{d} has no files.",
        "src_counts": "{n} file(s): {a} new, {b} read before, {c} changed since read, {s} skipped, {o} not fingerprinted.",
        "src_remind": "A record only says a file was looked at, for one job. It never means the file has no other usable evidence: look again when a requirement needs it. This list fingerprints files on this computer only; it reads no text and sends nothing to a model. Skipped files are never opened.",
        "src_cloud": "Cloud placeholders are recognised only for iCloud (.icloud files and the macOS dataless flag). With any other sync tool, fingerprinting a file may download it: use --no-hash to list names and sizes only.",
        "fp_ok": "{p}  {f}",
        "fp_skipped": "{p} is skipped: not opened.",
        "fp_outside": "{p} is outside this folder: not read.",
        "fp_cloud": "{p} is a cloud placeholder (not downloaded): not opened.",
        "fp_err": "{p}: can't read it ({e}).",
        "fp_missing": "{p} not found.",
        "many": "{n} cards. Read in full: every protected card ({k}), and every card whose summary, role or facets touch the job. Every card still goes in the evidence table; unused ones can share a line.",
    },
    "zh": {
        "head": "| ID | 一句话 | 状态 | 受保护 | 职位 | 能力切面 |",
        "yes": "是",
        "none": "{p} 里没有找到 Claim Card",
        "few": "共 {n} 张卡：数量不多，每张都读全文。",
        "dep_head": "| 文件 | 状态 | 检查 | 改了什么 |",
        "current": "最新",
        "changed": "需要复核",
        "historical": "改动前已投递",
        "not_checked": "未检查",
        "missing": "卡片不存在",
        "no_card": "没有这张卡（这里也没有记录过）",
        "edited": "记录之后被改过",
        "health_ok": "共 {n} 个文件引用了卡片，没有需要复核的。",
        "health_counts": "最新 {c} 个，需要复核 {k} 个，改动前已投递 {h} 个。",
        "health_unchecked": "还没检查过（{n} 个）：{fs}。0.7.0 之前做的版本都是这样，等再次复用或投递时再检查。",
        "no_assets": "没有简历、追问卡或答案引用 {c}。",
        "used_by": "{n} 个文件引用了 {c}：",
        "major": "重大",
        "minor": "一般",
        "ans_head": "| 答案 | 问题 | 适用范围 | 状态 | 检查 | 能复用吗 |",
        "ans_yes": "能",
        "ans_missing": "它引用的卡不存在：先处理这个",
        "ans_nocite": "没有引用任何卡：先标上它用到的卡，再记录",
        "ans_recheck": "先复核",
        "ans_unchecked": "先对照卡片检查",
        "ans_draft": "还没批准",
        "ans_none": "没有适用于 {j} 的已审核答案。新答案写在 interview/answers/（复制 _TEMPLATE.md）。",
        "ans_skipped": "另有 {n} 个答案是给别的公司或岗位的，没有列出。",
        "no_job": "找不到岗位文件 jobs/{j}.md：针对某家公司的答案没法匹配，只列出通用的。",
        "src_head": "| 文件 | 指纹 | 大小 | 状态 | 说明 |",
        "st_new": "新文件",
        "st_read": "读过",
        "st_changed": "读过之后变了",
        "st_renamed": "改名",
        "st_skipped": "已跳过",
        "st_cloud": "未下载",
        "st_unreadable": "读不了",
        "st_nonreg": "不是普通文件（没有读）",
        "st_gone": "已不在",
        "st_listed": "只列出",
        "n_renamed": "原来是 {p}",
        "n_dup": "内容和 {p} 相同",
        "n_ambig": "内容和 {p} 相同；不自动对应",
        "n_gone": "有记录，但文件已经不在这里",
        "n_cloud": "云同步占位文件；没有打开",
        "n_listed_rec": "有记录",
        "st_link": "链接（没有跟随）",
        "n_pipe": "文件名里有「|」，没法写进 INTAKE 的表格：请改名，或者跳过它所在的文件夹",
        "src_link_root": "{d} 本身或它的上级是链接：没有扫描。链接一律不跟随，请改成真正的文件夹。",
        "src_intake_bad": "evidence/INTAKE.md 里的跳过规则读不了（{e}），没法验证跳过规则。没有列出、打开或计算任何文件。修好之前，不要读任何原始资料。",
        "fp_link": "{p} 本身或它的上级是链接：链接一律不跟随，所以没有打开。",
        "src_none": "没有 {d} 文件夹：没有可列的。",
        "src_empty": "{d} 里没有文件。",
        "src_counts": "共 {n} 个文件：新文件 {a} 个，读过 {b} 个，读过之后变了 {c} 个，已跳过 {s} 个，没算指纹 {o} 个。",
        "src_remind": "记录只说明某个文件曾为某一个岗位看过，绝不表示这个文件里没有别的可用证据：有要求需要时再看。这个列表只在本机给文件算指纹，不读文字，也不把任何内容交给模型。已跳过的文件从不打开。",
        "src_cloud": "云占位文件只能识别 iCloud 的（.icloud 文件和 macOS 的 dataless 标记）。用其他同步工具时，算指纹可能会触发下载：用 --no-hash 只列文件名和大小。",
        "fp_ok": "{p}  {f}",
        "fp_skipped": "{p} 已跳过：没有打开。",
        "fp_outside": "{p} 在这个文件夹之外：没有读。",
        "fp_cloud": "{p} 是云占位文件（还没下载）：没有打开。",
        "fp_err": "{p}：读不了（{e}）。",
        "fp_missing": "找不到 {p}。",
        "many": "共 {n} 张卡。要读全文的：所有受保护的卡（{k}），以及一句话、职位或能力切面和这个岗位沾边的卡。每张卡仍要写进证据表；没用的可以合成一行。",
    },
}

FACET_HEADINGS = ("capability facets", "能力切面")


def summary(text):
    """The card's title after "C-001 ·", or the first heading."""
    m = re.search(r"^#\s+(.*)$", text, re.M)
    if not m:
        return ""
    return re.split(r"\s+[·・]\s+", m.group(1), maxsplit=1)[-1].strip()


def facets(text):
    """First-column entries of the Capability facets table."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith(FACET_HEADINGS)
            continue
        if inside and line.strip().startswith("|"):
            cell = line.strip().strip("|").split("|")[0].strip()
            if cell and not set(cell) <= set("-: ") and cell.lower() not in ("facet", "切面", "能力切面"):
                out.append(cell)
    return out


def cell(s):
    return s.replace("|", "/").strip()


def assets(root, known, records):
    """Every resume, follow-up card and answer, with the cards it cites:
    [(path, lifecycle, frozen, job type, {card: [lines]})]. A card deleted after the file was
    recorded still counts, so it shows up as removed instead of disappearing."""
    out = []
    recorded = {}
    for p, c in records:
        recorded.setdefault(p, set()).add(c)
    for p in sorted((root / "cv" / "resumes").glob("*.md")):
        if p.name.startswith("_"):
            continue
        r = cc.scan_resume(p)
        fm = r["fm"]
        mine = recorded.get(deps.rel(p, root), set())
        ids = sorted({c for _, _, xs in r["needs"] for c in xs})
        cites = {c: cc.lines_for(r["needs"], c) for c in ids if deps.is_cited(c, known, mine, tagged=True)}
        frozen = cc.frozen_entry(p) is not None or fm.get("status", "").strip().lower() == "sent"
        out.append((p, fm.get("status", "") or "-", frozen, fm.get("type", ""), cites))
    for p in sorted((root / "interview").rglob("*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        fm = cc.front_matter(text)[0]
        me = deps.rel(p, root)
        out.append((p, fm.get("status", "") or "-", False, fm.get("type", ""), deps.asset_citations(me, text, known, recorded.get(me, set()))))
    return out


def dependency_rows(root, cards, only=None):
    """[(file, lifecycle, health, {card: (state, detail)})], health one of current / changed /
    missing / historical / not_checked. `only` limits it to one card."""
    records = deps.read_records(root)
    rows = []
    for p, life, frozen, ty, cites in assets(root, set(cards), records):
        if only is not None:
            cites = {c: v for c, v in cites.items() if c == only}
        if not cites:
            continue
        me = deps.rel(p, root)
        states = {c: deps.card_state(records.get((me, c)), cards.get(c), lines, ty) for c, lines in cites.items()}
        health = deps.asset_health(states)
        if health == "changed" and frozen:
            health = "historical"
        rows.append((me, life, health, states))
    return rows


def describe(states, t, names):
    parts = []
    for c, (st, d) in sorted(states.items()):
        if st == "changed":
            parts.append(f"{c}: " + ", ".join(names.get(x, x) for x in d["blocks"]) + " · " + (t["major"] if d["major"] else t["minor"])
                         + (" · " + t["edited"] if d.get("edited") else ""))
        elif st == "missing":
            parts.append(f"{c}: {t['no_card']}")
        elif st == "not_checked" and d == "edited":
            parts.append(f"{c}: {t['edited']}")
    return "; ".join(parts)


def norm_name(s):
    """Company names compared whole: case, spacing and punctuation are ignored, nothing else."""
    return " ".join(re.sub(r"[^\w]+", " ", s.casefold()).split())


def scope_fits(scope, job_id, company):
    """reusable | employer: <name> | job: <id>. An empty scope counts as reusable. An employer scope
    matches only the exact company name on the job (no substring, and an empty name matches nothing)."""
    kind, _, value = (scope or "reusable").partition(":")
    kind, value = kind.strip().lower(), value.strip()
    if kind in ("reusable", "通用", ""):
        return True
    if kind in ("employer", "公司"):
        return bool(norm_name(value)) and norm_name(value) == norm_name(company)
    if kind in ("job", "岗位"):
        return bool(value) and value.lower() == job_id.lower()
    return False


def answers_for(root, cards, job_id, t):
    """Reviewed answers that fit this job, with whether each can be reused as it is (D-020)."""
    job = root / "jobs" / f"{job_id}.md"
    company = cc.front_matter(job.read_text(encoding="utf-8"))[0].get("company", "") if job.is_file() else ""
    if not job.is_file():
        print(t["no_job"].format(j=job_id))
    rows = {me: (life, health) for me, life, health, _ in dependency_rows(root, cards)}
    fit, skipped = [], 0
    for p in sorted((root / "interview" / "answers").glob("*.md")):
        if p.name.startswith("_"):
            continue
        fm = cc.front_matter(p.read_text(encoding="utf-8"))[0]
        if not scope_fits(fm.get("scope", ""), job_id, company):
            skipped += 1
            continue
        me = deps.rel(p, root)
        # Reuse as it is only when everything says yes: it cites cards, none is missing or changed, it was
        # checked against them, and the user approved it. No record or no citation never counts as current.
        life, health = rows.get(me, (fm.get("status", "") or "-", "no_cite"))
        if health in ("changed", "historical"):
            reuse = t["ans_recheck"]
        elif health == "missing":
            reuse = t["ans_missing"]
        elif health == "no_cite":
            reuse, health = t["ans_nocite"], "not_checked"
        elif health != "current":
            reuse = t["ans_unchecked"]
        elif life.strip().lower() != "approved":
            reuse = t["ans_draft"]
        else:
            reuse = t["ans_yes"]
        fit.append((fm.get("id") or p.stem, fm.get("question", ""), fm.get("scope", "") or "reusable", life,
                    t["changed" if health == "historical" else health], reuse))
    if not fit:
        print(t["ans_none"].format(j=job_id))
    else:
        print(t["ans_head"])
        print("|---|---|---|---|---|---|")
        for row in fit:
            print("| " + " | ".join(cell(x) for x in row) + " |")
    if skipped:
        print(t["ans_skipped"].format(n=skipped))
    return 0

SOURCES_DIR = "evidence/sources"
FP_LEN = 16
DATALESS = 0x40000000  # macOS SF_DATALESS: the file's content isn't on this disk yet
RECORD_HEADINGS = ("source records", "来源记录")
SKIP_HEADINGS = ("skipped sources", "跳过的资料")
HEADER_CELLS = ("file", "文件")


class IntakeUnreadable(Exception):
    """evidence/INTAKE.md exists but can't be read, so the skip list can't be checked."""


def fingerprint(path):
    """First 16 hex digits of the file's SHA-256, computed in chunks on this computer."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:FP_LEN]


def norm(rel):
    """How two paths are compared: Unicode-normalised and without regard to case, because macOS
    stores names in a different Unicode form and is usually case-insensitive. Over-matching is
    the safe direction for a skip list."""
    parts = [x for x in rel.replace("\\", "/").split("/") if x not in ("", ".")]
    return unicodedata.normalize("NFC", "/".join(parts)).casefold()


def one_cell(raw):
    """A table cell without its padding, and without one pair of wrapping backticks."""
    c = raw.strip()
    if len(c) > 1 and c.startswith("`") and c.endswith("`"):
        c = c[1:-1]
        if c != c.strip():
            raise IntakeUnreadable(row_error(c.strip()))
    return c


def row_error(first):
    return f"INTAKE 表格里有一行没法可靠解析（文件名或原因里有 |、反引号里面首尾有空格，或路径里有 '..'）。这一行以此开头：{first}"


def intake_tables(root):
    """(records {path: fingerprint}, skipped {path: reason}) from evidence/INTAKE.md.
    A missing INTAKE, or one without the sections, gives empty results, so an INTAKE from before 0.8.0
    works as it is. An INTAKE that exists but can't be read raises IntakeUnreadable: the skip list can't
    be checked, and that must never look the same as "nothing is skipped". The same goes for a skipped
    row with more cells than the table has columns: a "|" in a name or a reason makes it impossible to
    tell what the row says, so the list fails closed instead of guessing."""
    records, skipped, section = {}, {}, None
    try:
        text = (root / "evidence/INTAKE.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        if (root / "evidence/INTAKE.md").is_symlink():
            raise IntakeUnreadable("evidence/INTAKE.md is a link that leads nowhere")
        return records, skipped
    except (OSError, UnicodeDecodeError) as e:
        raise IntakeUnreadable(str(getattr(e, "strerror", None) or e))
    for line in text.splitlines():
        if line.startswith("## "):
            title = line[3:].strip().lower()
            section = "records" if title.startswith(RECORD_HEADINGS) else "skipped" if title.startswith(SKIP_HEADINGS) else None
            continue
        if section and line.strip().startswith("|"):
            cells = [one_cell(c) for c in line.strip().strip("|").split("|")]
            first = cells[0].replace("\\", "/")
            if first.startswith("./"):
                first = first[2:]
            if section == "skipped" and ".." in first.split("/"):
                raise IntakeUnreadable(row_error(first))
            if not first or set(first) <= set("-: ") or first.lower() in HEADER_CELLS:
                continue
            if section == "records":
                if len(cells) > 1 and cells[1]:
                    records[first] = cells[1].lower()
            else:
                if len(cells) > 2:
                    raise IntakeUnreadable(row_error(first))
                skipped[first] = cells[1] if len(cells) > 1 else ""
    return records, skipped


def is_skipped(rel, skipped):
    """A skipped entry covers a file, or a folder (with or without a trailing "/") and everything in it."""
    r = norm(rel).rstrip("/")
    for s in skipped:
        n = norm(s).rstrip("/")
        if r == n or r.startswith(n + "/"):
            return True
    return False


def has_link(root, path):
    """True if path, or any folder between root and it, is a symbolic link, or the path can't be checked
    as written (outside root, or with a ".." that the system would resolve through a link). The path is
    checked exactly as it will be opened; nothing is normalised first and nothing is followed."""
    try:
        parts = Path(path).relative_to(root).parts
    except ValueError:
        return True
    if ".." in parts:
        return True
    cur = Path(root)
    for part in parts:
        cur = cur / part
        if cur.is_symlink():
            return True
    return False


def size_text(n):
    return f"{n} B" if n < 1024 else f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def inspect_file(full):
    """Look at one file without following links. Returns (state, size, note)."""
    try:
        if full.is_symlink():
            return "link", None, ""
        st = os.stat(full)
    except OSError as e:
        return "unreadable", None, str(e.strerror or e)
    if not stat.S_ISREG(st.st_mode):
        return "nonreg", None, ""
    if getattr(st, "st_flags", 0) & DATALESS:
        return "cloud", st.st_size, ""
    return "ok", st.st_size, ""


def scan_sources(root, records, skipped, hash_files=True):
    """One row per file in evidence/sources/: (path, fingerprint, size, state, note-key, note-arg).
    Skipped files and anything behind a link are never opened. Nothing is written. Returns None when
    there is no folder, and the string "link" when the folder itself (or its parent) is a link."""
    base = root / SOURCES_DIR
    if is_skipped(SOURCES_DIR, skipped):
        return [[SOURCES_DIR + "/", None, None, "skipped", "", ""]]  # the whole folder: not entered
    if has_link(root, base):
        return "link"
    if not base.is_dir():
        return None
    found, blocked = [], []  # found: [rel, fp, size, state, note_key, note_arg]
    recorded = {norm(p): p for p in records}

    def on_error(e):
        rel = Path(os.path.abspath(e.filename)).relative_to(root).as_posix() + "/"
        blocked.append(norm(rel))
        found.append([rel, None, None, "unreadable", "", str(e.strerror or e)])

    for dirpath, dirnames, filenames in os.walk(base, onerror=on_error):
        dirnames.sort()
        keep = []
        for d in dirnames:
            full = Path(dirpath) / d
            rel = full.relative_to(root).as_posix()
            if is_skipped(rel, skipped):
                found.append([rel + "/", None, None, "skipped", "", ""]); continue
            if full.is_symlink():
                found.append([rel + "/", None, None, "link", "", ""]); continue
            keep.append(d)
        dirnames[:] = keep
        for name in sorted(filenames):
            if name == ".DS_Store":
                continue
            full = Path(dirpath) / name
            stub = name.startswith(".") and name.endswith(".icloud") and len(name) > 8
            shown = name[1:-len(".icloud")] if stub else name
            rel = (Path(dirpath) / shown).relative_to(root).as_posix()
            if is_skipped(rel, skipped):
                found.append([rel, None, None, "skipped", "", ""]); continue
            if stub:
                found.append([rel, None, None, "cloud", "n_cloud", ""]); continue
            state, size, note = inspect_file(full)
            fp = None
            if state == "ok":
                if hash_files:
                    try:
                        fp = fingerprint(full)
                    except OSError as e:
                        state, note = "unreadable", str(e.strerror or e)
                else:
                    state = "listed"
            found.append([rel, fp, size, state, "", note])
    present = {norm(r[0]) for r in found}
    unrecorded = [r for r in found if r[3] == "ok" and norm(r[0]) not in recorded]
    missing = [p for p in records if norm(p) not in present and not is_skipped(p, skipped)
               and not any(norm(p).startswith(b) for b in blocked)]
    if hash_files:
        for r in found:
            if r[3] == "ok" and norm(r[0]) in recorded:
                r[3] = "read" if records[recorded[norm(r[0])]] == r[1] else "changed"
        for m in sorted(missing):
            fp = records[m]
            gone_same = [x for x in missing if records[x] == fp]
            cands = [r for r in unrecorded if r[1] == fp]
            on_disk = [r for r in found if r[1] == fp]
            # A rename needs exactly one vanished path and exactly one file with that content. Any other
            # file with the same content (a copy, or the original still there) makes it ambiguous.
            if len(gone_same) == 1 and len(cands) == 1 and len(on_disk) == 1:
                cands[0][3], cands[0][4], cands[0][5] = "renamed", "n_renamed", m
                missing = [x for x in missing if x != m]
        for r in unrecorded:
            if r[3] == "ok":
                same = sorted(p for p, f in records.items() if f == r[1] and norm(p) in present and norm(p) != norm(r[0]))
                gone = sorted(p for p in missing if records[p] == r[1])
                if same:
                    r[4], r[5] = "n_dup", same[0]
                elif gone:
                    r[4], r[5] = "n_ambig", gone[0]
                r[3] = "new"
    else:
        for r in found:
            if r[3] == "listed":
                r[4] = "n_listed_rec" if norm(r[0]) in recorded else ""
    for r in found:
        if "|" in r[0] and r[3] not in ("skipped",) and not r[4]:
            r[4] = "n_pipe"
    rows = [tuple(r) for r in found]
    rows += [(m, records[m], None, "gone", "n_gone", "") for m in sorted(missing)]
    return rows


def show_sources(root, t, hash_files):
    try:
        records, skipped = intake_tables(root)
    except IntakeUnreadable as e:
        print(t["src_intake_bad"].format(e=e)); return 1
    rows = scan_sources(root, records, skipped, hash_files)
    if rows == "link":
        print(t["src_link_root"].format(d=SOURCES_DIR)); return 1
    if rows is None:
        print(t["src_none"].format(d=SOURCES_DIR)); return 0
    if not rows:
        print(t["src_empty"].format(d=SOURCES_DIR)); return 0
    print(t["src_head"])
    print("|---|---|---|---|---|")
    for rel, fp, size, state, key, arg in rows:
        note = t[key].format(p=arg) if key else arg
        print(f"| {cell(rel)} | {fp or ''} | {size_text(size) if size is not None else ''} | {t['st_' + state] if 'st_' + state in t else state} | {cell(note)} |")
    count = lambda s: sum(1 for r in rows if r[3] == s)
    other = sum(1 for r in rows if r[3] in ("cloud", "unreadable", "link", "nonreg", "listed"))
    print()
    print(t["src_counts"].format(n=len(rows), a=count("new"), b=count("read"), c=count("changed"), s=count("skipped"), o=other))
    print(t["src_remind"])
    if hash_files:
        print(t["src_cloud"])
    return 0


def show_fingerprint(root, t, arg):
    """The fingerprint of one file, for checking that it hasn't changed between reading it and writing a card."""
    path = Path(arg)
    full = path if path.is_absolute() else Path.cwd() / path
    if not os.path.lexists(full):
        print(t["fp_missing"].format(p=arg)); return 1
    try:
        rel = full.relative_to(root).as_posix()
    except ValueError:
        print(t["fp_outside"].format(p=arg)); return 1
    if has_link(root, full):
        print(t["fp_link"].format(p=arg)); return 1
    try:
        _, skipped = intake_tables(root)
    except IntakeUnreadable as e:
        print(t["src_intake_bad"].format(e=e)); return 1
    if is_skipped(rel, skipped):
        print(t["fp_skipped"].format(p=rel)); return 1
    name = full.name
    if name.startswith(".") and name.endswith(".icloud") and len(name) > 8:
        print(t["fp_cloud"].format(p=rel)); return 1
    state, _, note = inspect_file(full)
    if state == "cloud":
        print(t["fp_cloud"].format(p=rel)); return 1
    if state != "ok":
        print(t["fp_err"].format(p=rel, e=note or t["st_nonreg"])); return 1
    try:
        fp = fingerprint(full)
    except OSError as e:
        print(t["fp_err"].format(p=rel, e=e.strerror or e)); return 1
    print(t["fp_ok"].format(p=rel, f=fp))
    return 0


def main():
    ap = argparse.ArgumentParser(description="每张 Claim Card 列一行。")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--used-by", metavar="ID", help="列出引用这张卡的简历、追问卡和答案，以及各自要不要复核（D-020）")
    ap.add_argument("--health", action="store_true", help="只列出引用的卡在检查之后改过的文件（D-020）")
    ap.add_argument("--answers", metavar="JOB", help="interview/answers/ 里适用范围符合这个岗位的已审核答案，以及各自能否直接复用")
    ap.add_argument("--sources", action="store_true", help='列出 evidence/sources/ 里的文件和指纹，以及哪些是新的、读过之后变了、改了名或已跳过（不读文字）')
    ap.add_argument("--no-hash", action="store_true", help='配合 --sources：只列文件名和大小，不打开任何文件（云同步可能触发下载时用）')
    ap.add_argument("--fingerprint", metavar="FILE", help='打印单个文件的指纹，用来确认从读它到写卡之间它没变（已跳过的文件从不打开）')
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]
    if a.fingerprint:
        return show_fingerprint(deps.kit_root(a.claims), t, a.fingerprint)
    if a.sources:
        return show_sources(deps.kit_root(a.claims), t, not a.no_hash)
    if a.answers:
        return answers_for(deps.kit_root(a.claims), deps.load_cards(a.claims), a.answers, t)
    if a.used_by or a.health:
        root, cards = deps.kit_root(a.claims), deps.load_cards(a.claims)
        names = cc.BLOCK_NAMES[a.lang]
        rows = dependency_rows(root, cards, a.used_by)
        if a.used_by:
            if not rows:
                print(t["no_assets"].format(c=a.used_by)); return 0
            print(t["used_by"].format(n=len(rows), c=a.used_by))
            show = rows
        else:
            if not rows:
                print(t["health_ok"].format(n=0)); return 0
            show = [r for r in rows if r[2] in ("changed", "missing", "historical")]
        if show:
            print(t["dep_head"])
            print("|---|---|---|---|")
            for me, life, health, states in show:
                print(f"| {cell(me)} | {cell(life)} | {t[health]} | {cell(describe(states, t, names))} |")
        if a.health:
            count = lambda h: sum(1 for r in rows if r[2] == h)
            if not show:
                print(t["health_ok"].format(n=len(rows)))
            else:
                print(t["health_counts"].format(c=count("current"), k=count("changed") + count("missing"), h=count("historical")))
            unchecked = [r[0] for r in rows if r[2] == "not_checked"]
            if unchecked:
                print(t["health_unchecked"].format(n=len(unchecked), fs=", ".join(Path(u).name for u in unchecked)))
        return 0
    cards = []
    for p in sorted(Path(a.claims).glob("*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        fm = cc.front_matter(text)[0]
        cards.append((fm.get("id") or p.stem, summary(text), fm.get("status", ""),
                      fm.get("protected", "").lower() == "true", fm.get("role", ""), facets(text)))
    if not cards:
        print(t["none"].format(p=a.claims)); return 2
    print(t["head"])
    print("|---|---|---|---|---|---|")
    for cid, s, st, prot, role, fac in cards:
        print(f"| {cid} | {cell(s)} | {cell(st)} | {t['yes'] if prot else ''} | {cell(role)} | {cell('; '.join(fac))} |")
    print()
    if len(cards) <= FULL_READ_UP_TO:
        print(t["few"].format(n=len(cards)))
    else:
        print(t["many"].format(n=len(cards), k=", ".join(c[0] for c in cards if c[3]) or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
