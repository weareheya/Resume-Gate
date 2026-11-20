#!/usr/bin/env python3
"""每张 Claim Card 列一行，证据库很大时 AI 也能低成本地过一遍。只用标准库。

输出一张表：ID、卡片的一句话、状态、是否受保护、职位、能力切面。
每次运行都现场读卡、不写任何文件，所以清单不会过期，也不会多出一个要保护隐私的文件。

AI 怎么用（WORKFLOW S2）：卡片不超过 15 张时，照旧每张读全文。超过时，先读这份清单，再打开所有受保护的卡，
以及一句话、职位或能力切面和岗位沾边的卡读全文。每张卡仍要写进证据表（D-019），没用的可以合成一行。

用法：  python3 scripts/list_claims.py [--claims evidence/claims] [--lang en|zh]
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

T = {
    "en": {
        "head": "| ID | Summary | Status | Protected | Role | Facets |",
        "yes": "yes",
        "none": "No claim cards found in {p}",
        "few": "{n} cards: few enough to read every card in full.",
        "many": "{n} cards. Read in full: every protected card ({k}), and every card whose summary, role or facets touch the job. Every card still goes in the evidence table; unused ones can share a line.",
    },
    "zh": {
        "head": "| ID | 一句话 | 状态 | 受保护 | 职位 | 能力切面 |",
        "yes": "是",
        "none": "{p} 里没有找到 Claim Card",
        "few": "共 {n} 张卡：数量不多，每张都读全文。",
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


def main():
    ap = argparse.ArgumentParser(description="每张 Claim Card 列一行。")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]
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
