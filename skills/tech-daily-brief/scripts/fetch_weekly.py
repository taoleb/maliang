#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_weekly.py — 从 6606「马良洞见·智驭未来」周情报库拉取数据，
生成可直接合并进 data.json 的 `weekly` 片段（七日全景）。

用法:
    python fetch_weekly.py [--base http://115.190.229.115:6606] [-o weekly_fragment.json] [--merge data.json]

产出结构（对应 data.json 的 "weekly" 字段）:
{
  "source": "6606 周情报库",
  "week_total": 333,
  "days": [
    {"date": "2026-08-21", "weekday": "周五", "count": 40,
     "cats": {"机器人": 15, "人工智能": 12, ...},
     "picks": [{"title": "...", "url": "https://...", "cat": "机器人"}, ...]}
  ],
  "trends": [{"cat": "半导体", "summary": "本周..."}]
}

说明:
- 6606 的 /api/information/download/weekly 返回 xlsx（zip 包），脚本内置最小
  xlsx 解析（标准库，无第三方依赖）；
- 每日条目按 category 聚合，每日精选默认取 probability（相关度）最高的 3 条；
- trends 来自 /api/trends/latest（每类目一段周趋势摘要）。
"""
import argparse
import io
import json
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "tech-daily-brief/2.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_xlsx_rows(blob):
    """最小 xlsx 解析：返回 [(cell, cell, ...), ...]，字符串已解引用。"""
    z = zipfile.ZipFile(io.BytesIO(blob))
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        tname = "{%s}t" % NS["m"]
        for si in root.findall("m:si", NS):
            ss.append("".join(t.text or "" for t in si.iter(tname)))
    sheet = z.read("xl/worksheets/sheet1.xml")
    root = ET.fromstring(sheet)
    rows = []
    for r in root.findall(".//m:row", NS):
        vals = []
        for c in r.findall("m:c", NS):
            t, v = c.get("t"), c.find("m:v", NS)
            if v is None:
                vals.append("")
            elif t == "s":
                vals.append(ss[int(v.text)])
            else:
                vals.append(v.text)
        rows.append(vals)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://115.190.229.115:6606")
    ap.add_argument("-o", "--out", default="weekly_fragment.json")
    ap.add_argument("--merge", help="可选：把 weekly 片段合并进该 data.json 路径")
    ap.add_argument("--picks", type=int, default=3, help="每日精选条数（按相关度取前 N）")
    ap.add_argument("--days", type=int, default=7, help="保留最近 N 天（默认 7，即『七日全景』）")
    args = ap.parse_args()

    base = args.base.rstrip("/")
    blob = fetch(base + "/api/information/download/weekly")
    rows = parse_xlsx_rows(blob)
    if len(rows) < 2:
        print("FAIL: 周报表为空")
        sys.exit(1)
    header = rows[0]
    idx = {h: i for i, h in enumerate(header)}
    need = {"title", "url", "category", "created_at"}
    if not need.issubset(idx):
        print(f"FAIL: 周报表缺列 {need - set(idx)}")
        sys.exit(1)
    prob_i = idx.get("probability")

    by_day = defaultdict(list)
    for r in rows[1:]:
        if len(r) <= max(idx.values()):
            continue
        day = (r[idx["created_at"]] or "")[:10]
        if len(day) != 10:
            continue
        prob = 0.0
        if prob_i is not None and r[prob_i]:
            try:
                prob = float(r[prob_i])
            except ValueError:
                prob = 0.0
        by_day[day].append({
            "title": r[idx["title"]], "url": r[idx["url"]],
            "cat": r[idx["category"]] or "其他", "prob": prob,
        })

    import datetime
    day_keys = sorted(by_day)[-args.days:]
    days = []
    for d in day_keys:
        items = by_day[d]
        picks = sorted(items, key=lambda x: -x["prob"])[:args.picks]
        wd = WD[datetime.date.fromisoformat(d).weekday()]
        days.append({
            "date": d, "weekday": wd, "count": len(items),
            "cats": dict(Counter(x["cat"] for x in items).most_common()),
            "picks": [{"title": p["title"], "url": p["url"], "cat": p["cat"]} for p in picks],
        })

    trends = []
    try:
        t = json.loads(fetch(base + "/api/trends/latest").decode("utf-8"))
        for cat, v in t.items():
            if isinstance(v, dict) and v.get("trend_summary"):
                trends.append({"cat": cat, "summary": v["trend_summary"]})
    except Exception as e:
        print(f"[warn] trends 拉取失败（不影响主数据）: {e}")

    fragment = {
        "source": "6606 周情报库（马良洞见·智驭未来）",
        "week_total": sum(d["count"] for d in days),
        "days": days,
        "trends": trends,
    }
    json.dump(fragment, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"OK: {args.out}（{len(days)} 天 · 周库 {fragment['week_total']} 条 · 趋势 {len(trends)} 类）")

    if args.merge:
        data = json.load(open(args.merge, encoding="utf-8"))
        data["weekly"] = fragment
        json.dump(data, open(args.merge, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"OK: 已把 weekly 合并进 {args.merge}")


if __name__ == "__main__":
    main()
