#!/usr/bin/env python3
"""rebuild_page.py — 用本地或云端数据库，重建未来技术长名单页面数据块

用法:
  python rebuild_page.py [模板.html] [输出.html] [--cloud]

默认:
  - 使用本 skill 内置的 tech-atlas.db（462 项，离线可用）
  - 加 --cloud 从云端 6622 下载最新版再重建
  - 模板默认取当前目录的 未来技术长名单-462项.html
  - 输出默认 未来技术长名单-云端版.html

零第三方依赖：urllib + sqlite3 + json + re + os
"""

import json, re, sqlite3, sys, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CLOUD_DB_URL = "http://115.190.229.115:6622/download/tech-atlas.db"
LOCAL_DB = os.path.join(HERE, "tech-atlas.db")
TEMPLATE = "未来技术长名单-462项.html"
OUTPUT = "未来技术长名单-云端版.html"


def rebuild(db_path, template, output):
    print(f"读取数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM technologies ORDER BY seq").fetchall()
    n = len(rows)
    conn.close()
    print(f"  技术数: {n} 项")

    L, AFULL = [], {}
    for r in rows:
        aj = json.loads(r["atlas_json"])
        f17 = aj.get("full17") or {}
        L.append({
            "id": r["id"], "nm": r["name"], "l1": r["flow"], "st": r["stage_index"],
            "mat": r["maturity"], "heat": r["heat"], "win": r["window"],
            "dom": r["dimension"], "dir": r["direction"],
            "dfn": r["definition"] or "", "c": f17.get("c", "#2f6fed"),
            "flag": r["ref_flagship"] or "", "src": r["data_source"] or "",
        })
        if f17:
            AFULL[str(r["id"])] = f17

    print("重建页面数据块...")
    html = open(template, encoding="utf-8").read()
    l_js = "const L462=" + json.dumps(L, ensure_ascii=False, separators=(",", ":")) + ";"
    a_js = "const AFULL=" + json.dumps(AFULL, ensure_ascii=False, separators=(",", ":")) + ";"
    html1, n1 = re.subn(r"const L462=\[.*?\];", l_js, html, count=1, flags=re.S)
    html2, n2 = re.subn(r"const AFULL=\{.*?\};", a_js, html1, count=1, flags=re.S)
    if n1 != 1 or n2 != 1:
        print(f"⚠️ 数据块替换异常（L462={n1}, AFULL={n2}），模板结构可能已变更")
        sys.exit(1)
    open(output, "w", encoding="utf-8").write(html2)
    print(f"✅ 完成: {output}（L462={len(L)} 项, AFULL={len(AFULL)} 项图谱）")


def main():
    args = sys.argv[1:]
    use_cloud = "--cloud" in args
    args = [a for a in args if a != "--cloud"]
    template = args[0] if len(args) > 0 else TEMPLATE
    output = args[1] if len(args) > 1 else OUTPUT

    if use_cloud:
        print("下载云端数据库...")
        dl = "tech-atlas-cloud.db"
        urllib.request.urlretrieve(CLOUD_DB_URL, dl)
        size = os.path.getsize(dl)
        print(f"  完成: {size/1048576:.1f} MB")
        rebuild(dl, template, output)
        os.remove(dl)
    else:
        if not os.path.exists(LOCAL_DB):
            print(f"❌ 本地数据库不存在: {LOCAL_DB}（加 --cloud 从云端下载）")
            sys.exit(1)
        rebuild(LOCAL_DB, template, output)


if __name__ == "__main__":
    main()