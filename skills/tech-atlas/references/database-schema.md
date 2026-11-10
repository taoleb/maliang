# SQLite 数据库 Schema（tech-atlas.db · schema v2）

成品库：462 行 technologies + 6 套旗舰图谱 + 60 别名 + 111 方向分类 + 55 包含关系。`PRAGMA integrity_check` 必须为 ok。

## 表清单

| 表 | 行数 | 用途 |
|---|---|---|
| technologies | 462 | 长名单主表，含 atlas_json 图谱 |
| flagship_atlases | 6 | 手写旗舰 17 模块（full_json） |
| aliases | 60 | 同技异名归并 |
| taxonomy | 111 | 维度×方向分类统计 |
| inclusion_relations | 55 | 技术包含关系 |
| meta | 1 | info JSON（统计+描述） |

## technologies 表

```sql
CREATE TABLE technologies(
  id INTEGER PRIMARY KEY, seq INTEGER, name TEXT UNIQUE NOT NULL,
  flow TEXT,            -- 两流三底座：信息流/能源流/数据底座/安全底座/硬件底座
  dimension TEXT,       -- 14 个技术维度
  direction TEXT,       -- 111 个技术方向
  stage_index INTEGER,  -- 0-4
  stage TEXT,           -- 理论概念/实验室验证/原型机/商业化前夜/规模应用
  maturity INTEGER,     -- 成熟度百分比 0-100
  heat INTEGER,         -- 热度 0-100
  window TEXT,          -- 应用窗口
  definition TEXT,      -- 一句话定义
  trend TEXT,           -- 趋势
  card_id INTEGER,      -- tech-cards 卡片 id（可为 NULL）
  data_source TEXT,     -- 数据来源标注
  ref_flagship TEXT,    -- 关联旗舰名（可为 NULL，如"量子通信"）
  atlas_json TEXT NOT NULL);
CREATE INDEX idx_tech_flow ON technologies(flow);
CREATE INDEX idx_tech_dim ON technologies(dimension);
CREATE INDEX idx_tech_stage ON technologies(stage_index);
```

### atlas_json 结构（非旗舰 457 行）

```json
{
  "meta": {"name","stage","stage_index","source","data_date"},
  "p1_principle": {"definition","levels":{科普级/专业级/论文级},"key_points":[]},
  "p2_stage": {...}, "p3_applications": {...}, "p4_foresight": {...},
  "p5_disruption": {...}, "p6_industrialization": {...},
  "g_position": {...}, "g_dependency": {...}, "g_maturity_forecast": {...},
  "full17": { "nm","en","c","p1","p2","p3","p4","p5","p6",
              "g1","g2","g3","g4","g5","g6","g7","g8","r1","r2","r3" }
}
```

顶层扁平字段（p1_principle 等）为兼容旧接口保留；**完整 17 模块在 `full17` 键内**，与页面 renderAtlas 引擎字段一一对应（详见 field-contract.md）。

### 旗舰关联行（5 行）

ref_flagship 非空的行：量子密钥分发→量子通信、超导量子计算机→量子计算、固态电池→固态电池、人形机器人→人形机器人、脑机接口→脑机接口。其 atlas_json 为旧 10 键结构，**真实渲染数据取自 flagship_atlases 表**。

## flagship_atlases 表

```sql
CREATE TABLE flagship_atlases(name TEXT PRIMARY KEY, full_json TEXT NOT NULL);
```

6 行：量子通信 / 太比特量子通信 / 量子计算 / 脑机接口 / 固态电池 / 人形机器人。full_json 为手写深度 17 模块（nm/en/c + p1~p6 + g1~g8 + r1~r3），注意其中 p3.radar 是六维数组（普通项是行业 dict），属设计差异非缺失。

## aliases 表

```sql
CREATE TABLE aliases(std_name TEXT NOT NULL, alias TEXT NOT NULL,
  flow TEXT, direction TEXT, dimension TEXT);
CREATE INDEX idx_alias_std ON aliases(std_name);
```

来源：Excel「同技异名归并对照」sheet。用于 tech_atlas 第二级解析。

## taxonomy / inclusion_relations / meta

```sql
CREATE TABLE taxonomy(dimension TEXT, direction TEXT, flow TEXT, tech_count INTEGER,
  PRIMARY KEY(dimension, direction));
CREATE TABLE inclusion_relations(handle TEXT, big_item TEXT, flow TEXT,
  dimension TEXT, direction TEXT, children TEXT, reason TEXT);
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);  -- key='info'
```

meta.info 含 name/source/build_date/schema_version=2/description/stats（total/card_matched/flagship_linked/dimensions/directions/flagship_atlases/flows/stages）。

## 关键设计决策

1. **无 FTS 表**：中文双字词用 `LIKE '%kw%'` 检索，462 行规模毫秒级。（FTS5 unicode61 不切中文、trigram 需 ≥3 字符，均不适用）
2. **图谱整存 JSON**：atlas_json 存完整 JSON 而非拆表——查询只需一行，渲染端直接消费，避免多表 JOIN。
3. **双副本**：工作区根 `tech-atlas.db` 与 `tech-atlas-mcp/tech-atlas.db`（MCP 服务读后者），修改后 `cp -f` + md5sum 校验一致。
4. **重跑安全**：build_db.py 用 `DROP TABLE IF EXISTS` 重建（沙箱拦截 os.remove）。
