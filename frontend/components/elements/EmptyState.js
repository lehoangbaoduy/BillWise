export default function EmptyState({ icon = "fi fi-rr-inbox", message, className = "" }) {
    return (
        <div className={`text-center text-muted py-4 ${className}`}>
            <i className={icon} style={{ fontSize: "1.75rem" }} />
            <p className="mb-0 mt-2">{message}</p>
        </div>
    )
}
