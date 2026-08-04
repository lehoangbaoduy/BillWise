'use client'
import { useEffect, useId, useLayoutEffect, useRef, useState } from "react"
import { createPortal } from "react-dom"

const POPOVER_GAP = 10
const VIEWPORT_MARGIN = 8

// Renders its own trigger <button> (callers keep their exact className/
// aria-label/disabled/children) and shows an inline confirmation popup
// anchored above it instead of window.confirm. A native confirm() dialog
// steals then returns focus to the trigger element, which -- combined with
// this app's outline-button hover/focus fill -- made the button flash into
// a jarring filled state with no mouse movement to clear it. This popup's
// own Cancel/Confirm buttons are separate DOM nodes that unmount on close,
// so focus never lands back on the trigger.
//
// The popup is portaled to document.body and positioned with `fixed`
// viewport coordinates rather than being an absolutely-positioned child of
// the trigger's own anchor -- ConfirmButton renders inside `.table-responsive`
// on the Transaction History page, and any ancestor with non-visible overflow
// (table-responsive sets overflow-x: auto, which per spec also computes
// overflow-y to auto) clips an absolutely-positioned descendant instead of
// letting it escape to the viewport, cutting the popover off for rows near
// the top of the scrolled table.
export default function ConfirmButton({
    message,
    confirmLabel = "Delete",
    cancelLabel = "Cancel",
    onConfirm,
    className,
    children,
    // When set, the popover also collects a required free-text value (e.g.
    // "Paid by who?" for marking a Reimbursement transaction paid) and passes
    // it as onConfirm's argument instead of calling onConfirm with no args.
    inputLabel,
    inputPlaceholder,
    ...buttonProps
}) {
    const [isOpen, setIsOpen] = useState(false)
    const [position, setPosition] = useState(null)
    const [inputValue, setInputValue] = useState("")
    const containerRef = useRef(null)
    const buttonRef = useRef(null)
    const popoverRef = useRef(null)
    const inputId = useId()

    useEffect(() => {
        if (!isOpen) setInputValue("")
    }, [isOpen])

    useEffect(() => {
        if (!isOpen) return
        function isInside(target) {
            return (
                (containerRef.current && containerRef.current.contains(target)) ||
                (popoverRef.current && popoverRef.current.contains(target))
            )
        }
        function handlePointerDown(event) {
            if (!isInside(event.target)) setIsOpen(false)
        }
        function handleKeyDown(event) {
            if (event.key === "Escape") setIsOpen(false)
        }
        // A scrolled ancestor (e.g. the table-responsive wrapper) moves the
        // trigger button without moving this fixed-position portal -- closing
        // on scroll is simpler and safer than continuously re-measuring and
        // re-anchoring a popover that would otherwise visually detach from the
        // row it's confirming a delete for. `capture: true` catches scroll on
        // the table's own scroll container, not just window-level scroll.
        function handleScroll() {
            setIsOpen(false)
        }
        document.addEventListener("mousedown", handlePointerDown)
        document.addEventListener("keydown", handleKeyDown)
        window.addEventListener("scroll", handleScroll, true)
        return () => {
            document.removeEventListener("mousedown", handlePointerDown)
            document.removeEventListener("keydown", handleKeyDown)
            window.removeEventListener("scroll", handleScroll, true)
        }
    }, [isOpen])

    useLayoutEffect(() => {
        if (!isOpen || !buttonRef.current) return
        const rect = buttonRef.current.getBoundingClientRect()
        setPosition({
            bottom: window.innerHeight - rect.top + POPOVER_GAP,
            centerX: rect.left + rect.width / 2,
        })
    }, [isOpen])

    // Second pass: once the popover has rendered at its natural width, clamp
    // its horizontal center so it never sits partially off-screen at either
    // viewport edge -- e.g. a delete action in the table's rightmost column.
    useLayoutEffect(() => {
        if (!isOpen || !position || !popoverRef.current) return
        const popoverRect = popoverRef.current.getBoundingClientRect()
        const halfWidth = popoverRect.width / 2
        const minCenter = VIEWPORT_MARGIN + halfWidth
        const maxCenter = window.innerWidth - VIEWPORT_MARGIN - halfWidth
        const clamped = Math.min(Math.max(position.centerX, minCenter), maxCenter)
        popoverRef.current.style.left = `${clamped}px`
    }, [isOpen, position])

    const trimmedInput = inputValue.trim()
    const isConfirmDisabled = Boolean(inputLabel) && !trimmedInput

    function handleConfirm() {
        if (isConfirmDisabled) return
        setIsOpen(false)
        onConfirm(inputLabel ? trimmedInput : undefined)
    }

    return (
        <span className="confirm-popover-anchor" ref={containerRef}>
            <button
                ref={buttonRef}
                type="button"
                className={className}
                onClick={() => setIsOpen((open) => !open)}
                aria-haspopup="dialog"
                aria-expanded={isOpen}
                {...buttonProps}
            >
                {children}
            </button>
            {isOpen && position && createPortal(
                <div
                    ref={popoverRef}
                    className="confirm-popover"
                    role="dialog"
                    aria-label={message}
                    style={{ bottom: `${position.bottom}px`, left: `${position.centerX}px` }}
                >
                    <div className="confirm-popover-arrow" />
                    <p className="confirm-popover-message">{message}</p>
                    {inputLabel && (
                        <div className="mb-2 text-start">
                            <label className="form-label small mb-1" htmlFor={inputId}>{inputLabel}</label>
                            <input
                                id={inputId}
                                type="text"
                                className="form-control form-control-sm"
                                value={inputValue}
                                onChange={(event) => setInputValue(event.target.value)}
                                placeholder={inputPlaceholder}
                                autoFocus
                            />
                        </div>
                    )}
                    <div className="confirm-popover-actions">
                        <button
                            type="button"
                            className="btn btn-sm btn-danger"
                            onClick={handleConfirm}
                            disabled={isConfirmDisabled}
                        >
                            {confirmLabel}
                        </button>
                        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => setIsOpen(false)}>
                            {cancelLabel}
                        </button>
                    </div>
                </div>,
                document.body
            )}
        </span>
    )
}
