import React, { useEffect, useState } from 'react'
import Mascot from './Mascot'
import { t } from '../i18n'

interface AboutDialogProps {
  open: boolean
  onClose: () => void
}

const AboutDialog: React.FC<AboutDialogProps> = ({ open, onClose }) => {
  const [version, setVersion] = useState('')

  useEffect(() => {
    if (!open) return
    const fromApi = window.electronAPI?.getAppVersion?.()
    if (fromApi) {
      Promise.resolve(fromApi).then((v) => setVersion(String(v || ''))).catch(() => setVersion(''))
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-black/40"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="关于 maliang"
    >
      <div
        className="mx-4 w-full max-w-sm rounded-2xl px-8 py-8 text-center shadow-xl"
        style={{ backgroundColor: '#FDF9F2' }}
        onClick={(e) => e.stopPropagation()}
      >
        <Mascot className="h-44 w-auto mb-4" />
        <h1 className="text-xl font-bold text-slate-800">maliang</h1>
        <p className="mt-1 text-sm text-slate-500">长安前瞻院桌面智能体助手</p>
        {version ? <p className="mt-2 text-xs font-mono text-slate-400">v{version}</p> : null}
        <p className="mt-4 text-xs leading-relaxed text-slate-500">
          本软件基于一项 MIT 开源项目派生。版权与署名见仓库中的 LICENSE 与 NOTICE。
        </p>
        <button
          type="button"
          onClick={onClose}
          className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 cursor-pointer"
        >
          {t('ws_close')}
        </button>
      </div>
    </div>
  )
}

export default AboutDialog
