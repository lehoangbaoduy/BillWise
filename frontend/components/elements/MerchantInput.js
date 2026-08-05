'use client'
import { useEffect, useMemo, useRef, useState } from "react"
import useSWR from "swr"
import { merchantsApi } from "@/lib/api"
import { getHiddenMerchants, hideMerchant } from "@/lib/hiddenMerchants"

const _OTHER_GROUP = "Other"

// Creatable searchable merchant select -- a closed trigger button showing the
// current value, opening a panel with its own dedicated search field, a
// filtered options list grouped by Merchant.type, and an explicit "Add
// '<query>'" action when nothing matches (or the list is empty). The
// committed value only changes on an explicit selection, so cashback rule
// matching never sees a half-typed name. Backed by the Merchant directory
// (/merchants), not raw transaction history -- selecting or quick-adding
// still only ever writes the merchant's plain name string onto the calling
// form (Transaction.merchant / CashbackRule.merchant stay strings, no FK).
export default function MerchantInput({ id = "merchant-input", value, onChange, required = false, placeholder = "e.g. Costco" }) {
    const { data: merchants, mutate } = useSWR("/merchants", () => merchantsApi.list())
    const [isOpen, setIsOpen] = useState(false)
    const [search, setSearch] = useState("")
    const [hiddenMerchants, setHiddenMerchants] = useState([])
    const [isAdding, setIsAdding] = useState(false)
    const [addError, setAddError] = useState(null)
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
                .filter((merchant) => !hiddenMerchants.includes(merchant.name.toLowerCase()))
                .filter((merchant) => merchant.name.toLowerCase().includes(trimmedSearch.toLowerCase())),
        [merchants, hiddenMerchants, trimmedSearch]
    )
    const groupedMerchants = useMemo(() => {
        const groups = new Map()
        for (const merchant of filteredMerchants) {
            const groupName = merchant.type || _OTHER_GROUP
            if (!groups.has(groupName)) groups.set(groupName, [])
            groups.get(groupName).push(merchant)
        }
        return [...groups.entries()].sort(([a], [b]) => {
            if (a === _OTHER_GROUP) return 1
            if (b === _OTHER_GROUP) return -1
            return a.localeCompare(b)
        })
    }, [filteredMerchants])
    const hasExactMatch = filteredMerchants.some((merchant) => merchant.name.toLowerCase() === trimmedSearch.toLowerCase())
    const canAddNew = trimmedSearch.length > 0 && !hasExactMatch

    function selectMerchant(name) {
        onChange(name)
        setIsOpen(false)
    }

    async function handleAddMerchant() {
        setIsAdding(true)
        setAddError(null)
        try {
            const created = await merchantsApi.create({ name: trimmedSearch })
            await mutate()
            selectMerchant(created.name)
        } catch (error) {
            setAddError(error.message || "Couldn't add that merchant.")
        } finally {
            setIsAdding(false)
        }
    }

    function handleHideMerchant(event, name) {
        event.stopPropagation()
        hideMerchant(name)
        setHiddenMerchants((names) => [...names, name.trim().toLowerCase()])
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
                        {groupedMerchants.map(([groupName, groupMerchants]) => (
                            <li key={groupName} className="merchant-select-group">
                                <span className="merchant-select-group-label">{groupName}</span>
                                <ul>
                                    {groupMerchants.map((merchant) => (
                                        <li
                                            key={merchant.id}
                                            role="option"
                                            aria-selected={merchant.name === value}
                                            className="merchant-select-row"
                                        >
                                            <button
                                                type="button"
                                                className={`merchant-select-option${merchant.name === value ? " is-selected" : ""}`}
                                                onClick={() => selectMerchant(merchant.name)}
                                            >
                                                <span>{merchant.name}</span>
                                                {merchant.name === value && <i className="fi fi-rr-check" />}
                                            </button>
                                            <button
                                                type="button"
                                                className="merchant-select-hide"
                                                aria-label={`Remove ${merchant.name} from merchant suggestions`}
                                                onClick={(event) => handleHideMerchant(event, merchant.name)}
                                            >
                                                <i className="fi fi-rr-cross-small" />
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </li>
                        ))}
                        {canAddNew && (
                            <li>
                                <button
                                    type="button"
                                    className="merchant-select-add"
                                    disabled={isAdding}
                                    onClick={handleAddMerchant}
                                >
                                    <i className="fi fi-rr-plus-small" />
                                    {isAdding ? "Adding…" : <>Add &quot;{trimmedSearch}&quot;</>}
                                </button>
                                {addError && <div className="text-danger small mt-1">{addError}</div>}
                            </li>
                        )}
                    </ul>
                </div>
            )}
        </div>
    )
}
