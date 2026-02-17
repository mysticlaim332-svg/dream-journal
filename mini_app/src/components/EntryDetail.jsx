import { useState, useEffect } from 'react'
import { fetchEntry } from '../lib/api'
import { useBackButton, haptic } from '../lib/telegram'

const TYPE_META = {
  dream:   { emoji: '🌙', label: 'Сон',   color: 'text-dream-purple' },
  idea:    { emoji: '💡', label: 'Ідея',   color: 'text-dream-teal' },
  thought: { emoji: '💭', label: 'Думка',  color: 'text-dream-gold' },
}

const TONE_LABEL = {
  positive: '🌟 Позитивний',
  neutral:  '🌙 Нейтральний',
  anxious:  '🌀 Тривожний',
  exciting: '⚡ Захоплюючий',
  sad:      '🌧 Сумний',
  mixed:    '🌈 Змішаний',
}

const CONN_LABEL = {
  recurring_theme: 'Повторюваний мотив',
  similar_emotion: 'Схожа емоція',
  related_idea:    "Пов'язана ідея",
  same_symbol:     'Той самий символ',
}

export default function EntryDetail({ entryId, onBack }) {
  const [entry, setEntry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Register Telegram back button
  useEffect(() => useBackButton(onBack), [onBack])

  useEffect(() => {
    setLoading(true)
    fetchEntry(entryId)
      .then(setEntry)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [entryId])

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

  if (!entry) return null

  const meta = TYPE_META[entry.type] ?? TYPE_META.thought
  const analysis = entry.ai_analysis
  const date = entry.created_at?.slice(0, 16).replace('T', ' ') ?? ''
  const connections = entry.entry_connections ?? []

  return (
    <div className="animate-slide-up space-y-4 pb-8">
      {/* Header */}
      <div className="flex items-center gap-3 px-1">
        <span className="text-3xl">{meta.emoji}</span>
        <div>
          <p className={`text-xs font-semibold uppercase tracking-wide ${meta.color}`}>
            {meta.label}
          </p>
          <p className="text-dream-muted text-xs">{date}</p>
        </div>
      </div>

      {/* Raw text */}
      <div className="bg-dream-card rounded-2xl p-4">
        <p className="text-xs text-dream-muted mb-2 uppercase tracking-wide">Запис</p>
        <p className="text-dream-text text-sm leading-relaxed whitespace-pre-wrap">
          {entry.raw_text}
        </p>
        {entry.voice_file_id && (
          <p className="text-dream-muted text-xs mt-2">🎙 Розпізнано з голосового</p>
        )}
      </div>

      {/* AI Analysis */}
      {analysis && (
        <>
          {/* Summary */}
          <div className="bg-dream-card rounded-2xl p-4">
            <p className="text-xs text-dream-muted mb-2 uppercase tracking-wide">AI Резюме</p>
            <p className="text-dream-text text-sm leading-relaxed">{analysis.summary}</p>
          </div>

          {/* Mood + Themes row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-dream-card rounded-2xl p-4">
              <p className="text-xs text-dream-muted mb-2 uppercase tracking-wide">Настрій</p>
              <p className="text-dream-text text-sm">
                {TONE_LABEL[analysis.emotional_tone] ?? analysis.emotional_tone}
              </p>
            </div>
            <div className="bg-dream-card rounded-2xl p-4">
              <p className="text-xs text-dream-muted mb-2 uppercase tracking-wide">Теми</p>
              <div className="flex flex-wrap gap-1">
                {(analysis.key_themes ?? []).map(t => (
                  <span key={t} className="text-xs text-dream-teal">· {t}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Tags */}
          {analysis.tags?.length > 0 && (
            <div className="bg-dream-card rounded-2xl p-4">
              <p className="text-xs text-dream-muted mb-3 uppercase tracking-wide">Теги</p>
              <div className="flex flex-wrap gap-2">
                {analysis.tags.map(tag => (
                  <span
                    key={tag}
                    className="text-sm px-3 py-1 rounded-full bg-dream-border text-dream-text"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Connections */}
      {connections.length > 0 && (
        <div className="bg-dream-card rounded-2xl p-4">
          <p className="text-xs text-dream-muted mb-3 uppercase tracking-wide">
            🔗 Зв'язки з іншими записами
          </p>
          <div className="space-y-3">
            {connections.map(conn => {
              const related = conn.entries__entry_id_b ?? conn.entries
              const relMeta = TYPE_META[related?.type] ?? TYPE_META.thought
              return (
                <div key={conn.id} className="flex items-start gap-3 p-3 rounded-xl bg-dream-surface">
                  <span className="text-lg flex-shrink-0">{relMeta.emoji}</span>
                  <div className="min-w-0">
                    <p className="text-xs text-dream-muted mb-1">
                      {CONN_LABEL[conn.connection_type] ?? conn.connection_type}
                      {' · '}
                      {Math.round((conn.similarity_score ?? 0) * 100)}% схожість
                    </p>
                    <p className="text-dream-text text-xs leading-relaxed">
                      {conn.description}
                    </p>
                    {related?.ai_analysis?.summary && (
                      <p className="text-dream-muted text-xs mt-1 line-clamp-1 italic">
                        «{related.ai_analysis.summary}»
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
