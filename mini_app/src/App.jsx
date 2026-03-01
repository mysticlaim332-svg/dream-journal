import { useState, useEffect } from 'react'
import { initTelegram, getTelegramUser, getInitData } from './lib/telegram'
import CalendarPage from './pages/CalendarPage'
import InsightsPage from './pages/InsightsPage'
import PatternsPage from './pages/PatternsPage'

const TABS = [
  { id: 'calendar', emoji: '📅', label: 'Календар' },
  { id: 'patterns', emoji: '🔮', label: 'Патерни' },
  { id: 'insights', emoji: '✨', label: 'Інсайти' },
]

// Init Telegram WebApp immediately (before any component mounts)
initTelegram()

export default function App() {
  const [activeTab, setActiveTab] = useState('calendar')
  const user = getTelegramUser()
  const initData = getInitData()

  // DEBUG — remove after fix
  const webApp = window.Telegram?.WebApp
  const unsafeUser = webApp?.initDataUnsafe?.user
  const urlParams = window.location.search
  const debugInfo = [
    `v${webApp?.version ?? '?'} | ${webApp?.platform ?? '?'}`,
    `initData: ${initData ? initData.slice(0,30)+'...' : 'EMPTY'}`,
    `user: ${unsafeUser ? unsafeUser.id : 'EMPTY'}`,
    `url: ${urlParams || 'no params'}`,
  ].join(' | ')

  return (
    <div className="flex flex-col h-full bg-dream-bg safe-top">
      {/* DEBUG PANEL — remove after fix */}
      <div style={{background:'#1a1a2e',color:'#aaa',fontSize:'10px',padding:'4px 8px',wordBreak:'break-all'}}>
        {debugInfo}
      </div>

      {/* User greeting */}
      {user && (
        <div className="px-4 pt-4 pb-2 flex items-center gap-2">
          <span className="text-xl">🌙</span>
          <div>
            <p className="text-dream-text font-medium text-sm">
              {user.first_name ?? 'Журнал'}
            </p>
            <p className="text-dream-muted text-xs">Журнал снів та ідей</p>
          </div>
        </div>
      )}

      {/* Page content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'calendar' && <div className="h-full overflow-y-auto"><CalendarPage /></div>}
        {activeTab === 'patterns' && <div className="h-full overflow-y-auto"><PatternsPage /></div>}
        {activeTab === 'insights' && <div className="h-full overflow-y-auto"><InsightsPage /></div>}
      </div>

      {/* Bottom navigation */}
      <nav className="flex border-t border-dream-border bg-dream-surface safe-bottom">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex-1 flex flex-col items-center gap-1 py-3 transition-colors
              ${activeTab === tab.id
                ? 'text-dream-purple'
                : 'text-dream-muted hover:text-dream-text'}
            `}
          >
            <span className="text-xl">{tab.emoji}</span>
            <span className="text-xs font-medium">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
