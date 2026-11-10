# 云端数据库部署与更新指南

适用场景：长名单持续扩容，数据托管在云服务器，各用户/设备直读最新版本，不再分发本地数据库文件。

## 方案对比

| 方案 | 原理 | 优点 | 适用 |
|---|---|---|---|
| **A. 静态文件直链（推荐起步）** | 云服务器用 Nginx/对象存储（COS/腾讯云 OSS/阿里云 OSS/S3）托管 `tech-atlas.db`，客户端 `sync_remote.py` 拉取到本地缓存后用 | 零依赖、最简单、支持 ETag 缓存、离线可用 | 单机/小团队，日更级别 |
| **B. 云端 REST API** | 云服务器把数据导入 MySQL/PostgreSQL，提供 `GET /api/techs` 等接口 | 实时、可加权限/增量 | 多端高频实时查询 |
| **C. MCP 直连云端** | MCP server.py 配置 `TECH_ATLAS_REMOTE_URL`，启动/定时自动下载云端 db 到本地缓存再查询 | 对调用方完全透明，保持 stdio MCP 形态 | 推荐配合方案 A |

> 注意：SQLite 是单文件数据库，**不支持**多客户端同时直连远程写。所有远程方案本质都是「云端文件 → 本地只读缓存」，查询走本地缓存（毫秒级、离线可用）。

## 方案 A 部署步骤（Nginx 示例）

1. 服务器上放置文件（假设 `/data/www/tech-atlas.db`），Nginx：
   ```nginx
   location /tech-atlas.db {
       alias /data/www/tech-atlas.db;
       types { } default_type application/octet-stream;
       add_header Cache-Control "no-cache";
   }
   ```
   或直接传对象存储，拿到下载直链。
2. 本地首次使用：
   ```bash
   python scripts/sync_remote.py https://your-server/tech-atlas.db --force
   ```
3. 后续更新：云端替换文件后，再执行同一条命令即可（脚本自动校验+备份+安装）。

需要鉴权时设置环境变量 `ATLAS_AUTH_HEADER="Authorization: Bearer <token>"`。

## 更新发布流程（您更新长名单后）

```
本地改数据 → verify_all.py 全绿 → push_remote.py <URL>（或手动上传）→ 各端 sync_remote.py 拉新
```

- `push_remote.py` 会先跑完整性校验（技术数/表结构），通过才允许上传，防止把坏库发布出去。
- 建议云端文件带版本后缀（`tech-atlas-2026-08-26.db`）并维护一个 `latest` 指向，便于回滚。

## 页面与云端的关系

单文件 HTML 是「某时刻的快照」（内联数据）。云端更新后如需页面同步，用：
```bash
python scripts/sync_remote.py <URL> --html 未来技术长名单-462项.html
```
脚本会用新库重建页面内联的 `L462`/`AFULL` 数据块（原页面自动备份）。旗舰手写数据（TECH.qc 等）在页面内不受影响。

## 云端发布记录建议

在云端同目录放 `tech-atlas.version.json`：
```json
{"version": "2026-08-26", "total": 462, "sha256": "...", "notes": "新增 XX 技术"}
```
`sync_remote.py` 未来可直接比对版本号决定是否拉取（当前按技术数 + --force 控制）。
