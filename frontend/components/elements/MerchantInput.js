'use client'
import { useEffect, useMemo, useRef, useState } from "react"
import useSWR from "swr"
import { transactionsApi } from "@/lib/api"
import { getHiddenMerchants, hideMerchant } from "@/lib/hiddenMerchants"

// Creatable searchable merchant select -- a closed trigger button showing the
// current value, opening a panel with its own dedicated search field, a
// filtered options list, and an explicit "Add '<query>'" action when nothing
// matches (or the list is empty). The committed value only changes on an
// explicit selection, so cashback rule matching never sees a half-typed name.
export default function MerchantInput({ id = "merchant-input", value, onChange, required = false, placeholder = "e.g. Costco" }) {
    const { data: merchants } = useSWR("/transactions/merchants", () => transactionsApi.merchants())
    const [isOpen, setIsOpen] = useState(false)
    const [search, setSearch] = useState("")
    const [hiddenMerchants, setHiddenMerchants] = useState([])
    const containerRef = useRef(null)
    const searchInputRef = useRef(null)

    useEffect(() => {
        setHiddenMerchants(getHiddenMerchants())
    }, [])

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

    useEffect(() => {
        if (isOpen) {
            setSearch("")
            searchInputRef.current?.focus()
        }
    }, [isOpen])

    const trimmedSearch = search.trim()
    const filteredMerchants = useMemo(
        () =>
            (merchants ?? [])
                .filter((merchant) => !hiddenMerchants.includes(merchant.toLowerCase()))
                .filter((merchant) => merchant.toLowerCase().includes(trimmedSearch.toLowerCase())),
        [merchants, hiddenMerchants, trimmedSearch]
    )
    const hasExactMatch = filteredMerchants.some((merchant) => merchant.toLowerCase() === trimmedSearch.toLowerCase())
    const canAddNew = trimmedSearch.length > 0 && !hasExactMatch

    function selectMerchant(merchant) {
        onChange(merchant)
        setIsOpen(false)
    }

    function handleHideMerchant(event, merchant) {
        event.stopPropagation()
        hideMerchant(merchant)
        setHiddenMerchants((names) => [...names, merchant.trim().toLowerCase()])
    }

    return (
        <div className="merchant-select" ref={containerRef}>
            <button
                type="button"
                id={id}
                className="form-control merchant-select-trigger"
                onClick={() => setIsOpen((open) => !open)}
                aria-haspopup="listbox"
                aria-expanded={isOpen}
                aria-required={required}
            >
                <span className={value ? "merchant-select-trigger-value" : "merchant-select-trigger-placeholder"}>
                    {value || placeholder}
                </span>
                <i className={`fi fi-rr-angle-small-down merchant-select-chevron${isOpen ? " is-open" : ""}`} />
            </button>
            {isOpen && (
                <div className="merchant-select-panel">
                    <div className="merchant-select-search">
                        <input
                            ref={searchInputRef}
                            type="text"
                            className="form-control"
                            placeholder="Search merchants…"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                        />
                    </div>
                    <ul className="merchant-select-list" role="listbox">
                        {filteredMerchants.length === 0 && !canAddNew && (
                            <li className="merchant-select-empty">
                                {trimmedSearch ? "No matches." : "No merchants yet — type to add one."}
                            </li>
                        )}
                        {filteredMerchants.map((merchant) => (
                            <li key={merchant} role="option" aria-selected={merchant === value} className="merchant-select-row">
                                <button
                                    type="button"
                                    className={`merchant-select-option${merchant === value ? " is-selected" : ""}`}
                                    onClick={() => selectMerchant(merchant)}
                                >
                                    <span>{merchant}</span>
                                    {merchant === value && <i className="fi fi-rr-check" />}
                                </button>
                                <button
                                    type="button"
                                    className="merchant-select-hide"
                                    aria-label={`Remove ${merchant} from merchant suggestions`}
                                    onClick={(event) => handleHideMerchant(event, merchant)}
                                >
                                    <i className="fi fi-rr-cross-small" />
                                </button>
                            </li>
                        ))}
                        {canAddNew && (
                            <li>
                                <button type="button" className="merchant-select-add" onClick={() => selectMerchant(trimmedSearch)}>
                                    <i className="fi fi-rr-plus-small" />
                                    Add &quot;{trimmedSearch}&quot;
                                </button>
                            </li>
                        )}
                    </ul>
                </div>
            )}
        </div>
    )
}
