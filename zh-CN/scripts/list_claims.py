#!/usr/bin/env python3
"""每张 Claim Card 列一行，证据库很大时 AI 也能低成本地过一遍。只用标准库。

输出一张表：ID、卡片的一句话、状态、是否受保护、职位、能力切面。
每次运行都现场读卡、不写任何文件，所以清单不会过期，也不会多出一个要保护隐私的文件。

AI 怎么用（WORKFLOW S2）：卡片不超过 15 张时，照旧每张读全文。超过时，先读这份清单，再打开所有受保护的卡，
以及一句话、职位或能力切面和岗位沾边的卡读全文。每张卡仍要写进证据表（D-019），没用的可以合成一行。

用法：  python3 scripts/list_claims.py [--claims evidence/claims] [--lang en|zh]
        python3 scripts/list_claims.py --used-by C-001   哪些简历、追问卡、答案引用了这张卡，各自要不要复核（D-020）
        python3 scripts/list_claims.py --health          只列出引用的卡改过、需要复核的文件
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
        "edited": "edited after it was recorded",
        "health_ok": "{n} file(s) cite cards; none needs a recheck.",
        "health_counts": "{c} current, {k} need a recheck, {h} sent before a change.",
        "health_unchecked": "Not checked yet ({n}): {fs}. Normal for versions made before 0.7.0; check one when you reuse or send it.",
        "no_assets": "No resumes, follow-up cards or answers cite {c}.",
        "used_by": "{n} file(s) cite {c}:",
        "major": "major",
        "minor": "minor",
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
        "edited": "记录之后被改过",
        "health_ok": "共 {n} 个文件引用了卡片，没有需要复核的。",
        "health_counts": "最新 {c} 个，需要复核 {k} 个，改动前已投递 {h} 个。",
        "health_unchecked": "还没检查过（{n} 个）：{fs}。0.7.0 之前做的版本都是这样，等再次复用或投递时再检查。",
        "no_assets": "没有简历、追问卡或答案引用 {c}。",
        "used_by": "{n} 个文件引用了 {c}：",
        "major": "重大",
        "minor": "一般",
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


def assets(root, known):
    """Every resume, follow-up card and answer, with the cards it cites:
    [(path, lifecycle, frozen, job type, {card: [lines]})]."""
    out = []
    for p in sorted((root / "cv" / "resumes").glob("*.md")):
        if p.name.startswith("_"):
            continue
        r = cc.scan_resume(p)
        fm = r["fm"]
        cites = {c: cc.lines_for(r["needs"], c) for c in sorted(r["used"] & known)}
        frozen = cc.frozen_entry(p) is not None or fm.get("status", "").strip().lower() == "sent"
        out.append((p, fm.get("status", "") or "-", frozen, fm.get("type", ""), cites))
    for p in sorted((root / "interview").rglob("*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        fm = cc.front_matter(text)[0]
        out.append((p, fm.get("status", "") or "-", False, fm.get("type", ""), deps.generic_citations(text, known)))
    return out


def dependency_rows(root, cards, only=None):
    """[(file, lifecycle, health, {card: (state, detail)})], health one of current / changed /
    historical / not_checked. `only` limits it to one card."""
    records = deps.read_records(root)
    rows = []
    for p, life, frozen, ty, cites in assets(root, set(cards)):
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
            parts.append(f"{c}: " + ", ".join(names.get(x, x) for x in d["blocks"]) + " · " + (t["major"] if d["major"] else t["minor"]))
        elif st == "not_checked" and d == "edited":
            parts.append(f"{c}: {t['edited']}")
    return "; ".join(parts)


def main():
    ap = argparse.ArgumentParser(description="每张 Claim Card 列一行。")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--used-by", metavar="ID", help="列出引用这张卡的简历、追问卡和答案，以及各自要不要复核（D-020）")
    ap.add_argument("--health", action="store_true", help="只列出引用的卡在检查之后改过的文件（D-020）")
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]
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
            show = [r for r in rows if r[2] in ("changed", "historical")]
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
                print(t["health_counts"].format(c=count("current"), k=count("changed"), h=count("historical")))
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
