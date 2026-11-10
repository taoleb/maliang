// Native shell UI strings (app menu, tray, system dialogs).
// Default is Simplified Chinese; the renderer notifies us if the user switches.

export type UiLang = 'zh' | 'en'

let currentLang: UiLang = 'zh'

export function getUiLang(): UiLang {
  return currentLang
}

export function setUiLang(lang: string): UiLang {
  currentLang = lang === 'en' ? 'en' : 'zh'
  return currentLang
}

export function isZhUi(): boolean {
  return currentLang !== 'en'
}

const ZH = {
  about: '关于 maliang',
  settings: '设置…',
  settingsShort: '设置',
  file: '文件',
  newChat: '新对话',
  edit: '编辑',
  undo: '撤销',
  redo: '重做',
  cut: '剪切',
  copy: '复制',
  paste: '粘贴',
  selectAll: '全选',
  view: '查看',
  reload: '重新加载',
  toggleDevTools: '开发者工具',
  resetZoom: '实际大小',
  zoomIn: '放大',
  zoomOut: '缩小',
  toggleFullscreen: '进入全屏',
  window: '窗口',
  minimize: '最小化',
  zoom: '缩放',
  closeWindow: '关闭窗口',
  help: '帮助',
  viewLogs: '查看日志',
  documentation: '文档',
  skillHub: '技能广场',
  hide: '隐藏 maliang',
  hideOthers: '隐藏其他',
  unhide: '全部显示',
  quit: '退出 maliang',
  showApp: (name: string) => `显示 ${name}`,
  saveImageAs: '图片另存为…',
  copyImage: '复制图片',
  saveFailed: '保存失败',
  saveFailedDetail: '无法保存该图片。',
  allFiles: '所有文件',
}

const EN = {
  about: 'About maliang',
  settings: 'Settings…',
  settingsShort: 'Settings',
  file: 'File',
  newChat: 'New Chat',
  edit: 'Edit',
  undo: 'Undo',
  redo: 'Redo',
  cut: 'Cut',
  copy: 'Copy',
  paste: 'Paste',
  selectAll: 'Select All',
  view: 'View',
  reload: 'Reload',
  toggleDevTools: 'Toggle Developer Tools',
  resetZoom: 'Actual Size',
  zoomIn: 'Zoom In',
  zoomOut: 'Zoom Out',
  toggleFullscreen: 'Toggle Full Screen',
  window: 'Window',
  minimize: 'Minimize',
  zoom: 'Zoom',
  closeWindow: 'Close Window',
  help: 'Help',
  viewLogs: 'View Logs',
  documentation: 'Documentation',
  skillHub: 'Skill Hub',
  hide: 'Hide maliang',
  hideOthers: 'Hide Others',
  unhide: 'Show All',
  quit: 'Quit maliang',
  showApp: (name: string) => `Show ${name}`,
  saveImageAs: 'Save Image As…',
  copyImage: 'Copy Image',
  saveFailed: 'Save failed',
  saveFailedDetail: 'Could not save the image.',
  allFiles: 'All Files',
}

export function labels() {
  return currentLang === 'en' ? EN : ZH
}
