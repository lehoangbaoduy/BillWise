'use client'

// Every preset holds >=4.5:1 contrast with white text, so any card/badge that
// uses one of these as a background can always pair it with white text
// without a per-color contrast check.
export const COLOR_PRESETS = [
    { name: "Pink", value: "#C93B7D" },
    { name: "Dark Rose", value: "#7A2048" },
    { name: "Violet", value: "#4a3aa7" },
    { name: "Teal", value: "#0d7a54" },
    { name: "Orange", value: "#b8501f" },
    { name: "Blue", value: "#1c5cab" },
    { name: "Maroon", value: "#5c2338" },
    { name: "Charcoal", value: "#3d2b33" },
]

export default function ColorPicker({ value, onChange, name = "color" }) {
    return (
        <div className="color-picker" role="radiogroup" aria-label="Color">
            {COLOR_PRESETS.map((preset) => (
                <button
                    key={preset.value}
                    type="button"
                    role="radio"
                    aria-checked={value === preset.value}
                    aria-label={preset.name}
                    title={preset.name}
                    className={`color-picker-swatch${value === preset.value ? " active" : ""}`}
                    style={{ backgroundColor: preset.value }}
                    onClick={() => onChange(preset.value)}
                >
                    {value === preset.value && <i className="fi fi-rr-check" aria-hidden="true" />}
                </button>
            ))}
        </div>
    )
}
