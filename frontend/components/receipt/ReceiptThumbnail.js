"use client"
import { useEffect, useState } from "react"
import { createPortal } from "react-dom"
import { transactionsApi } from "@/lib/api"

// PRD v2 §7.2: Transaction History's thumbnail + modal for a retained
// receipt image. Fetched as a blob via the authenticated GET endpoint
// (never a public/presigned URL) rather than a plain <img src> -- see
// transactionsApi.receiptImageDataUrl's comment in lib/api.js.
export default function ReceiptThumbnail({ transaction }) {
    const [dataUrl, setDataUrl] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)

    function handleClose() {
        setDataUrl(null)
        setError(null)
    }

    useEffect(() => {
        if (!dataUrl) return
        function handleKeyDown(event) {
            if (event.key === "Escape") handleClose()
        }
        document.addEventListener("keydown", handleKeyDown)
        return () => document.removeEventListener("keydown", handleKeyDown)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [dataUrl])

    if (!transaction.receipt_image_key) {
        return <span className="text-muted">—</span>
    }

    async function handleOpen() {
        setError(null)
        setIsLoading(true)
        try {
            const url = await transactionsApi.receiptImageDataUrl(transaction.id)
            setDataUrl(url)
        } catch (err) {
            setError(err.message || "Couldn't load the receipt image.")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <>
            <button
                type="button"
                className="btn btn-sm btn-outline-secondary p-1"
                onClick={handleOpen}
                disabled={isLoading}
                aria-label={`View receipt image for ${transaction.merchant}`}
            >
                {isLoading ? <span className="spinner-border spinner-border-sm" /> : <i className="fi fi-rr-picture" />}
            </button>
            {error && <div className="text-danger small mt-1">{error}</div>}
            {dataUrl &&
                createPortal(
                    <>
                        <div className="modal-backdrop fade show" onClick={handleClose} />
                        <div
                            className="modal fade show"
                            style={{ display: "block" }}
                            role="dialog"
                            aria-modal="true"
                            aria-label={`Receipt for ${transaction.merchant}`}
                        >
                            <div className="modal-dialog modal-dialog-centered">
                                <div className="modal-content">
                                    <div className="modal-header">
                                        <h5 className="modal-title">
                                            {transaction.merchant} — {transaction.date}
                                        </h5>
                                        <button type="button" className="btn-close" aria-label="Close" onClick={handleClose} />
                                    </div>
                                    <div className="modal-body text-center">
                                        <img
                                            src={dataUrl}
                                            alt={`Receipt for ${transaction.merchant}`}
                                            className="img-fluid"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </>,
                    document.body
                )}
        </>
    )
}
