'use client'
import { useEffect, useRef, useState } from "react"

// Renders its own trigger <button> (callers keep their exact className/
// aria-label/disabled/children) and shows an inline confirmation popup
// anchored above it instead of window.confirm. A native confirm() dialog
// steals then returns focus to the trigger element, which -- combined with
// this app's outline-button hover/focus fill -- made the button flash into
// a jarring filled state with no mouse movement to clear it. This popup's
// own Cancel/Confirm buttons are separate DOM nodes that unmount on close,
// so focus never lands back on the trigger.
export default function ConfirmButton({
    message,
    confirmLabel = "Delete",
    cancelLabel = "Cancel",
    onConfirm,
    className,
    children,
    ...buttonProps
}) {
    const [isOpen, setIsOpen] = useState(false)
    const containerRef = useRef(null)

    useEffect(() => {
        if (!isOpen) return
        function handlePointerDown(event) {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setIsOpen(false)
            }
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

    function handleConfirm() {
        setIsOpen(false)
        onConfirm()
    }

    return (
        <span className="confirm-popover-anchor" ref={containerRef}>
            <button
                type="button"
                className={className}
                onClick={() => setIsOpen((open) => !open)}
                aria-haspopup="dialog"
                aria-expanded={isOpen}
                {...buttonProps}
            >
                {children}
            </button>
            {isOpen && (
                <div className="confirm-popover" role="dialog" aria-label={message}>
                    <div className="confirm-popover-arrow" />
                    <p className="confirm-popover-message">{message}</p>
                    <div className="confirm-popover-actions">
                        <button type="button" className="btn btn-sm btn-danger" onClick={handleConfirm}>
                            {confirmLabel}
                        </button>
                        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => setIsOpen(false)}>
                            {cancelLabel}
                        </button>
                    </div>
                </div>
            )}
        </span>
    )
}
