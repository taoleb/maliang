# 在 Windows 上打包 maliang 桌面安装包

桌面端是 **Electron + React + TypeScript**，通过 electron-builder 打出 NSIS 安装包；
Python 后端用 **PyInstaller onedir** 打成 `maliang-backend`，再作为 extraResources 打进安装包。

PyInstaller 需要在 Windows 上生成本地二进制（含大量原生扩展），**不能**在 Linux 上可靠地交叉编译出完整的 Windows 安装包。请在 64 位 Windows 上构建，或使用仓库里的 GitHub Actions 工作流 `.github/workflows/build-windows.yml`。

## 本机构建步骤（Windows x64）

前置：Windows 10/11 x64，Git，Python 3.11（推荐）或 3.12，Node.js 18+，以及 Visual C++ 构建工具（PyInstaller 依赖可能需要）。

在仓库根目录打开 PowerShell：

```powershell
# 1. 后端
py -3.11 -m venv desktop\build\.venv-build
desktop\build\.venv-build\Scripts\pip install -U pip
desktop\build\.venv-build\Scripts\pip install -r desktop\build\requirements-desktop.txt
desktop\build\.venv-build\Scripts\pip install pyinstaller
desktop\build\.venv-build\Scripts\pyinstaller desktop\build\maliang-backend.spec --noconfirm --distpath desktop\build\dist --workpath desktop\build\build-work

# 2. 可选：为文件搜索工具附带 ripgrep
# 将 rg.exe 放到 desktop\resources\bin\rg.exe

# 3. 前端与安装包
cd desktop
npm ci
npm run dist:win
```

产物在 `desktop/release/`，文件名类似：

`maliang-Setup-<version>-x64.exe`

安装向导欢迎页/完成页使用 `desktop/build/installerSidebar.bmp`（吉祥物静帧）。窗口、托盘和安装包文件图标仍是静态 `desktop/resources/icon.ico`。未配置代码签名时，安装包是未签名的；如需签名，可设置 `SIGNTOOL_PATH` 等环境变量后使用 `electron-builder.win.js`（参见该文件说明）。

## 自定义更新源

默认不会向任何上游地址检查更新。若以后有自己的更新服务器，在桌面 flavor 的 `app-config.json` 里设置 `updateFeedUrl`，或设置环境变量 `MALIANG_UPDATE_FEED`。
