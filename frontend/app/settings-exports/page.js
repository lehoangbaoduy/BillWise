'use client'
import { useState } from "react"
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import EmptyState from "@/components/elements/EmptyState"
import { useAuth } from "@/hooks/useAuth"
import { exportsApi } from "@/lib/api"

const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

function triggerDownload(link) {
    window.open(exportsApi.downloadUrl(link.download_url), "_blank", "noopener")
}

export default function SettingsExports() {
    const { user, isLoading: isAuthLoading } = useAuth()
    const isOwner = user?.role === "owner"

    const [month, setMonth] = useState(() => new Date().getMonth() + 1)
    const [year, setYear] = useState(() => new Date().getFullYear())
    const [pdfPassword, setPdfPassword] = useState("")
    const [error, setError] = useState(null)
    const [pendingAction, setPendingAction] = useState(null)

    async function handleCsvExport() {
        setPendingAction("csv")
        setError(null)
        try {
            const link = await exportsApi.transactionsCsv()
            triggerDownload(link)
        } catch (err) {
            setError(err.message)
        } finally {
            setPendingAction(null)
        }
    }

    async function handleXlsxExport() {
        setPendingAction("xlsx")
        setError(null)
        try {
            const link = await exportsApi.monthlyReportXlsx(month, year)
            triggerDownload(link)
        } catch (err) {
            setError(err.message)
        } finally {
            setPendingAction(null)
        }
    }

    async function handlePdfExport(event) {
        event.preventDefault()
        setPendingAction("pdf")
        setError(null)
        try {
            const link = await exportsApi.monthlyReportPdf(month, year, pdfPassword.trim() || null)
            triggerDownload(link)
        } catch (err) {
            setError(err.message)
        } finally {
            setPendingAction(null)
        }
    }

    if (isAuthLoading) return null

    if (!isOwner) {
        return (
            <Layout breadcrumbTitle="Exports">
                <div className="card">
                    <div className="card-body">
                        <EmptyState icon="fi fi-rr-lock" message="Only the household owner can export data." />
                    </div>
                </div>
            </Layout>
        )
    }

    return (
        <Layout breadcrumbTitle="Exports">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu />
                    {error && <div className="text-danger mb-3" role="alert">{error}</div>}

                    <div className="row">
                        <div className="col-xxl-4 col-xl-4 col-lg-6">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Transactions CSV</h4>
                                </div>
                                <div className="card-body">
                                    <p>Every transaction, one row per line item.</p>
                                    <button
                                        type="button"
                                        className="btn btn-success w-100"
                                        disabled={pendingAction === "csv"}
                                        onClick={handleCsvExport}
                                    >
                                        {pendingAction === "csv" ? "Generating…" : "Download CSV"}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="col-xxl-4 col-xl-4 col-lg-6">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Monthly Report (Excel)</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row g-2 mb-3">
                                        <div className="col-6">
                                            <label className="form-label" htmlFor="export-xlsx-month">Month</label>
                                            <select
                                                id="export-xlsx-month"
                                                className="form-select"
                                                value={month}
                                                onChange={(event) => setMonth(Number(event.target.value))}
                                            >
                                                {MONTH_NAMES.map((name, index) => (
                                                    <option key={name} value={index + 1}>{name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="col-6">
                                            <label className="form-label" htmlFor="export-xlsx-year">Year</label>
                                            <input
                                                id="export-xlsx-year"
                                                type="number"
                                                className="form-control"
                                                value={year}
                                                onChange={(event) => setYear(Number(event.target.value))}
                                            />
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        className="btn btn-success w-100"
                                        disabled={pendingAction === "xlsx"}
                                        onClick={handleXlsxExport}
                                    >
                                        {pendingAction === "xlsx" ? "Generating…" : "Download Excel Report"}
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="col-xxl-4 col-xl-4 col-lg-6">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Monthly Report (PDF)</h4>
                                </div>
                                <div className="card-body">
                                    <form onSubmit={handlePdfExport}>
                                        <div className="row g-2 mb-3">
                                            <div className="col-6">
                                                <label className="form-label" htmlFor="export-pdf-month">Month</label>
                                                <select
                                                    id="export-pdf-month"
                                                    className="form-select"
                                                    value={month}
                                                    onChange={(event) => setMonth(Number(event.target.value))}
                                                >
                                                    {MONTH_NAMES.map((name, index) => (
                                                        <option key={name} value={index + 1}>{name}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className="col-6">
                                                <label className="form-label" htmlFor="export-pdf-year">Year</label>
                                                <input
                                                    id="export-pdf-year"
                                                    type="number"
                                                    className="form-control"
                                                    value={year}
                                                    onChange={(event) => setYear(Number(event.target.value))}
                                                />
                                            </div>
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label" htmlFor="export-pdf-password">
                                                PDF password (optional)
                                            </label>
                                            <input
                                                id="export-pdf-password"
                                                type="password"
                                                className="form-control"
                                                placeholder="Leave blank for no password"
                                                value={pdfPassword}
                                                onChange={(event) => setPdfPassword(event.target.value)}
                                                minLength={4}
                                                maxLength={128}
                                            />
                                        </div>
                                        <button
                                            type="submit"
                                            className="btn btn-success w-100"
                                            disabled={pendingAction === "pdf"}
                                        >
                                            {pendingAction === "pdf" ? "Generating…" : "Download PDF Report"}
                                        </button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
