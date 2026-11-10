---
name: tech-atlas
description: 云端数据驱动的未来技术长名单 × 新兴技术图谱流水线。本地内置 462 项技术图谱数据库，云端 6622 提供最新数据。用户问一项技术时，优先查本地库→有则直接返回图谱→无则查云端6622→还没有才搜集信息生成。触发词：查技术、技术图谱、技术档案、新兴技术、未来技术、462项、长名单、技术全景、某技术怎么样、某技术是什么、技术库查询、技术搜索、技术百科、云端同步、更新长名单、生成图谱报告、导出表格。当用户需要查询某项技术的图谱档案、从云端更新数据、重建长名单页面、或导出表格/PPT时使用。
agent_created: true
metadata:
  maliang:
    emoji: "🗺️"
    always: false
---

# 云端技术图谱流水线（Cloud Tech Atlas Pipeline）

**核心优先级：用户问技术 → 查本地库 → 有则直接返回图谱 → 无则查云端 → 还没有才搜集生成**

## 目录结构

```
cloud-tech-atlas-pipeline/
├── SKILL.md                    ← 主指令文件
├── tech-atlas.db               ← 内置数据库（462 项，离线可用，18MB）
├── rebuild_page.py             ← 重建页面脚本（本地/云端双模式）
└── references/
    ├── database-schema.md      ← 数据库 schema 参考
    ├── mcp-protocol.md         ← MCP 协议与调用方式
    ├── cloud-deploy.md         ← 云端部署说明
    ├── extract-prompt.md       ← 每日抽取规则契约
    └── pitfalls.md             ← 踩坑记录
```

## 云端服务端点

| 端点 | 说明 |
|---|---|
| `http://115.190.229.115:6622/mcp` | MCP JSON-RPC 接口（7 个工具） |
| `http://115.190.229.115:6622/health` | 健康检查 |
| `http://115.190.229.115:6622/api/daily-intel` | REST 查询每日情报 |
| `http://115.190.229.115:6622/download/tech-atlas.db` | 下载完整数据库（18MB） |
| `http://115.190.229.115:6600` | 技术日报监测系统（只读；账号密码请通过环境变量 TECH_DAILY_USER / TECH_DAILY_PASSWORD 配置，不要写入技能文件） |

## 云端 MCP 工具速查（POST /mcp）

| 工具 | 用途 |
|---|---|
| `tech_list` | 长名单筛选分页（flow/dimension/direction/stage/sort/limit/offset） |
| `tech_atlas` | 单项技术 17 模块图谱（name，模糊匹配+旗舰路由） |
| `tech_search` | 关键词搜索（名称/定义/前瞻/别名） |
| `taxonomy_tree` | 两流三底座分类体系 |
| `tech_stats` | 数据库统计信息 |
| `daily_intel` | 每日重点技术情报（date='latest' 查最新，支持 tech_name/domain/value_level 过滤） |
| `intel_ingest_log` | 入库记录摘要（运维用） |

---

## 工作模式（按优先级排列）

### 模式 1（最优先）：查本地库 → 返回技术图谱

**用户问"某技术怎么样"、"某技术是什么"、"查一下某技术"时，第一步永远是查本地数据库。**

```python
import sqlite3, json

conn = sqlite3.connect("tech-atlas.db")
conn.row_factory = sqlite3.Row

# 1) 精确匹配
name = "用户说的技术名"
r = conn.execute("SELECT * FROM technologies WHERE name=?", (name,)).fetchone()

# 2) 模糊匹配（找不到时）
if not r:
    rows = conn.execute("SELECT id, name, flow, dimension, stage, maturity, definition FROM technologies WHERE name LIKE ?", (f"%{name}%",)).fetchall()
    if rows:
        # 让用户确认选哪个
        for i, rr in enumerate(rows):
            print(f"  {i+1}. {rr['name']} | {rr['flow']} | {rr['stage']} | {rr['definition'][:60]}")
        # 用户选完后 r = rows[选中]
    else:
        r = None  # 本地无匹配 → 切模式 2

# 3) 找到 → 返回 17 模块图谱
if r:
    atlas = json.loads(r["atlas_json"])
    full17 = atlas.get("full17", {})
    result = {
        "id": r["id"], "name": r["name"], "flow": r["flow"],
        "dimension": r["dimension"], "direction": r["direction"],
        "stage": r["stage"], "maturity": r["maturity"], "heat": r["heat"],
        "definition": r["definition"],
        "p1_技术六维档案": full17.get("p1",{}),
        "p2_技术指标": full17.get("p2",{}),
        "p3_技术成熟度": full17.get("p3",{}),
        "p4_技术演进": full17.get("p4",{}),
        "p5_技术生态": full17.get("p5",{}),
        "p6_技术换乘": full17.get("p6",{}),
        "g1_技术全景": full17.get("g1",{}),
        "g2_技术路线": full17.get("g2",{}),
        "g3_技术集群": full17.get("g3",{}),
        "g4_技术风口": full17.get("g4",{}),
        "g5_专利技术": full17.get("g5",{}),
        "g6_可比技术": full17.get("g6",{}),
        "g7_技术向量": full17.get("g7",{}),
        "g8_技术代际": full17.get("g8",{}),
        "r1_变革时间档案": full17.get("r1",{}),
        "r2_技术路线图": full17.get("r2",{}),
        "r3_技术代际更迭": full17.get("r3",{}),
    }
    # 返回给用户（可配合 Visualizer 展示图谱或直接输出结构化数据）

conn.close()
```

