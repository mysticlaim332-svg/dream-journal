import { useState, useEffect } from 'react'
import { initTelegram, getTelegramUser } from './lib/telegram'
import CalendarPage from './pages/CalendarPage'
import InsightsPage from './pages/InsightsPage'
import PatternsPage from './pages/PatternsPage'

const TABS = [
  { id: 'calendar', emoji: '📅', label: 'Календар' },
  { id: 'patterns', emoji: '🔮', label: 'Патерни' },
  { id: 'insights', emoji: '✨', label: 'Інсайти' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('calendar')
  const user = getTelegramUser()

  useEffect(() => {
    initTelegram()
  }, [])

  return (
    <div className="flex flex-col h-full bg-dream-bg safe-top">
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
