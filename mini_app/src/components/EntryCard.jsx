import { haptic } from '../lib/telegram'

const TYPE_META = {
  dream:   { emoji: '🌙', label: 'Сон',   color: 'text-dream-purple', border: 'border-dream-purple/30' },
  idea:    { emoji: '💡', label: 'Ідея',   color: 'text-dream-teal',   border: 'border-dream-teal/30' },
  thought: { emoji: '💭', label: 'Думка',  color: 'text-dream-gold',   border: 'border-dream-gold/30' },
}

const TONE_EMOJI = {
  positive: '🌟', neutral: '🌙', anxious: '🌀',
  exciting: '⚡', sad: '🌧', mixed: '🌈',
}

export default function EntryCard({ entry, onClick }) {
  const meta = TYPE_META[entry.type] ?? TYPE_META.thought
  const analysis = entry.ai_analysis
  const time = entry.created_at?.slice(11, 16) ?? ''

  function handleClick() {
    haptic.light()
    onClick?.(entry)
  }

  return (
    <button
      onClick={handleClick}
      className={`
        w-full text-left rounded-2xl bg-dream-card border ${meta.border}
        p-4 transition-all duration-150 active:scale-[0.98]
        hover:bg-dream-card/80 animate-slide-up
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{meta.emoji}</span>
          <span className={`text-xs font-semibold uppercase tracking-wide ${meta.color}`}>
            {meta.label}
          </span>
        </div>
        <div className="flex items-center gap-2 text-dream-muted text-xs">
          {analysis && (
            <span title={analysis.emotional_tone}>
              {TONE_EMOJI[analysis.emotional_tone] ?? '🌙'}
            </span>
          )}
          <span>{time}</span>
        </div>
      </div>

      {/* Summary or raw text preview */}
      <p className="text-dream-text text-sm leading-relaxed line-clamp-2">
        {analysis?.summary || entry.raw_text}
      </p>

      {/* Tags */}
      {analysis?.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {analysis.tags.slice(0, 4).map(tag => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-full bg-dream-border/50 text-dream-muted"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Voice indicator */}
      {entry.voice_file_id && (
        <div className="flex items-center gap-1 mt-2 text-dream-muted text-xs">
          <span>🎙</span>
          <span>Голосовий запис</span>
        </div>
      )}
    </button>
  )
}
