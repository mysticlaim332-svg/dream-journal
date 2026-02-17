import { useStats } from '../hooks/useEntries'

const TONE_META = {
  positive: { emoji: '🌟', label: 'Позитивний', color: 'bg-green-500/20 text-green-400' },
  neutral:  { emoji: '🌙', label: 'Нейтральний', color: 'bg-dream-purple/20 text-dream-purple' },
  anxious:  { emoji: '🌀', label: 'Тривожний',  color: 'bg-orange-500/20 text-orange-400' },
  exciting: { emoji: '⚡', label: 'Захоплюючий', color: 'bg-yellow-500/20 text-yellow-400' },
  sad:      { emoji: '🌧', label: 'Сумний',      color: 'bg-blue-500/20 text-blue-400' },
  mixed:    { emoji: '🌈', label: 'Змішаний',    color: 'bg-pink-500/20 text-pink-400' },
}

const TYPE_META = {
  dream:   { emoji: '🌙', label: 'Снів',   color: 'text-dream-purple' },
  idea:    { emoji: '💡', label: 'Ідей',   color: 'text-dream-teal' },
  thought: { emoji: '💭', label: 'Думок',  color: 'text-dream-gold' },
}

function MoodBar({ tone, count, total }) {
  const meta = TONE_META[tone] ?? { emoji: '❓', label: tone, color: 'bg-dream-muted/20 text-dream-muted' }
  const pct = total > 0 ? Math.round((count / total) * 100) : 0

  return (
    <div className="flex items-center gap-3">
      <span className="text-base w-6 text-center flex-shrink-0">{meta.emoji}</span>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between mb-1">
          <span className="text-dream-text text-xs">{meta.label}</span>
          <span className="text-dream-muted text-xs">{count} ({pct}%)</span>
        </div>
        <div className="h-1.5 bg-dream-border rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${meta.color.includes('green') ? 'bg-green-500' : meta.color.includes('orange') ? 'bg-orange-500' : meta.color.includes('yellow') ? 'bg-yellow-500' : meta.color.includes('blue') ? 'bg-blue-500' : meta.color.includes('pink') ? 'bg-pink-500' : 'bg-dream-purple'}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  )
}

function TagCloud({ tags }) {
  if (!tags?.length) return <p className="text-dream-muted text-sm text-center py-4">Немає тегів</p>
  const maxCount = tags[0]?.count ?? 1

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map(({ tag, count }) => {
        const size = count / maxCount
        return (
          <span
            key={tag}
            className="px-3 py-1 rounded-full bg-dream-border text-dream-text transition-all"
            style={{
              fontSize: `${0.65 + size * 0.4}rem`,
              opacity: 0.5 + size * 0.5,
              borderColor: `rgba(123, 109, 232, ${size * 0.8})`,
              border: '1px solid',
            }}
          >
            {tag}
            <span className="ml-1 text-dream-muted text-xs">{count}</span>
          </span>
        )
      })}
    </div>
  )
}

export default function InsightsPage() {
  const { stats, loading, error } = useStats()

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-6 h-6 border-2 border-dream-purple border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (error) return (
    <div className="text-center text-dream-muted py-16">
      <p className="text-2xl mb-2">⚠️</p>
      <p>{error}</p>
    </div>
  )

  if (!stats) return null

  const totalMood = Object.values(stats.mood_counts ?? {}).reduce((a, b) => a + b, 0)

  return (
    <div className="px-4 py-4 space-y-5 pb-8 animate-fade-in">
      {/* Totals */}
      <div className="grid grid-cols-3 gap-3">
        {Object.entries(stats.type_counts ?? {}).map(([type, count]) => {
          const meta = TYPE_META[type] ?? { emoji: '📝', label: type, color: 'text-dream-text' }
          return (
            <div key={type} className="bg-dream-card rounded-2xl p-4 text-center">
              <p className="text-2xl mb-1">{meta.emoji}</p>
              <p className={`text-xl font-semibold ${meta.color}`}>{count}</p>
              <p className="text-dream-muted text-xs mt-0.5">{meta.label}</p>
            </div>
          )
        })}
      </div>

      {/* Total */}
      <div className="bg-dream-card rounded-2xl p-4 flex items-center justify-between">
        <div>
          <p className="text-dream-muted text-xs uppercase tracking-wide">Всього записів</p>
          <p className="text-dream-text text-2xl font-semibold mt-0.5">{stats.total_entries}</p>
        </div>
        <span className="text-4xl">📖</span>
      </div>

      {/* Mood distribution */}
      {totalMood > 0 && (
        <div className="bg-dream-card rounded-2xl p-4">
          <p className="text-xs text-dream-muted uppercase tracking-wide mb-4">Настрій записів</p>
          <div className="space-y-3">
            {Object.entries(stats.mood_counts ?? {})
              .sort((a, b) => b[1] - a[1])
              .map(([tone, count]) => (
                <MoodBar key={tone} tone={tone} count={count} total={totalMood} />
              ))}
          </div>
        </div>
      )}

      {/* Tag cloud */}
      {stats.top_tags?.length > 0 && (
        <div className="bg-dream-card rounded-2xl p-4">
          <p className="text-xs text-dream-muted uppercase tracking-wide mb-4">
            Топ теги
          </p>
          <TagCloud tags={stats.top_tags} />
        </div>
      )}

      {/* Monthly activity */}
      {Object.keys(stats.monthly ?? {}).length > 0 && (
        <div className="bg-dream-card rounded-2xl p-4">
          <p className="text-xs text-dream-muted uppercase tracking-wide mb-4">
            Активність по місяцях
          </p>
          <div className="space-y-2">
            {Object.entries(stats.monthly)
              .slice(-6)
              .reverse()
              .map(([month, count]) => {
                const maxMonth = Math.max(...Object.values(stats.monthly))
                const pct = Math.round((count / maxMonth) * 100)
                return (
                  <div key={month} className="flex items-center gap-3">
                    <span className="text-dream-muted text-xs w-16 flex-shrink-0">{month}</span>
                    <div className="flex-1 h-1.5 bg-dream-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-dream-purple rounded-full transition-all duration-700"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-dream-text text-xs w-4 text-right">{count}</span>
                  </div>
                )
              })}
          </div>
        </div>
      )}
    </div>
  )
}
