// Small pill-style tab group for narrowing a list (All/Private/Shared,
// category type, merchant type, ...) without navigating -- purely local
// filter state owned by the caller.
export default function FilterTabs({ options, value, onChange, className = "" }) {
    return (
        <div className={`filter-tabs d-flex flex-wrap gap-2${className ? ` ${className}` : ""}`} role="tablist">
            {options.map((option) => {
                const isActive = option.value === value
                return (
                    <button
                        key={option.value}
                        type="button"
                        role="tab"
                        aria-selected={isActive}
                        onClick={() => onChange(option.value)}
                        style={{
                            padding: "4px 14px",
                            borderRadius: 999,
                            border: isActive ? "1px solid var(--bs-primary)" : "1px solid var(--bs-border-color)",
                            backgroundColor: isActive ? "var(--bs-primary)" : "transparent",
                            color: isActive ? "#fff" : "var(--bs-body-color)",
                            fontSize: "0.8rem",
                            fontWeight: 600,
                            lineHeight: 1.6,
                            transition: "background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease",
                        }}
                    >
                        {option.label}
                    </button>
                )
            })}
        </div>
    )
}
