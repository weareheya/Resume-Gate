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
退出码：0 = 已列出，2 = 没找到卡片。
"""
import argparse
import importlib.util
import re
import sys
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
        "ans_recheck": "recheck first",
        "ans_unchecked": "check against the cards first",
        "ans_draft": "not approved yet",
        "ans_none": "No reviewed answers fit {j}. Write new ones in interview/answers/ (copy _TEMPLATE.md).",
        "ans_skipped": "{n} other answer(s) are for another employer or job, so they're left out.",
        "no_job": "No job file jobs/{j}.md: employer-specific answers can't be matched, so only reusable ones are listed.",
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
        "ans_recheck": "先复核",
        "ans_unchecked": "先对照卡片检查",
        "ans_draft": "还没批准",
        "ans_none": "没有适用于 {j} 的已审核答案。新答案写在 interview/answers/（复制 _TEMPLATE.md）。",
        "ans_skipped": "另有 {n} 个答案是给别的公司或岗位的，没有列出。",
        "no_job": "找不到岗位文件 jobs/{j}.md：针对某家公司的答案没法匹配，只列出通用的。",
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
        out.append((p, fm.get("status", "") or "-", False, fm.get("type", ""), deps.generic_citations(text, known, recorded.get(deps.rel(p, root), set()))))
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


def scope_fits(scope, job_id, company):
    """reusable | employer: <name> | job: <id>. An empty scope counts as reusable."""
    kind, _, value = (scope or "reusable").partition(":")
    kind, value = kind.strip().lower(), value.strip().lower()
    if kind in ("reusable", "通用", ""):
        return True
    if kind in ("employer", "公司"):
        return bool(company) and (value in company.lower() or company.lower() in value)
    if kind in ("job", "岗位"):
        return value == job_id.lower()
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
        life, health = rows.get(me, (fm.get("status", "") or "-", "current"))
        if health in ("changed", "historical"):
            reuse = t["ans_recheck"]
        elif health == "not_checked":
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


def main():
    ap = argparse.ArgumentParser(description="每张 Claim Card 列一行。")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--used-by", metavar="ID", help="列出引用这张卡的简历、追问卡和答案，以及各自要不要复核（D-020）")
    ap.add_argument("--health", action="store_true", help="只列出引用的卡在检查之后改过的文件（D-020）")
    ap.add_argument("--answers", metavar="JOB", help="interview/answers/ 里适用范围符合这个岗位的已审核答案，以及各自能否直接复用")
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]
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
