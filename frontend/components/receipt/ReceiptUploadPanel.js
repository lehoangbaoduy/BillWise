"use client"
import { useEffect, useState } from "react"
import { ocrApi } from "@/lib/api"
import { usePlatformView } from "@/hooks/usePlatformView"

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024
const ACCEPTED_TYPES = "image/jpeg,image/png,image/heic,image/heif,application/pdf"
// Matches the app's existing mobile/PC layout breakpoint (see usePlatformView.js).
const MOBILE_BREAKPOINT_QUERY = "(max-width: 767px)"

export default function ReceiptUploadPanel({ onExtracted, onScanFailed, onCancel }) {
    const [selectedFile, setSelectedFile] = useState(null)
    const [isScanning, setIsScanning] = useState(false)
    const [error, setError] = useState(null)
    const { platformView } = usePlatformView()
    const [isNarrowViewport, setIsNarrowViewport] = useState(false)

    useEffect(() => {
        const mediaQuery = window.matchMedia(MOBILE_BREAKPOINT_QUERY)
        setIsNarrowViewport(mediaQuery.matches)
        const handleChange = (event) => setIsNarrowViewport(event.matches)
        mediaQuery.addEventListener("change", handleChange)
        return () => mediaQuery.removeEventListener("change", handleChange)
    }, [])

    // PRD v2 §7.1: native camera picker on mobile, not a custom viewfinder --
    // an explicit sidebar/bottom-nav override (platformView) wins over the
    // real viewport width; "Auto" (null) follows the actual width.
    const isMobile = platformView === "mobile" || (platformView === null && isNarrowViewport)

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
            onExtracted(result, selectedFile)
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
                capture={isMobile ? "environment" : undefined}
                onChange={handleFileChange}
                disabled={isScanning}
                aria-label="Receipt file"
            />
            {error && (
                <div className="alert alert-danger mt-3" role="alert">
                    {error} Try a clearer photo, a different file, or{" "}
                    <button
                        type="button"
                        className="btn btn-link p-0 align-baseline"
                        onClick={() => onScanFailed(selectedFile)}
                    >
                        enter the amount and merchant manually
                    </button>
                    {" "}— we&apos;ll keep the photo attached.
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
