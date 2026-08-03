'use client'
import { usePlatformView } from "@/hooks/usePlatformView"

const OPTIONS = [
    { mode: null, label: "Auto" },
    { mode: "mobile", label: "Mobile" },
    { mode: "pc", label: "PC" },
]

const VARIANT_CLASSES = {
    auth: { group: "auth-platform-toggle", option: "auth-platform-toggle-option" },
    menu: { group: "platform-view-options", option: "platform-view-option" },
}

// Presentational only -- the state itself lives wherever usePlatformView()
// is called from a component that's always mounted (Layout, for pages
// behind auth; this component owns it directly on the unauthenticated sign-in
// page). It must NOT own the hook itself here: this component is nested
// inside the profile dropdown's Menu.Items, which Headless UI unmounts
// while the dropdown is closed, so a hook living only here would reset to
// "no preference" (and clear the forced body class) on every page load
// until the dropdown was reopened.
export default function PlatformViewToggle({ variant = "menu", platformView, setPlatformView }) {
    const classes = VARIANT_CLASSES[variant]

    return (
        <div className={classes.group} role="group" aria-label="Platform view">
            {OPTIONS.map((option) => (
                <button
                    key={option.label}
                    type="button"
                    className={`${classes.option}${platformView === option.mode ? " is-active" : ""}`}
                    onClick={() => setPlatformView(option.mode)}
                >
                    {option.label}
                </button>
            ))}
        </div>
    )
}
