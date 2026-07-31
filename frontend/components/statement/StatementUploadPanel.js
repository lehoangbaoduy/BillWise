"use client"
import { useState } from "react"
import { ocrApi } from "@/lib/api"

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024
const ACCEPTED_TYPES = "image/jpeg,image/png,image/heic,image/heif,application/pdf"

function formatCurrency(value) {
    if (value === null || value === undefined) return "—"
    return `$${Number(value).toFixed(2)}`
}

export default function StatementUploadPanel({ onConfirm, onCancel }) {
    const [selectedFile, setSelectedFile] = useState(null)
    const [isScanning, setIsScanning] = useState(false)
    const [scanError, setScanError] = useState(null)
    const [extraction, setExtraction] = useState(null)
    const [balanceInput, setBalanceInput] = useState("")
    const [isConfirming, setIsConfirming] = useState(false)
    const [confirmError, setConfirmError] = useState(null)

    function handleFileChange(event) {
        const file = event.target.files?.[0] ?? null
        setScanError(null)
        if (file && file.size > MAX_UPLOAD_BYTES) {
            setScanError("File exceeds the 10MB limit.")
            setSelectedFile(null)
            return
        }
        setSelectedFile(file)
    }

    async function handleScan() {
        if (!selectedFile) return
        setIsScanning(true)
        setScanError(null)
        try {
            const result = await ocrApi.scanStatement(selectedFile)
            setExtraction(result)
            setBalanceInput(result.statement_balance ?? "")
        } catch (err) {
            setScanError(err.message || "Couldn't read this statement.")
        } finally {
            setIsScanning(false)
        }
    }

    async function handleConfirm() {
        if (balanceInput === "" || Number.isNaN(Number(balanceInput))) {
            setConfirmError("Enter a valid balance.")
            return
        }
        setIsConfirming(true)
        setConfirmError(null)
        try {
            await onConfirm(Number(balanceInput))
        } catch (err) {
            setConfirmError(err.message || "Couldn't update the balance.")
        } finally {
            setIsConfirming(false)
        }
    }

    if (extraction) {
        return (
            <div>
                {extraction.warnings.length > 0 && (
                    <div className="alert alert-warning" role="alert">
                        {/* index-keyed: this array is a fixed, immutable snapshot from a single
                            OCR response — never reordered, filtered, or mutated after render —
                            and warning text isn't guaranteed unique, so it can't key safely. */}
                        {extraction.warnings.map((warning, index) => (
                            <p key={index} className="mb-0">{warning}</p>
                        ))}
                    </div>
                )}

                <div className="mb-3">
                    <label className="form-label" htmlFor="statement-balance-input">
                        Statement balance {extraction.ocr_status === "low_confidence" && (
                            <span className="badge bg-warning text-dark ms-1">Review carefully</span>
                        )}
                    </label>
                    <input
                        id="statement-balance-input"
                        type="number"
                        step="0.01"
                        className="form-control"
                        value={balanceInput}
                        onChange={(event) => setBalanceInput(event.target.value)}
                        disabled={isConfirming}
                    />
                    <div className="form-text">
                        This is the only value applied to your wallet. Edit it if the scan got it wrong.
                    </div>
                </div>

                <dl className="row mb-3">
                    <dt className="col-sm-5">Statement date</dt>
                    <dd className="col-sm-7">{extraction.statement_date || "—"}</dd>
                    <dt className="col-sm-5">Due date</dt>
                    <dd className="col-sm-7">{extraction.due_date || "—"}</dd>
                    <dt className="col-sm-5">Minimum payment</dt>
                    <dd className="col-sm-7">{formatCurrency(extraction.minimum_payment)}</dd>
                </dl>

                {extraction.items.length > 0 && (
                    <div className="mb-3">
                        <p className="form-label mb-1">Charges on this statement (for reference only)</p>
                        <ul className="list-group">
                            {/* index-keyed: same rationale as the warnings list above — a fixed,
                                immutable snapshot with no schema-provided id and no guaranteed-unique
                                name (e.g. two identical subscription charges). */}
                            {extraction.items.map((item, index) => (
                                <li key={index} className="list-group-item d-flex justify-content-between">
                                    <span>{item.name}</span>
                                    <span>{formatCurrency(item.amount)}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {confirmError && (
                    <div className="alert alert-danger" role="alert">{confirmError}</div>
                )}

                <div className="d-flex gap-2">
                    <button type="button" className="btn btn-primary" onClick={handleConfirm} disabled={isConfirming}>
                        {isConfirming ? "Updating…" : "Confirm balance update"}
                    </button>
                    <button type="button" className="btn btn-outline-secondary" onClick={onCancel} disabled={isConfirming}>
                        Cancel
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div>
            <p className="text-muted">
                Upload a photo or PDF of your statement or bill (jpg, png, heic, or a single-page PDF — 10MB max).
                We&apos;ll read it locally and suggest a balance update for you to review before saving.
            </p>
            <input
                type="file"
                className="form-control"
                accept={ACCEPTED_TYPES}
                onChange={handleFileChange}
                disabled={isScanning}
                aria-label="Statement file"
            />
            {scanError && (
                <div className="alert alert-danger mt-3" role="alert">
                    {scanError} Try a clearer photo, a different file, or{" "}
                    <button type="button" className="btn btn-link p-0 align-baseline" onClick={onCancel}>
                        cancel
                    </button>
                    .
                </div>
            )}
            <div className="mt-3 d-flex gap-2">
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleScan}
                    disabled={!selectedFile || isScanning}
                >
                    {isScanning ? "Scanning…" : "Scan statement"}
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={onCancel} disabled={isScanning}>
                    Cancel
                </button>
            </div>
        </div>
    )
}