**判断逻辑：**
- 本地库精确匹配到 → 直接返回完整图谱，用户看到即可
- 本地库模糊匹配到多个 → 列出让用户选择，确认后返回
- 本地库没找到 → 进入 **模式 2（查云端）**

### 模式 2：查云端 6622（本地库没有时）

```bash
# 搜索技术（云端可能更新了更多技术）
curl -s -X POST http://115.190.229.115:6622/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"tech_search","arguments":{"keyword":"用户说的技术名"}}}'

# 或直接查图谱
curl -s -X POST http://115.190.229.115:6622/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"tech_atlas","arguments":{"name":"用户说的技术名"}}}'
```

- 云端有 → 返回图谱，并提示"此技术不在本地库，已从云端获取"
- 云端也没有 → 进入 **模式 3（搜集信息生成）**

### 模式 3：搜集信息生成（本地库和云端都没有时）

当用户问的技术不在 462 项长名单中，也不在云端数据库时：

1. 用 WebSearch 搜索该技术的公开信息
2. 按 17 模块图谱的结构整理：定义、指标、成熟度、趋势、产业链、竞品、专利等
3. 直接以结构化文本返回给用户（不造图，不伪造数据）
4. 提示"此技术不在当前长名单中，建议加入候选技术列表"

### 模式 4：从云端重建长名单页面

```bash
# 默认用内置数据库重建（离线可用）
python rebuild_page.py 未来技术长名单-462项.html 未来技术长名单-新版.html

# 从云端下载最新版再重建
python rebuild_page.py 未来技术长名单-462项.html 未来技术长名单-云端版.html --cloud
```

### 模式 5：导出表格 / PPT

```bash
# 用内置库导出
python ~/.workbuddy/skills/future-tech-list-pipeline/scripts/export_xlsx.py tech-atlas.db -o 未来技术长名单-全量表.xlsx
python ~/.workbuddy/skills/future-tech-list-pipeline/scripts/export_pptx.py tech-atlas.db -o 技术图谱报告.pptx

# 或从云端下载最新版再导出
curl -o tech-atlas-latest.db http://115.190.229.115:6622/download/tech-atlas.db
python ~/.workbuddy/skills/future-tech-list-pipeline/scripts/export_pptx.py tech-atlas-latest.db -o 技术图谱报告.pptx
```

### 模式 6：每日情报拉取+入库

见 `references/extract-prompt.md` 完整契约。每日自动化已配置，早 9:00 自动执行。

---

## 核心硬规则

1. **查库优先**：用户问任何技术，**第一步永远是查本地数据库**（精确查询→模糊查询→用户确认）。找到就返回，找不到才去云端或搜索。
2. **内置数据库离线可用**：`tech-atlas.db`（18MB，462 项）已随 skill 内置，不需要联网。
3. **云端是最新数据源**：本地库查不到时查云端 6622；长名单页面重建时可选 `--cloud` 获取最新版。
4. **不存在的不伪造**：技术不在库中时，明确告知用户，并给出搜索到的真实信息，不编造 17 模块图谱。
5. **一篇一技术**：每日情报抽取时，一篇报道只抽全文主讲的一个技术。
6. **字段完整**：抽取结果 12 字段缺一不可，`relevance`（对长安的含义）必填。
7. **交付提示协议**：每次交付图谱后，告知"可导出 xlsx 表格 / PPT 报告 / 或重建完整长名单页面"。
8. **只读限制**：对 6600 只做读取（GET 列表/详情），不调用任何新增/修改/删除接口。
9. **参考文档**：改数据库/MCP/页面结构前，先读 `references/` 下对应文档；写代码前扫一遍 `pitfalls.md`。