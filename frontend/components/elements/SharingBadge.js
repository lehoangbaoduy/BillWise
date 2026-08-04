// Icon-only by default (a lock/unlock glyph reads fine at list-row density);
// pass showText for contexts like Transaction History where the row already
// has several icon-bearing columns and a text label disambiguates faster.
export default function SharingBadge({ isShared, showText = false }) {
    return (
        <span
            className={`badge d-inline-flex align-items-center gap-1 ${isShared ? "bg-success" : "bg-danger"}`}
            title={isShared ? "Shared with partner" : "Private -- visible only to you"}
        >
            <i className={isShared ? "fi fi-rr-unlock" : "fi fi-rr-lock"} />
            {showText && (isShared ? "Shared" : "Private")}
        </span>
    )
}
