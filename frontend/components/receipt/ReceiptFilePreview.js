"use client"
import { useEffect, useState } from "react"
import { createPortal } from "react-dom"

// Companion to ReceiptThumbnail.js for the scan-fallback quick-entry flow: the
// receipt File here hasn't been uploaded yet (that only happens on submit, see
// add-transaction/page.js's handleSubmit), so there's no transaction id to fetch
// an image by -- preview it straight from the local File as a data: URL instead
// of ReceiptThumbnail's authenticated GET. A blob: object URL would be simpler
// but this app's CSP only allows img-src 'self' data: -- no blob: -- so it reads
// as a data URL via FileReader instead of URL.createObjectURL.
export default function ReceiptFilePreview({ file }) {
    const [isOpen, setIsOpen] = useState(false)
    const [objectUrl, setObjectUrl] = useState(null)

    useEffect(() => {
        if (!file) {
            setObjectUrl(null)
            return undefined
        }
        let cancelled = false
        const reader = new FileReader()
        reader.onload = () => {
            if (!cancelled) setObjectUrl(reader.result)
        }
        reader.readAsDataURL(file)
        return () => {
            cancelled = true
        }
    }, [file])

    useEffect(() => {
        if (!isOpen) return undefined
        function handleKeyDown(event) {
            if (event.key === "Escape") setIsOpen(false)
        }
        document.addEventListener("keydown", handleKeyDown)
        return () => document.removeEventListener("keydown", handleKeyDown)
    }, [isOpen])

    if (!file || !objectUrl) return null

    const isPdf = file.type === "application/pdf"

    return (
        <>
            <button
                type="button"
                className="btn btn-sm btn-outline-secondary"
                onClick={() => setIsOpen(true)}
                aria-label="View uploaded receipt"
            >
                <i className="fi fi-rr-picture" /> View receipt
            </button>
            {isOpen &&
                createPortal(
                    <>
                        <div className="modal-backdrop fade show" onClick={() => setIsOpen(false)} />
                        <div
                            className="modal fade show"
                            style={{ display: "block" }}
                            role="dialog"
                            aria-modal="true"
                            aria-label="Receipt preview"
                        >
                            <div className="modal-dialog modal-dialog-centered modal-lg">
                                <div className="modal-content">
                                    <div className="modal-header">
                                        <h5 className="modal-title">Receipt preview</h5>
                                        <button type="button" className="btn-close" aria-label="Close" onClick={() => setIsOpen(false)} />
                                    </div>
                                    <div className="modal-body text-center">
                                        {isPdf ? (
                                            // <embed>/<iframe> would need object-src/frame-src, both 'none' under
                                            // this app's CSP -- offer a download instead of an inline PDF viewer.
                                            <a href={objectUrl} download={file.name || "receipt.pdf"} className="btn btn-outline-primary">
                                                <i className="fi fi-rr-download" /> Download {file.name || "receipt.pdf"}
                                            </a>
                                        ) : (
                                            <img src={objectUrl} alt="Uploaded receipt" className="img-fluid" />
                                        )}
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
