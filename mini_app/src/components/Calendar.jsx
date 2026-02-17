import { useMemo } from 'react'
import { haptic } from '../lib/telegram'

const DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд']

const TYPE_COLOR = {
  dream:   'bg-dream-purple',
  idea:    'bg-dream-teal',
  thought: 'bg-dream-gold',
}

export default function Calendar({ year, month, byDate, selectedDate, onSelectDate }) {
  // month is 1-indexed
  const days = useMemo(() => {
    const result = []
    const firstDay = new Date(year, month - 1, 1)
    // Monday = 0 offset
    let startOffset = (firstDay.getDay() + 6) % 7
    const daysInMonth = new Date(year, month, 0).getDate()

    // Fill leading empty cells
    for (let i = 0; i < startOffset; i++) result.push(null)

    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      result.push({ day: d, dateStr, entries: byDate[dateStr] || [] })
    }
    return result
  }, [year, month, byDate])

  const today = new Date().toISOString().slice(0, 10)

  function handleSelect(cell) {
    if (!cell || cell.entries.length === 0) return
    haptic.light()
    onSelectDate(cell.dateStr)
  }

  return (
    <div className="animate-fade-in">
      {/* Day headers */}
      <div className="grid grid-cols-7 mb-2">
        {DAYS.map(d => (
          <div key={d} className="text-center text-xs font-medium text-dream-muted py-1">
            {d}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((cell, i) => {
          if (!cell) return <div key={`empty-${i}`} />

          const isToday = cell.dateStr === today
          const isSelected = cell.dateStr === selectedDate
          const hasEntries = cell.entries.length > 0

          // Determine dot colors (up to 3 unique types)
          const types = [...new Set(cell.entries.map(e => e.type))].slice(0, 3)

          return (
            <button
              key={cell.dateStr}
              onClick={() => handleSelect(cell)}
              className={`
                relative flex flex-col items-center justify-center
                aspect-square rounded-xl transition-all duration-150
                ${isSelected
                  ? 'bg-dream-purple/30 ring-1 ring-dream-purple'
                  : isToday
                  ? 'bg-dream-surface ring-1 ring-dream-border'
                  : hasEntries
                  ? 'bg-dream-surface/60 hover:bg-dream-surface'
                  : 'hover:bg-dream-surface/30'}
                ${hasEntries ? 'cursor-pointer' : 'cursor-default'}
              `}
            >
              <span className={`text-sm font-medium ${
                isSelected ? 'text-dream-purple' :
                isToday ? 'text-dream-text' :
                hasEntries ? 'text-dream-text' : 'text-dream-muted'
              }`}>
                {cell.day}
              </span>

              {/* Entry dots */}
              {types.length > 0 && (
                <div className="flex gap-0.5 mt-0.5">
                  {types.map(type => (
                    <div
                      key={type}
                      className={`w-1 h-1 rounded-full ${TYPE_COLOR[type] ?? 'bg-dream-muted'}`}
                    />
                  ))}
                </div>
              )}
            </button>
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-4 justify-center">
        {[['dream', '🌙', 'Сон'], ['idea', '💡', 'Ідея'], ['thought', '💭', 'Думка']].map(
          ([type, emoji, label]) => (
            <div key={type} className="flex items-center gap-1.5 text-xs text-dream-muted">
              <div className={`w-2 h-2 rounded-full ${TYPE_COLOR[type]}`} />
              <span>{emoji} {label}</span>
            </div>
          )
        )}
      </div>
    </div>
  )
}
