#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_daily.py — 把 data.json 注入 tech-daily-brief 模板。

用法:
    python build_daily.py <data.json> <输出.html> [--template <template-daily.html>]

规则:
- 只替换模板中 <script id="tdb-data" type="application/json">...</script> 数据槽，
  不碰任何结构 / CSS / 渲染逻辑；
- 注入前做结构自检：板块 4-8 个自选、每板块 2-6 条、总条数 ≥16、每条有真实 URL、观点带来源；
- 【日期铁律】data.date 必须等于系统今天（防止把旧日报当"今天"交付）；
  data.source_date 必须等于昨天。归档历史日报请加 --allow-past 跳过该校验；
- 若含 weekly 七日全景：校验 days 覆盖 7 天且按日期升序、每日精选条目带 URL。
"""
import argparse
import datetime
import json
import os
import re
import sys

MODULE_MIN, MODULE_MAX = 4, 8          # 板块数量灵活：4-8 个自选
PER_MODULE_MIN, PER_MODULE_MAX = 2, 6  # 每板块条数灵活：2-6 条
NEWS_MIN_TOTAL = 16                    # 总条数下限
SLOT = re.compile(
    r'(<script id="tdb-data" type="application/json">)(.*?)(</script>)', re.S
)


def check(data, allow_past=False):
    errs = []
    for k in ("date", "source_date", "modules", "news", "ops", "topics"):
        if k not in data:
            errs.append(f"缺少顶层字段: {k}")
    if errs:
        return errs

    # ---- 日期铁律：发布日必须是今天，信源日必须是昨天 ----
    if not allow_past:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        try:
            d = datetime.date.fromisoformat(data["date"])
            if d != today:
                errs.append(
                    f"【日期铁律】发布日必须是今天 {today}，data.date 却是 {data['date']}"
                    f"（日报永远生成当天版本，禁止沿用旧日期；归档请加 --allow-past）"
                )
        except ValueError:
            errs.append(f"date 格式错误（应为 YYYY-MM-DD）: {data['date']!r}")
        try:
            sd = datetime.date.fromisoformat(data["source_date"])
            if sd != yesterday:
                errs.append(f"【日期铁律】信源日必须是昨天 {yesterday}，data.source_date 却是 {data['source_date']}")
        except ValueError:
            errs.append(f"source_date 格式错误（应为 YYYY-MM-DD）: {data['source_date']!r}")

    news = data["news"]
    count = {}
    for n in news:
        for k in ("title", "summary", "opp", "url", "module", "source"):
            if not n.get(k):
                errs.append(f"NEWS 缺字段 {k}: {str(n.get('title'))[:30]}")
        url = n.get("url", "")
        if not (url.startswith("http://") or url.startswith("https://")):
            errs.append(f"NEWS url 非法: {str(n.get('title'))[:30]} -> {url[:50]}")
        count[n.get("module")] = count.get(n.get("module"), 0) + 1

    # ---- 板块数量灵活：4-8 个自选板块，每板块 2-6 条 ----
    mods = data["modules"]
    mod_keys = [m.get("key") for m in mods]
    if not (MODULE_MIN <= len(mods) <= MODULE_MAX):
        errs.append(f"板块数应为 {MODULE_MIN}-{MODULE_MAX} 个（按需自选），实际 {len(mods)} 个")
    for m in mods:
        for k in ("key", "name", "color"):
            if not m.get(k):
                errs.append(f"MODULE 缺字段 {k}: {m}")
    unknown = [k for k in count if k not in mod_keys]
    if unknown:
        errs.append(f"NEWS 引用了未定义的板块: {unknown}")
    for key in mod_keys:
        c = count.get(key, 0)
        if not (PER_MODULE_MIN <= c <= PER_MODULE_MAX):
            errs.append(f"板块 {key} 条数应为 {PER_MODULE_MIN}-{PER_MODULE_MAX} 条，实际 {c} 条")
    if len(news) < NEWS_MIN_TOTAL:
        errs.append(f"总条数应 ≥{NEWS_MIN_TOTAL}，实际 {len(news)}")

    # ---- weekly 七日全景（可选）----
    wk = data.get("weekly")
    if wk:
        for k in ("source", "days"):
            if not wk.get(k):
                errs.append(f"WEEKLY 缺字段 {k}")
        days = wk.get("days", [])
        if not (5 <= len(days) <= 9):
            errs.append(f"WEEKLY.days 应覆盖 5-9 天（通常为 7 天），实际 {len(days)}")
        ds = [d.get("date", "") for d in days]
        if ds != sorted(ds):
            errs.append("WEEKLY.days 未按日期升序排列")
        for d in days:
            if not d.get("date") or d.get("count") is None:
                errs.append(f"WEEKLY.day 缺 date/count: {d.get('date')}")
            for p in d.get("picks", []):
                if not (p.get("title") and str(p.get("url", "")).startswith(("http://", "https://"))):
                    errs.append(f"WEEKLY 每日精选缺 title/url: {str(p.get('title'))[:30]}")

    for o in data["ops"]:
        for k in ("name", "title", "quote", "url", "stance"):
            if not o.get(k):
                errs.append(f"OPS 缺字段 {k}: {str(o.get('name'))}")
        if o.get("name") in ("业内人士", "网友", "专家"):
            errs.append(f"观点发言人必须是具名大牛，不允许: {o.get('name')}")

    if not data["topics"]:
        errs.append("topics 专题候选为空（至少 4 个）")
    for t in data["topics"]:
        for k in ("title", "why", "points"):
            if not t.get(k):
                errs.append(f"TOPIC 缺字段 {k}: {str(t.get('title'))[:30]}")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="data.json 路径")
    ap.add_argument("out", help="输出 html 路径")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--template", default=os.path.join(here, "..", "assets", "template-daily.html"))
    ap.add_argument("--allow-past", action="store_true",
                    help="归档历史日报时使用：跳过『发布日必须是今天』校验")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    errs = check(data, allow_past=args.allow_past)
    if errs:
        print("数据自检未通过，请先修正 data.json：")
        for e in errs:
            print("  ✗", e)
        sys.exit(1)

    with open(args.template, encoding="utf-8") as f:
        tpl = f.read()

    # JSON 中的 </script> 会破坏注入，转义掉
    payload = json.dumps(data, ensure_ascii=False, indent=None).replace("</script>", r"<\/script>")
    out, n = SLOT.subn(lambda m: m.group(1) + payload + m.group(3), tpl, count=1)
    if n != 1:
        print("FAIL: 模板中未找到数据槽 <script id=\"tdb-data\">")
        sys.exit(2)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK: 已生成 {args.out}（{os.path.getsize(args.out)//1024}KB，{len(data['news'])} 条资讯 / {len(data['ops'])} 条观点 / {len(data['topics'])} 个专题）")


if __name__ == "__main__":
    main()
