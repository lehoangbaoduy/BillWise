'use client'
import { useEffect, useRef, useState } from "react"

// Multi-select filter styled to match the app's other single-line filter
// dropdowns (a closed trigger + dropdown panel, same shell as MerchantInput's
// .merchant-select-* classes) rather than a native <select multiple>, which
// renders as an always-open scrollable listbox and looks out of place next
// to the other single-line filters on this page.
export default function TypeMultiSelect({ id, options, value, onChange, placeholder = "All types" }) {
    const [isOpen, setIsOpen] = useState(false)
    const containerRef = useRef(null)

    useEffect(() => {
        if (!isOpen) return
        function handlePointerDown(event) {
            if (containerRef.current && !containerRef.current.contains(event.target)) setIsOpen(false)
        }
        function handleKeyDown(event) {
            if (event.key === "Escape") setIsOpen(false)
        }
        document.addEventListener("mousedown", handlePointerDown)
        document.addEventListener("keydown", handleKeyDown)
        return () => {
            document.removeEventListener("mousedown", handlePointerDown)
            document.removeEventListener("keydown", handleKeyDown)
        }
    }, [isOpen])

    function toggleOption(option) {
        onChange(value.includes(option) ? value.filter((item) => item !== option) : [...value, option])
    }

    const label = value.length === 0 ? placeholder : value.length === 1 ? value[0] : `${value.length} selected`

    return (
        <div className="merchant-select" ref={containerRef}>
            <button
                type="button"
                id={id}
                className="form-control merchant-select-trigger"
                onClick={() => setIsOpen((open) => !open)}
                aria-haspopup="listbox"
                aria-expanded={isOpen}
            >
                <span className={value.length === 0 ? "merchant-select-trigger-placeholder" : "merchant-select-trigger-value"}>
                    {label}
                </span>
                <i className={`fi fi-rr-angle-small-down merchant-select-chevron${isOpen ? " is-open" : ""}`} />
            </button>
            {isOpen && (
                <div className="merchant-select-panel">
                    <ul className="merchant-select-list" role="listbox" aria-multiselectable="true">
                        {options.map((option) => {
                            const isSelected = value.includes(option)
                            return (
                                <li key={option} role="option" aria-selected={isSelected}>
                                    <button
                                        type="button"
                                        className={`merchant-select-option${isSelected ? " is-selected" : ""}`}
                                        onClick={() => toggleOption(option)}
                                    >
                                        <span className="d-flex align-items-center gap-2">
                                            <input
                                                type="checkbox"
                                                className="form-check-input m-0"
                                                checked={isSelected}
                                                readOnly
                                                tabIndex={-1}
                                            />
                                            {option}
                                        </span>
                                    </button>
                                </li>
                            )
                        })}
                    </ul>
                </div>
            )}
        </div>
    )
}
