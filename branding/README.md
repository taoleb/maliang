# maliang 品牌资源

- `maliang-source.ico` / `maliang.ico`：用户提供的静态图标（窗口、托盘、安装包文件图标）。
- `maliang-16.png` … `maliang-1024.png`：由该 ico 生成的各尺寸 PNG。
- `maliang-mascot.gif`：循环吉祥物动画（309×414，12 帧）。用于启动闪屏、空会话欢迎区和关于对话框；不能作为 Windows `.ico` 或托盘图标。
- `maliang-mascot-still.png`：吉祥物静帧，供安装向导侧栏等无法播放 GIF 的场合使用。

对应产物：

- `desktop/resources/icon.ico` / `icon.png` / `icon.icns`
- `channel/web/static/favicon.ico`、`logo.jpg`、`mascot.gif`
- `desktop/resources/installerSidebar.bmp`、`desktop/resources/installerWelcome.bmp`（NSIS 欢迎/完成页，奶油色底）
