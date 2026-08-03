'use client'

// A curated set covering the categories/goals people actually create in a
// budgeting app -- broad enough that most picks need no custom entry, but
// the free-text fallback below still covers anything not listed here.
export const EMOJI_PRESETS = [
    "🍔", "🛒", "🍽️", "☕", "🚗", "⛽", "🚌", "🏠", "💡", "🌐",
    "📱", "💊", "🏋️", "🎬", "✈️", "👕", "🎓", "🐾", "🎁", "💰",
    "🏦", "🛡️", "🧸", "🔧", "❤️", "🔖",
]

export default function EmojiPicker({ value, onChange, name = "emoji" }) {
    return (
        <div>
            <div className="emoji-picker" role="radiogroup" aria-label="Icon">
                {EMOJI_PRESETS.map((emoji) => (
                    <button
                        key={emoji}
                        type="button"
                        role="radio"
                        aria-checked={value === emoji}
                        aria-label={emoji}
                        className={`emoji-picker-swatch${value === emoji ? " active" : ""}`}
                        onClick={() => onChange(emoji)}
                    >
                        {emoji}
                    </button>
                ))}
            </div>
            <input
                type="text"
                className="form-control mt-2"
                placeholder="Or type a custom emoji"
                maxLength={8}
                value={value}
                onChange={(event) => onChange(event.target.value)}
                aria-label={`Custom ${name}`}
            />
        </div>
    )
}
