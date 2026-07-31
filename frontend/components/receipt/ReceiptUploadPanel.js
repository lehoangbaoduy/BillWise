"use client"
import { useState } from "react"
import { ocrApi } from "@/lib/api"

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024
const ACCEPTED_TYPES = "image/jpeg,image/png,image/heic,image/heif,application/pdf"

export default function ReceiptUploadPanel({ onExtracted, onCancel }) {
    const [selectedFile, setSelectedFile] = useState(null)
    const [isScanning, setIsScanning] = useState(false)
    const [error, setError] = useState(null)

    function handleFileChange(event) {
        const file = event.target.files?.[0] ?? null
        setError(null)
        if (file && file.size > MAX_UPLOAD_BYTES) {
            setError("File exceeds the 10MB limit.")
            setSelectedFile(null)
            return
        }
        setSelectedFile(file)
    }

    async function handleScan() {
        if (!selectedFile) return
        setIsScanning(true)
        setError(null)
        try {
            const result = await ocrApi.scanReceipt(selectedFile)
            onExtracted(result)
        } catch (err) {
            setError(err.message || "Couldn't read this receipt.")
        } finally {
            setIsScanning(false)
        }
    }

    return (
        <div>
            <p className="text-muted">
                Upload a photo or PDF of your receipt (jpg, png, heic, or a single-page PDF — 10MB max). We&apos;ll
                read it locally and suggest the details below for you to review before saving.
            </p>
            <input
                type="file"
                className="form-control"
                accept={ACCEPTED_TYPES}
                onChange={handleFileChange}
                disabled={isScanning}
                aria-label="Receipt file"
            />
            {error && (
                <div className="alert alert-danger mt-3" role="alert">
                    {error} Try a clearer photo, a different file, or{" "}
                    <button type="button" className="btn btn-link p-0 align-baseline" onClick={onCancel}>
                        enter this transaction manually
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
                    {isScanning ? "Scanning…" : "Scan receipt"}
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={onCancel} disabled={isScanning}>
                    Enter manually instead
                </button>
            </div>
        </div>
    )
}
