#!/usr/bin/env python3
"""把 Resume-Gate 报告存成 PNG 图片，在对话里能直接看，也能发出去。

Many AI chat windows and preview panes don't run JavaScript, so a report file opened there shows
only the watermark. This renders it in headless Chrome (or Edge, Brave, Chromium) and saves an image.
Standard library only; it needs one of those browsers installed. Nothing leaves your computer.

Usage:  python3 scripts/report_png.py reports/<file>.html [--full] [--out <file>.png]
  default   the share card alone (1080 px wide). Works on full reports, -share.html copies and posters.
  --full    the whole report (2x resolution). Holds every private detail: keep it to yourself.
Set CHROME=/path/to/browser if the browser isn't found.
Exit code: 0 = written, 2 = no browser or the page didn't render.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"]


def find_browser():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    for n in NAMES:
        if shutil.which(n):
            return shutil.which(n)
    return None


def run(browser, args, profile):
    base = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", f"--user-data-dir={profile}", "--virtual-time-budget=3000"]
    return subprocess.run(base + args, capture_output=True, text=True, timeout=90)


def main():
    ap = argparse.ArgumentParser(description="Save a report as a PNG.")
    ap.add_argument("report")
    ap.add_argument("--full", action="store_true", help="the whole report instead of the share card")
    ap.add_argument("--out", help="output file (default: next to the report, <name>-card.png or <name>-full.png)")
    a = ap.parse_args()

    src = Path(a.report).resolve()
    if not src.exists():
        print(f"找不到 {src}"); return 2
    browser = find_browser()
    if not browser:
        print("没找到 Chrome、Edge、Brave 或 Chromium。装一个，或者设置 CHROME=/浏览器路径。"); return 2
    out = Path(a.out).resolve() if a.out else src.with_name(f"{src.stem}-{'full' if a.full else 'card'}.png")
    url = src.as_uri() + ("#png-full" if a.full else "#png-share")
    width, scale = (1100, 2) if a.full else (1080, 1)

    with tempfile.TemporaryDirectory() as profile:
        # Pass 1: let the page draw itself and report its height.
        dom = run(browser, [f"--window-size={width},1200", "--dump-dom", url], profile).stdout
        m = re.search(r'data-png="(\d+)"', dom)
        if not m:
            print("页面没画出来。这是 Resume-Gate 的报告吗？"); return 2
        height = int(m.group(1))
        # Pass 2: screenshot at exactly that size.
        run(browser, [f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
                      f"--screenshot={out}", url], profile)
    if not out.exists():
        print("浏览器没有生成截图。"); return 2
    print(f"已生成：{out}（{width * scale} × {height * scale} px）")
    if a.full:
        print("这张图是完整报告，里面有你的全部信息。不要发出去；要分享就用分享卡。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
