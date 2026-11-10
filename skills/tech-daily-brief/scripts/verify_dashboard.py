#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_dashboard.py — 验证 tech-daily-brief v2 仪表盘渲染正确且信息新鲜。

渲染检查（Chrome headless dump DOM 计数）:
- 六板块信息卡数量、原文链接数量、上车机会点数量、观点卡、专题卡、雷达多边形。

新鲜度守卫（不渲染也能判）:
- 【日期铁律】发布日必须是今天、信源日必须是昨天，否则直接 FAIL（归档历史日报加 --allow-past）;
- data 槽中每条 news 必须有 http(s) 原文链接。

用法:
    python verify_dashboard.py <path/to/dashboard.html> [--chrome <chrome.exe>] [--allow-past]
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time

DEFAULT_CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

SLOT = re.compile(r'<script id="tdb-data" type="application/json">(.*?)</script>', re.S)
STRIP_SCRIPTS = re.compile(r"<script\b(?![^>]*tdb-data).*?</script>", re.S | re.I)

CHECKS = [
    # (label, pattern, min, max_or_None)  —— 数量随板块数灵活，放宽区间
    ("ncard news cards", r'class="ncard"', 16, 48),
    ("orig-link 原文链接", r'原文 ↗', 16, 48),
    ("opp 上车机会点", r'🚗 上车机会点', 16, 48),
    ("op opinion cards", r'class="op ', 4, 10),
    ("topic cards 专题卡", r'class="ttopic"', 4, 8),
    ("radar polygon", r"points=", 4, None),
]


