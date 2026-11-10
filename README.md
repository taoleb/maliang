# maliang

**maliang** 是长安前瞻院的桌面智能体助手：在本机规划任务、调用工具与技能，并提供 Web 控制台和 Windows 桌面客户端。

本仓库由一项 MIT 开源项目派生而来，已去掉上游产品品牌。原始版权声明保留在 `LICENSE`，派生说明见 `NOTICE`。

<p align="center">
  <img src="channel/web/static/mascot.gif" alt="maliang 吉祥物" width="240" />
</p>

发布方：**长安前瞻院**。产品名保持拉丁拼写 **maliang**。

## 能做什么

- 在 Web 控制台或桌面窗口中对话，查看思考过程与工具调用
- 接入微信、飞书、钉钉、企业微信、Telegram 等通道
- 使用技能、知识库、长期记忆和多 Agent 协作
- 对接主流模型服务商（也可配置自定义兼容接口）

## 从源码运行（Web 控制台）

需要 Python 3.10+（推荐 3.11）。

```bash
git clone <本仓库地址>
cd maliang
pip install -r requirements.txt
pip install -e .
python app.py
```

默认在本机 [http://127.0.0.1:9899](http://127.0.0.1:9899) 打开控制台。命令行入口是 `maliang`：

```bash
maliang start | stop | restart
maliang status | logs
maliang skill install <name>
maliang install-browser
```

- 配置与运行数据目录：`~/.maliang`（桌面端打包版）
- Agent 工作空间（记忆、技能等）：默认 `~/maliang`
- 环境变量前缀：`MALIANG_`（例如 `MALIANG_DATA_DIR`、`MALIANG_LANG`）

也可使用 Docker：`docker build -f docker/Dockerfile.latest -t maliang:latest .`，或根目录的轻量 `Dockerfile`。

## Windows 桌面客户端

桌面端位于 `desktop/`，技术栈为 **Electron + React + TypeScript**，后端由 **PyInstaller** 打成 `maliang-backend` 一并打包。安装向导欢迎页使用吉祥物静帧，应用启动闪屏、空会话和「关于」对话框使用循环 GIF。窗口与托盘图标仍是静态 `.ico`。

交叉编译完整 Windows 安装包在 Linux 上不可靠。请在 Windows 机器上按 [BUILD-WINDOWS.md](BUILD-WINDOWS.md) 构建，或使用 GitHub Actions 工作流 `.github/workflows/build-windows.yml`。

开发时：

```bash
cd desktop
npm install
npm run dev
```

## 图标与吉祥物

品牌资源在 `branding/`。静态图标用于系统图标；`mascot.gif` 只用于界面装饰，不会替换整个工作台布局。

## 上游服务（默认关闭）

目前没有 maliang 自己的更新服务器或技能市场。因此：

- 桌面自动更新默认关闭；以后可设置 `updateFeedUrl` 或 `MALIANG_UPDATE_FEED`
- 源码 `maliang update` 默认不访问上游 GitHub；可设置 `MALIANG_UPDATE_REPO`
- 技能广场入口默认隐藏；可在配置中填写 `skill_hub_url`
- 不再从 `cdn.link-ai.tech` 下载安装脚本或飞书 SDK 预置包（飞书通道仍可通过环境变量 `MALIANG_FEISHU_VENDOR_URL` 指定自有地址）

LinkAI 等第三方模型/语音接口作为可选供应商保留，仅在你自行配置 API 时访问 `api.link-ai.tech`。

## 许可

MIT。请同时保留 `LICENSE` 中的原始版权声明和本仓库的 `NOTICE`。
