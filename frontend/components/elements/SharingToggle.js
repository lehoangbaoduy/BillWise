// Sliding pill switch for the Private/Shared model. The track's background
// color is the status readout (red = private, green = shared) and a white
// thumb slides to the corresponding side, with the state label sitting in
// the track next to it -- so it reads as an actual toggle, not a badge.
const TRACK_WIDTH = 94
const TRACK_HEIGHT = 30
const THUMB_SIZE = 24
const THUMB_INSET = 3

export default function SharingToggle({ id, isShared, onChange, disabled = false, hint, compact = false }) {
    const thumbOffset = isShared ? TRACK_WIDTH - THUMB_SIZE - THUMB_INSET : THUMB_INSET

    return (
        // display: flex on the wrapper (instead of the button's default
        // inline-block) avoids the inline-formatting-context baseline gap
        // that otherwise leaves the button a few px taller than its box,
        // which throws off align-items: center in the parent title row.
        <div className={`sharing-toggle d-flex${compact ? "" : " mb-3"}`}>
            <button
                id={id}
                type="button"
                role="switch"
                aria-checked={isShared}
                disabled={disabled}
                onClick={() => onChange(!isShared)}
                title={hint}
                className="p-0 border-0"
                style={{
                    position: "relative",
                    width: TRACK_WIDTH,
                    height: TRACK_HEIGHT,
                    borderRadius: TRACK_HEIGHT / 2,
                    backgroundColor: isShared ? "var(--bs-success)" : "var(--bs-danger)",
                    transition: "background-color 0.2s ease",
                    cursor: disabled ? "not-allowed" : "pointer",
                    opacity: disabled ? 0.55 : 1,
                    flexShrink: 0,
                }}
            >
                <span
                    style={{
                        position: "absolute",
                        inset: 0,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: isShared ? "flex-start" : "flex-end",
                        padding: "0 9px",
                        color: "#fff",
                        fontSize: "0.68rem",
                        fontWeight: 700,
                        letterSpacing: "0.02em",
                        pointerEvents: "none",
                    }}
                >
                    {isShared ? "Shared" : "Private"}
                </span>
                <span
                    style={{
                        position: "absolute",
                        top: THUMB_INSET,
                        left: thumbOffset,
                        width: THUMB_SIZE,
                        height: THUMB_SIZE,
                        borderRadius: "50%",
                        backgroundColor: "#fff",
                        boxShadow: "0 1px 3px rgba(0,0,0,0.35)",
                        transition: "left 0.2s ease",
                    }}
                />
            </button>
        </div>
    )
}
