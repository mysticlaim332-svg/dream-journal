import { useState } from 'react'
import Calendar from '../components/Calendar'
import EntryCard from '../components/EntryCard'
import EntryDetail from '../components/EntryDetail'
import { useMonthEntries } from '../hooks/useEntries'
import { haptic } from '../lib/telegram'

const UK_MONTHS = [
  '', 'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
  'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень',
]

export default function CalendarPage() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [selectedDate, setSelectedDate] = useState(null)
  const [selectedEntryId, setSelectedEntryId] = useState(null)

  const monthStr = `${year}-${String(month).padStart(2, '0')}`
  const { by_date, loading, error } = useMonthEntries(monthStr)

  function prevMonth() {
    haptic.light()
    if (month === 1) { setYear(y => y - 1); setMonth(12) }
    else setMonth(m => m - 1)
    setSelectedDate(null)
  }

  function nextMonth() {
    haptic.light()
    if (month === 12) { setYear(y => y + 1); setMonth(1) }
    else setMonth(m => m + 1)
    setSelectedDate(null)
  }

  // If viewing an entry detail
  if (selectedEntryId) {
    return (
      <div className="px-4 pt-4">
        <EntryDetail
          entryId={selectedEntryId}
          onBack={() => setSelectedEntryId(null)}
        />
      </div>
    )
  }

  const dayEntries = selectedDate ? (by_date[selectedDate] ?? []) : []

  return (
    <div className="flex flex-col h-full">
      {/* Month navigation */}
      <div className="flex items-center justify-between px-4 py-4">
        <button
          onClick={prevMonth}
          className="w-9 h-9 flex items-center justify-center rounded-xl bg-dream-surface text-dream-muted hover:text-dream-text transition-colors"
        >
          ‹
        </button>
        <div className="text-center">
          <h2 className="text-dream-text font-semibold text-lg">
            {UK_MONTHS[month]}
          </h2>
          <p className="text-dream-muted text-xs">{year}</p>
        </div>
        <button
          onClick={nextMonth}
          className="w-9 h-9 flex items-center justify-center rounded-xl bg-dream-surface text-dream-muted hover:text-dream-text transition-colors"
        >
          ›
        </button>
      </div>

      {/* Calendar grid */}
      <div className="px-4">
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-dream-purple border-t-transparent rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="text-center text-dream-muted py-8">
            <p>⚠️ {error}</p>
          </div>
        ) : (
          <Calendar
            year={year}
            month={month}
            byDate={by_date}
            selectedDate={selectedDate}
            onSelectDate={setSelectedDate}
          />
        )}
      </div>

      {/* Day entries list */}
      {selectedDate && (
        <div className="flex-1 overflow-y-auto px-4 mt-6 animate-slide-up">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-dream-text font-medium text-sm">
              {selectedDate}
            </h3>
            <span className="text-dream-muted text-xs">
              {dayEntries.length} {dayEntries.length === 1 ? 'запис' : 'записів'}
            </span>
          </div>

          {dayEntries.length === 0 ? (
            <p className="text-dream-muted text-sm text-center py-8">
              Немає записів за цей день
            </p>
          ) : (
            <div className="space-y-3 pb-6">
              {dayEntries.map(entry => (
                <EntryCard
                  key={entry.id}
                  entry={entry}
                  onClick={() => { haptic.light(); setSelectedEntryId(entry.id) }}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!selectedDate && !loading && (
        <div className="flex-1 flex items-center justify-center text-dream-muted text-sm px-8 text-center">
          Натисни на день зі значком щоб побачити записи
        </div>
      )}
    </div>
  )
}