def find_chrome(cli_arg):
    if cli_arg:
        return cli_arg if os.path.exists(cli_arg) else None
    for p in DEFAULT_CHROME:
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="dashboard html file")
    ap.add_argument("--chrome", help="path to chrome/edge executable")
    ap.add_argument("--allow-past", action="store_true",
                    help="归档历史日报时使用：放宽『发布日=今天』的日期铁律校验")
    args = ap.parse_args()

    html = os.path.abspath(args.html)
    if not os.path.exists(html):
        print(f"FAIL: file not found: {html}")
        sys.exit(2)

    with open(html, encoding="utf-8") as f:
        src = f.read()

    ok = True

    # ---------- 新鲜度守卫（静态检查） ----------
    m = SLOT.search(src)
    data = None
    if m:
        try:
            data = json.loads(m.group(1).replace(r"<\/script>", "</script>"))
        except Exception as e:
            print(f"  [FAIL] data 槽 JSON 解析失败: {e}")
            ok = False
    else:
        print("  [FAIL] 未找到数据槽 <script id=\"tdb-data\">")
        ok = False

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    if data:
        for key, expected in (("date", today), ("source_date", yesterday)):
            ds = data.get(key, "")
            try:
                d = datetime.date.fromisoformat(ds)
                if d == expected:
                    print(f"  [PASS] 日期铁律：{key}={ds}（{'今天' if key == 'date' else '昨天'}）")
                elif args.allow_past and (today - d).days <= 60:
                    print(f"  [PASS] 归档豁免(--allow-past)：{key}={ds}（{(today - d).days} 天前）")
                else:
                    want = '今天' if key == 'date' else '昨天'
                    print(f"  [FAIL] 日期铁律：{key} 必须是{want} {expected}，实际是 {ds} —— 日报永远生成当天版本，禁止沿用旧日期")
                    ok = False
            except ValueError:
                print(f"  [FAIL] {key} 日期格式错误: {ds!r}")
                ok = False

        mods = {x.get("key") for x in data.get("modules", [])}
        cnt = {}
        for n in data.get("news", []):
            cnt[n.get("module")] = cnt.get(n.get("module"), 0) + 1
            if not str(n.get("url", "")).startswith(("http://", "https://")):
                print(f"  [FAIL] 条目缺少原文链接: {str(n.get('title'))[:30]}")
                ok = False
            if not n.get("opp"):
                print(f"  [FAIL] 条目缺少【上车机会点】: {str(n.get('title'))[:30]}")
                ok = False
        # 板块数量灵活：4-8 个自选板块、每板块 2-6 条、总数≥16
        if not (4 <= len(mods) <= 8):
            print(f"  [FAIL] 板块数应为 4-8 个（按需自选），实际 {len(mods)}")
            ok = False
        else:
            print(f"  [PASS] 板块数 {len(mods)} 个（4-8 个自选范围内）")
        for k in mods:
            c = cnt.get(k, 0)
            if not (2 <= c <= 6):
                print(f"  [FAIL] 板块 {k} 条数应为 2-6 条，实际 {c}")
                ok = False
            else:
                print(f"  [PASS] 板块 {k}: {c} 条")
        if len(data.get("news", [])) < 16:
            print(f"  [FAIL] 总条数应 ≥16，实际 {len(data.get('news', []))}")
            ok = False
        # weekly 七日全景（可选）
        wk = data.get("weekly")
        if wk:
            days = wk.get("days", [])
            ds = [d.get("date", "") for d in days]
            if not (5 <= len(days) <= 9) or ds != sorted(ds):
                print(f"  [FAIL] weekly.days 应覆盖 5-9 天且按日期升序，实际 {len(days)} 天")
                ok = False
            else:
                total = sum(d.get("count", 0) for d in days)
                print(f"  [PASS] 七日全景：{len(days)} 天 · 周库 {total} 条 · 每日精选 "
                      f"{sum(len(d.get('picks', [])) for d in days)} 条")
            for d in days:
                for p in d.get("picks", []):
                    if not str(p.get("url", "")).startswith(("http://", "https://")):
                        print(f"  [FAIL] 七日全景每日精选缺原文: {str(p.get('title'))[:30]}")
                        ok = False
        bad_ops = [o for o in data.get("ops", []) if o.get("name") in ("业内人士", "网友", "专家") or not o.get("url")]
        if bad_ops:
            print(f"  [FAIL] 观点不符合大牛规则（需具名+原文链接）: {[o.get('name') for o in bad_ops]}")
            ok = False
        else:
            print(f"  [PASS] 大牛观点 {len(data.get('ops', []))} 条（具名 + 原文链接）")

    # ---------- 渲染检查 ----------
    chrome = find_chrome(args.chrome)
    if not chrome:
        print("  [warn] 未找到 Chrome/Edge，跳过渲染检查（可用 --chrome 指定）")
    else:
        url = "file:///" + html.replace("\\", "/")
        tmp = tempfile.mkdtemp(prefix="tdb-verify-")
        out = os.path.join(tmp, "dom.html")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--virtual-time-budget=6000", "--dump-dom", url]
        t0 = time.time()
        with open(out, "w", encoding="utf-8") as f:
            r = subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=120)
        if r.returncode != 0:
            print(f"  [FAIL] chrome exited with code {r.returncode}")
            ok = False
        else:
            with open(out, encoding="utf-8", errors="replace") as f:
                dom = f.read()
            print(f"  [info] rendered in {time.time()-t0:.1f}s, DOM {len(dom)//1024}KB")
            rendered = STRIP_SCRIPTS.sub("", dom)
            for label, pat, lo, hi in CHECKS:
                n = len(re.findall(pat, rendered))
                if hi is None:
                    good, expect = n >= lo, f">= {lo}"
                else:
                    good, expect = lo <= n <= hi, f"{lo}-{hi}"
                if not good:
                    ok = False
                print(f"  [{'PASS' if good else 'FAIL'}] {label}: found {n} (expected {expect})")
            # 七日全景渲染检查（仅当 data 含 weekly 时）
            if data and data.get("weekly") and data["weekly"].get("days"):
                expect_days = len(data["weekly"]["days"])
                n_days = len(re.findall(r'class="wk-day[ "]', rendered))
                n_picks = len(re.findall(r'class="wk-picks"', rendered))
                good_d, good_p = n_days == expect_days, n_picks == expect_days
                if not (good_d and good_p):
                    ok = False
                print(f"  [{'PASS' if good_d else 'FAIL'}] wk-day 每日卡片: found {n_days} (expected {expect_days})")
                print(f"  [{'PASS' if good_p else 'FAIL'}] wk-picks 每日精选区: found {n_picks} (expected {expect_days})")
        try:
            os.remove(out)
            os.rmdir(tmp)
        except OSError:
            pass

    print("RESULT:", "PASS - dashboard renders correctly & data is fresh" if ok else "FAIL - 修正 data.json 后重新 build/verify")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
