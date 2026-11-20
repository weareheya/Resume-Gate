#!/usr/bin/env python3
"""在拿简历对照证据库之前，先检查证据库本身。只用标准库。

它检查什么：
  1. 每张 Claim Card 都有 `id`，且没有两张卡共用一个 ID。
  2. `status` 是 需复核 | Safe to draft | 仅面试 | 已停用 之一（英文写法也认）。
  3. `protected` 是 true 或 false。
  4. 数字表「核实」一列的每个值都是 ✓、「待核实」或空白。空白按已确认处理（数字是本人给的），
     只提醒你打勾；其他值算错误，因为 check_claims.py 会把它当作未确认。
  5. evidence/profile.md 至少填了一条任职（只是提醒，不算错误）。

用法：
  python3 scripts/validate_evidence.py [--claims evidence/claims] [--profile evidence/profile.md] [--lang en|zh]

退出码：0 = 没有错误，1 = 发现错误，2 = 没能运行。
"""
import argparse
import importlib.util
import sys
from pathlib import Path

DEFAULT_LANG = "zh"

spec = importlib.util.spec_from_file_location("check_claims", Path(__file__).with_name("check_claims.py"))
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

STATUSES = {"needs review", "safe to draft", "interview only", "retired", "需复核", "仅面试", "已停用"}
PENDING = {"to verify", "unverified", "待核实", "待补", "未核实"}

T = {
    "en": {
        "no_claims": "No claim cards found in {p}",
        "no_id": "{f}: no `id:` in the front matter",
        "dup": "{c} is used by more than one card: {f}",
        "status": "{f}: status \"{s}\" isn't one of Needs review / Safe to draft / Interview only / Retired",
        "protected": "{f}: protected must be true or false, not \"{v}\"",
        "no_verified": "{f}: the Numbers table has no Verified column; its numbers count as confirmed. Add the column to mark any that aren't",
        "blank": "{f}: {k} number(s) with a blank Verified cell count as confirmed. Tick them ✓ when you next look at the card",
        "verified": "{f}: Verified value \"{v}\" on row \"{r}\" is neither ✓ nor \"to verify\"",
        "no_profile": "{p} is missing or lists no roles. Role headings and Education aren't checked until it's filled in",
        "ok": "OK: {n} cards checked, no errors{w}",
        "fail": "FAILED: {e} error(s)",
    },
    "zh": {
        "no_claims": "在 {p} 里没有找到 Claim Card",
        "no_id": "{f}：front matter 里没有 `id:`",
        "dup": "{c} 被多张卡使用：{f}",
        "status": "{f}：状态「{s}」不是 需复核 / Safe to draft / 仅面试 / 已停用 之一",
        "protected": "{f}：protected 只能是 true 或 false，不是「{v}」",
        "no_verified": "{f}：数字表没有「核实」一列，里面的数字都按已确认处理。需要标出未确认的，就加上这一列",
        "blank": "{f}：有 {k} 个数字的「核实」一栏是空的，按已确认处理。下次看这张卡时顺手打上 ✓",
        "verified": "{f}：「{r}」这一行的核实值「{v}」既不是 ✓ 也不是「待核实」",
        "no_profile": "{p} 不存在或没有填写任职。填好之前，职位标题和教育背景不会被检查",
        "ok": "通过：检查了 {n} 张卡，没有错误{w}",
        "fail": "未通过：{e} 个错误",
    },
}


def main():
    ap = argparse.ArgumentParser(description="检查证据库。")
    ap.add_argument("--claims", default="evidence/claims")
    ap.add_argument("--profile")
    ap.add_argument("--lang", choices=["en", "zh"], default=DEFAULT_LANG)
    a = ap.parse_args()
    t = T[a.lang]
    files = [f for f in sorted(Path(a.claims).glob("*.md")) if not f.name.startswith("_")] if Path(a.claims).is_dir() else []
    if not files:
        print(t["no_claims"].format(p=a.claims)); return 2

    errors, warns, seen = 0, 0, {}

    def err(msg):
        nonlocal errors
        print("ERROR " + msg); errors += 1

    def warn(msg):
        nonlocal warns
        print("WARN  " + msg); warns += 1

    for f in files:
        text = f.read_text(encoding="utf-8")
        fm, start = cc.front_matter(text)
        cid = fm.get("id", "")
        if not cid:
            err(t["no_id"].format(f=f.name)); continue
        seen.setdefault(cid, []).append(f.name)
        if fm.get("status", "").strip().lower() not in STATUSES:
            err(t["status"].format(f=f.name, s=fm.get("status", "")))
        if fm.get("protected", "false").strip().lower() not in ("true", "false"):
            err(t["protected"].format(f=f.name, v=fm.get("protected")))
        lines, section, numbers = text.split("\n")[start:], "", []
        for line in lines:
            h = cc.HEADING_RE.match(line.strip())
            if h:
                section = h.group(2).strip().lower()
            elif section in ("numbers and what they mean", "数字与口径") and line.strip().startswith("|"):
                numbers.append(line)
        for header, rows in cc.parse_tables(numbers):
            vcol = next((i for i, c in enumerate(header) if c in cc.VERIFY_HEADERS), None)
            if vcol is None:
                warn(t["no_verified"].format(f=f.name)); continue
            blank = 0
            for cells in rows:
                if not cc.tokens(cells[0]):
                    continue  # a row with no number in it, e.g. "(none yet)"
                v = cells[vcol].strip() if vcol < len(cells) else ""
                if not v:
                    blank += 1
                elif v.lower() not in cc.VERIFIED_OK and v.lower() not in PENDING:
                    err(t["verified"].format(f=f.name, v=v, r=cells[0][:40]))
            if blank:
                warn(t["blank"].format(f=f.name, k=blank))
    for cid, names in sorted(seen.items()):
        if len(names) > 1:
            err(t["dup"].format(c=cid, f=", ".join(names)))

    ppath = Path(a.profile) if a.profile else Path(a.claims).parent / "profile.md"
    profile = cc.load_profile(ppath)
    if not profile or not profile[0]:
        warn(t["no_profile"].format(p=ppath))

    w = ((f" ({warns} WARN)" if a.lang == "en" else f"（{warns} 条提醒）") if warns else "")
    print(t["fail"].format(e=errors) if errors else t["ok"].format(n=len(files), w=w))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
