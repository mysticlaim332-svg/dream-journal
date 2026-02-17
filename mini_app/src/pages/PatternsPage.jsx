import { useState } from 'react'
import { usePatterns } from '../hooks/useEntries'

const TYPE_META = {
  dream:   { emoji: '🌙', label: 'Сон',   color: 'text-dream-purple' },
  idea:    { emoji: '💡', label: 'Ідея',  color: 'text-dream-teal' },
  thought: { emoji: '💭', label: 'Думка', color: 'text-dream-gold' },
}

const CONN_META = {
  recurring_theme: { label: 'Повторювана тема', color: 'bg-dream-purple/20 text-dream-purple' },
  similar_emotion: { label: 'Схожий настрій',   color: 'bg-blue-500/20 text-blue-400' },
  related_idea:    { label: 'Схожа ідея',        color: 'bg-dream-teal/20 text-dream-teal' },
  same_symbol:     { label: 'Той самий символ',  color: 'bg-dream-gold/20 text-dream-gold' },
}

function ThemeCard({ theme, count, entries }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className="bg-dream-card rounded-2xl p-4 cursor-pointer active:opacity-80 transition-opacity"
      onClick={() => setExpanded(v => !v)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-2xl">🔁</span>
          <div className="min-w-0">
            <p className="text-dream-text font-medium truncate">{theme}</p>
            <p className="text-dream-muted text-xs mt-0.5">
              зустрічається в <span className="text-dream-purple font-semibold">{count}</span> записах
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          <div className="flex gap-1">
            {[...new Set(entries.map(e => e.type))].map(type => (
              <span key={type} className="text-sm">{TYPE_META[type]?.emoji ?? '📝'}</span>
            ))}
          </div>
          <span className="text-dream-muted text-sm">{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 space-y-2 border-t border-dream-border pt-3">
          {entries.map(e => (
            <div key={e.id} className="flex items-start gap-2">
              <span className="text-sm mt-0.5">{TYPE_META[e.type]?.emoji ?? '📝'}</span>
              <div className="min-w-0">
                <p className="text-dream-muted text-xs">{e.date}</p>
                <p className="text-dream-text text-sm leading-snug">{e.summary || '—'}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ConnectionCard({ conn }) {
  const meta = CONN_META[conn.connection_type] ?? { label: conn.connection_type, color: 'bg-dream-border text-dream-muted' }
  const entryA = conn.entry_a
  const entryB = conn.entry_b

  return (
    <div className="bg-dream-card rounded-2xl p-4 space-y-3">
      {/* Type badge + description */}
      <div className="flex items-start gap-2">
        <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${meta.color}`}>
          {meta.label}
        </span>
      </div>
      <p className="text-dream-text text-sm leading-snug">{conn.description}</p>

      {/* Two entries */}
      <div className="grid grid-cols-2 gap-2">
        {[entryA, entryB].map((entry, i) => (
          <div key={i} className="bg-dream-bg rounded-xl p-3 space-y-1">
            <div className="flex items-center gap-1.5">
              <span className="text-sm">{TYPE_META[entry.type]?.emoji ?? '📝'}</span>
              <span className="text-dream-muted text-xs">{entry.date}</span>
            </div>
            <p className="text-dream-text text-xs leading-snug line-clamp-3">
              {entry.summary || '—'}
            </p>
          </div>
        ))}
      </div>

      {/* Similarity score */}
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1 bg-dream-border rounded-full overflow-hidden">
          <div
            className="h-full bg-dream-purple rounded-full"
            style={{ width: `${Math.round(conn.similarity_score * 100)}%` }}
          />
        </div>
        <span className="text-dream-muted text-xs flex-shrink-0">
          {Math.round(conn.similarity_score * 100)}% схожість
        </span>
      </div>
    </div>
  )
}

export default function PatternsPage() {
  const { patterns, loading, error } = usePatterns()

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

  const hasThemes = patterns?.recurring_themes?.length > 0
  const hasConnections = patterns?.connections?.length > 0

  if (!hasThemes && !hasConnections) return (
    <div className="text-center py-20 px-8">
      <p className="text-5xl mb-4">🔮</p>
      <p className="text-dream-text font-medium text-lg mb-2">Ще немає патернів</p>
      <p className="text-dream-muted text-sm leading-relaxed">
        Записуй сни та ідеї регулярно — і AI знайде повторювані теми та закономірності між ними
      </p>
    </div>
  )

  return (
    <div className="px-4 py-4 space-y-6 pb-8 animate-fade-in">

      {/* Recurring themes */}
      {hasThemes && (
        <section>
          <p className="text-xs text-dream-muted uppercase tracking-wide mb-3">
            Повторювані теми
          </p>
          <div className="space-y-3">
            {patterns.recurring_themes.map(item => (
              <ThemeCard
                key={item.theme}
                theme={item.theme}
                count={item.count}
                entries={item.entries}
              />
            ))}
          </div>
        </section>
      )}

      {/* AI-found connections */}
      {hasConnections && (
        <section>
          <p className="text-xs text-dream-muted uppercase tracking-wide mb-3">
            Зв'язки знайдені AI
          </p>
          <div className="space-y-3">
            {patterns.connections.map((conn, i) => (
              <ConnectionCard key={i} conn={conn} />
            ))}
          </div>
        </section>
      )}

    </div>
  )
}
