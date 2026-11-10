# MCP 服务协议（tech-atlas stdio server）

`data/mcp/server.py`——纯标准库实现的 stdio JSON-RPC MCP 服务（零第三方依赖），协议版本 2025-06-18。DB 路径 = server.py 同目录的 `tech-atlas.db`。

## 注册配置（~/.workbuddy/mcp.json）

```json
{
  "mcpServers": {
    "tech-atlas": {
      "command": "<python 绝对路径>",
      "args": ["<server.py 绝对路径>"],
      "env": {"PYTHONIOENCODING": "utf-8"},
      "description": "未来技术长名单(462项)×新兴技术图谱数据库",
      "disabled": false
    }
  }
}
```

注册后提示用户：在连接器管理页右上角自定义连接器入口点击「信任」启用。

## 远程模式（云端数据库直读）

配置环境变量 `TECH_ATLAS_REMOTE_URL`（云端 tech-atlas.db 下载地址）后，server.py 启动时自动下载云端最新库到本地缓存（`%TEMP%/tech-atlas-remote.db`）再查询；云端不可达时依次回退：上次缓存 → 同目录本地库，全程不中断服务。`tech_stats` 返回的 `data_source` 字段标明当前数据来源（`remote:<url>` 或 `local`）。

```json
{
  "mcpServers": {
    "tech-atlas": {
      "command": "<python 绝对路径>",
      "args": ["<server.py 绝对路径>"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "TECH_ATLAS_REMOTE_URL": "https://your-server/tech-atlas.db"
      }
    }
  }
}
```

云端需鉴权时再加 `"ATLAS_AUTH_HEADER": "Authorization: Bearer <token>"`。

## 五个工具

### 1. tech_list — 长名单查询
参数：`flow`（五流）/ `dimension` / `direction` / `stage`（均可选筛选）、`sort`（maturity|heat|stage|name，默认 maturity）、`limit`（默认50最大462）、`offset`。
返回：`{total, offset, limit, sort, items:[{id,name,flow,dimension,direction,stage,maturity,heat,window,data_source,definition(截200字),ref_flagship?}]}`

### 2. tech_atlas — 单项图谱（核心）
参数：`name`（必填）。**四级解析优先级**（顺序不可乱）：
1. technologies 精确名 → 返回 `{status:ok, match:exact, atlas}`，若 ref_flagship 非空附加 `flagship_atlas`+`flagship_name`
2. aliases 别名 → 同上（match:alias:xxx）
3. **flagship_atlases 精确名**（太比特量子通信/量子通信为独立旗舰，不在 462 清单内）→ `{status:ok, match:flagship, flagship_name, flagship_atlas}`
4. 模糊合并：旗舰表 LIKE + technologies LIKE；单一旗舰命中→match:flagship_fuzzy；单一无旗舰命中→match:fuzzy；多候选→`{status:ambiguous, candidates}`；零命中→报错提示用 tech_search

⚠️ 教训：第 3 级必须优先于 technologies 的模糊匹配，否则"量子通信"会被"量子通信车载化"抢占。

返回的 `atlas.full17` 即完整 17 模块数据（457 项）；旗舰关联项以 `flagship_atlas` 为准。

### 3. tech_search — 关键词搜索
参数：`keyword`（必填）、`limit`（默认20最大100）。匹配 name/definition/trend/direction/alias，名称命中优先。返回 `{keyword, count, items:[...]}`

### 4. taxonomy_tree — 分类体系
参数：`group_by`（flow|dimension|stage，默认 flow）。flow→五流→维度→方向树（含计数）；stage→`{阶段名:数量}`。

### 5. tech_stats — 统计
无参数。返回 meta.info + `flagship_atlases`（6 个名称）+ `db_path`。

## 端到端调用测试模板

```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"tech_atlas","arguments":{"name":"世界模型"}}}' \
 | python server.py
```

回归必测项：①普通项（世界模型→atlas.full17 17 模块）②旗舰关联项（量子密钥分发→flagship_atlas 17 模块）③独立旗舰（太比特量子通信/量子通信→match:flagship）④tech_list flow 筛选 ⑤tech_search ⑥taxonomy_tree stage ⑦tech_stats。

## 服务器实现要点

- `sys.stdin/stdout.reconfigure(encoding="utf-8")`（防 Windows GBK 破坏中文 JSON）
- 每请求新建连接、用完即关（避免嵌套游标问题）
- 工具异常返回 `{content:[{type:text,text:"调用失败: ..."}], isError:true}`，不抛栈
