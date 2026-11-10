import { app, Menu, BrowserWindow, shell } from 'electron'
import type { MenuItemConstructorOptions } from 'electron'
import { loadAppConfig } from './themes'
import { labels } from './i18n-labels'

const isMac = process.platform === 'darwin'
const SKILL_HUB_URL = 'https://EXAMPLE-DISABLED-NO-SKILL-HUB/'
const DEFAULT_DOCS_URL = 'https://docs.maliang.local'

// Send a menu-triggered action to the renderer (e.g. new chat, open settings).
function emit(win: BrowserWindow | null, action: string) {
  win?.webContents.send('menu-action', action)
}

let currentGetWindow: (() => BrowserWindow | null) | null = null

/**
 * Build a minimal, purpose-built application menu. Labels follow the current
 * UI language (Simplified Chinese by default).
 */
export function buildAppMenu(getWindow: () => BrowserWindow | null) {
  currentGetWindow = getWindow
  const win = () => getWindow()
  const l = labels()

  const appMenu: MenuItemConstructorOptions[] = isMac
    ? [
        {
          label: app.name,
          submenu: [
            { label: l.about, click: () => emit(win(), 'open-about') },
            { type: 'separator' },
            { label: l.settings, accelerator: 'Cmd+,', click: () => emit(win(), 'open-settings') },
            { type: 'separator' },
            { role: 'hide', label: l.hide },
            { role: 'hideOthers', label: l.hideOthers },
            { role: 'unhide', label: l.unhide },
            { type: 'separator' },
            { role: 'quit', label: l.quit },
          ],
        },
      ]
    : []

  const fileMenu: MenuItemConstructorOptions = {
    label: l.file,
    submenu: [
      { label: l.newChat, accelerator: 'CmdOrCtrl+N', click: () => emit(win(), 'new-chat') },
      ...(!isMac
        ? ([
            { label: l.settingsShort, accelerator: 'Ctrl+,', click: () => emit(win(), 'open-settings') },
            { type: 'separator' },
            { role: 'quit', label: l.quit },
          ] as MenuItemConstructorOptions[])
        : []),
    ],
  }

  const editMenu: MenuItemConstructorOptions = {
    label: l.edit,
    submenu: [
      { role: 'undo', label: l.undo },
      { role: 'redo', label: l.redo },
      { type: 'separator' },
      { role: 'cut', label: l.cut },
      { role: 'copy', label: l.copy },
      { role: 'paste', label: l.paste },
      { role: 'selectAll', label: l.selectAll },
    ],
  }

  const viewMenu: MenuItemConstructorOptions = {
    label: l.view,
    submenu: [
      { role: 'reload', label: l.reload },
      { role: 'toggleDevTools', label: l.toggleDevTools },
      { type: 'separator' },
      { role: 'resetZoom', label: l.resetZoom },
      { role: 'zoomIn', label: l.zoomIn },
      { role: 'zoomOut', label: l.zoomOut },
      { type: 'separator' },
      { role: 'togglefullscreen', label: l.toggleFullscreen },
    ],
  }

  const windowMenu: MenuItemConstructorOptions = {
    label: l.window,
    submenu: [
      { role: 'minimize', label: l.minimize },
      ...(isMac ? ([{ role: 'zoom' as const, label: l.zoom }] as MenuItemConstructorOptions[]) : []),
      { type: 'separator' },
      // Explicit Close so Cmd/Ctrl+W reliably triggers our close-to-tray hide.
      { label: l.closeWindow, accelerator: 'CmdOrCtrl+W', click: () => win()?.close() },
    ],
  }

  const appConfig = loadAppConfig()
  const configuredDocs = typeof appConfig?.docsUrl === 'string' ? appConfig.docsUrl.trim() : ''
  const docsUrl = configuredDocs && !configuredDocs.includes('maliang.local') && !configuredDocs.includes('EXAMPLE-DISABLED')
    ? configuredDocs
    : ''
  const skillHubUrl = (appConfig?.skillHubUrl || SKILL_HUB_URL || '').trim()
  const skillHubEnabled = Boolean(
    appConfig?.skillHub && skillHubUrl && skillHubUrl.startsWith('http') && !skillHubUrl.includes('EXAMPLE-DISABLED'),
  )
  const linkItems: MenuItemConstructorOptions[] = [
    ...(docsUrl ? [{ label: l.documentation, click: () => shell.openExternal(docsUrl) }] : []),
    ...(skillHubEnabled ? [{ label: l.skillHub, click: () => shell.openExternal(skillHubUrl) }] : []),
  ]
  const helpMenu: MenuItemConstructorOptions = {
    label: l.help,
    submenu: [
      { label: l.about, click: () => emit(win(), 'open-about') },
      { label: l.viewLogs, click: () => emit(win(), 'view-logs') },
      ...(linkItems.length ? [{ type: 'separator' } as MenuItemConstructorOptions, ...linkItems] : []),
    ],
  }

  const template: MenuItemConstructorOptions[] = [
    ...appMenu,
    fileMenu,
    editMenu,
    viewMenu,
    windowMenu,
    helpMenu,
  ]

  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
}

export function rebuildAppMenu() {
  if (currentGetWindow) buildAppMenu(currentGetWindow)
}
