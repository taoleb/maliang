# EXTRACT_PROMPT.md — 每日重点技术抽取规则（自动化任务执行契约）

本文件定义「技术日报 → 重点技术结构化抽取」的规则。智能体每日自动化运行时按此执行。

## 流水线目录（`_cloud/cloud-mcp/`）

```
config.json           凭据配置（勿外传）
state.json            拉取状态（已处理 id、运行记录）——脚本自维护
inbox/new/            待抽取记录（每条一个 JSON，来自 6600 /api/tech-info/list）
inbox/done/           抽取完成归档
extracted/ready/      抽取结果（待上传）
extracted/done/       上传成功归档
pipeline.log          运行日志
```

## 每日执行步骤

1. **拉取**：运行
   `python daily_pipeline.py pull`
   - 有新记录 → `inbox/new/` 出现 `时间戳-记录id.json`，继续第 2 步
   - 输出 `"new": 0` → 当天无新数据，本次任务结束（回复"今日无新增技术情报"即可）
2. **逐条抽取**：对 `inbox/new/` 每个 JSON：
   - 读取 6600 记录字段：`id, title, content, domain, source, source_url, keywords, tags, priority, status, tracking_status, ai_opinion, value_to_foresight, created_at/imported_at` 等
   - 按下文【抽取规则】产出结构化结果
3. **写入抽取结果**：每条记录一个 JSON，写入 `extracted/ready/`，文件名与源文件一致；
   一条源记录可抽出多项技术时，用 `{"items":[...]}` 包裹。然后把源文件移入 `inbox/done/`。
4. **上传**：运行 `python daily_pipeline.py push`
   - 成功后 `extracted/ready/*.json` 自动归档到 `extracted/done/`
5. **汇报**：简要报告本次新增条数、抽出的重点技术（high 价值优先列出）、上传结果。

## 抽取规则

### 判定"重点技术"（必须满足其一）
- 涉及具体技术方向（芯片、AI、智驾、电池、传感器、材料、量子、机器人等）且有实质进展：
  发布会/量产/融资/专利突破/政策落地/头部企业动作
- 源记录 `priority` 为高，或 `value_to_foresight` / `ai_opinion` 判断为高价值
- 与长安汽车业务域（整车、智驾、三电、芯片、座舱、制造）明确相关

纯行业新闻、人事变动、无技术实质的市场消息 → 不抽取（跳过该记录）。

### 输出字段（每条抽取结果）

| 字段 | 说明 | 要求 |
|---|---|---|
| `intel_id` | 去重键 | 固定格式 `6600-<源记录id>` |
| `date` | 入库日期 | 源记录日期（无则当天），YYYY-MM-DD |
| `tech_name` | 技术名称 | 尽量对齐长名单标准名（如"固态电池""激光雷达""量子密钥分发"）；新名词直接用原文 |
| `title` | 源信息标题 | 原文标题 |
| `domain` | 领域 | 源记录 domain；缺失时自拟（芯片/智驾/新能源/AI/通信/材料/其他） |
| `summary` | 要点 | 2-3 句，含关键数字（性能/时间/金额），不复述标题 |
| `trend` | 趋势研判 | 一句话，说明该事件反映的技术趋势 |
| `value_level` | 价值等级 | `high`=改变产业化节奏或直接竞争威胁；`medium`=值得跟踪；`low`=一般关注 |
| `relevance` | 对长安的含义 | **必填**，一句话落到长安汽车：布局建议/对标对象/风险预警；确实无关写"暂无直接影响" |
| `source_url` | 来源链接 | 源记录 source_url |
| `source_system` | 来源系统 | 固定 `tech-daily-6600` |
| `raw` | 原始记录 | 完整源 JSON（原样保留） |

### 单条示例（写入 `extracted/ready/20260826-091500-1001.json`）

```json
{
  "intel_id": "6600-1001",
  "date": "2026-08-26",
  "tech_name": "固态电池",
  "title": "丰田宣布硫化物固态电池量产时间表",
  "domain": "新能源",
  "summary": "丰田确认2027-2028年量产硫化物全固态电池，能量密度1000Wh/L，充电10分钟。",
  "trend": "硫化物路线产业化窗口前移，头部车企进入工程化竞速。",
  "value_level": "high",
  "relevance": "长安固态路线需对标硫化物电解质进度，建议复核自研与合作方技术路线时间锚点。",
  "source_url": "https://...",
  "source_system": "tech-daily-6600",
  "raw": { "...": "源记录原样" }
}
```

## 质量红线
- 不编造源记录中没有的数字与事实；`summary`/`trend` 必须可从原文推出。
- `tech_name` 不确定归属时用原文名词，不强行归类。
- 上传前如 `push` 报 401，提示用户检查 `config.json` 的 `cloud_api_key`。

## 凭据配置（首次运行前）
复制 `config.example.json` 为 `config.json`，填入：
- `source_username` / `source_password`：6600 技术日报监测系统登录账号
- `cloud_api_key`：与云端 server.py 的 `ATLAS_API_KEY` 环境变量一致
