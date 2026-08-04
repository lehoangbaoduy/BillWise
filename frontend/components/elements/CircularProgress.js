'use client'
import { buildStyles, CircularProgressbar } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'

// Goals: low progress toward a target is the risk, so color gets *better* as
// value climbs. Budgets: high spend against a cap is the risk, so color gets
// *worse* as value climbs -- same component, inverted stop order.
const GOAL_COLOR_STOPS = [
    { max: 30, color: "#EF4444" },
    { max: 50, color: "#F97316" },
    { max: 70, color: "#EAB308" },
    { max: Infinity, color: "#51BB25" },
]

const BUDGET_COLOR_STOPS = [
    { max: 50, color: "#51BB25" },
    { max: 70, color: "#EAB308" },
    { max: 90, color: "#F97316" },
    { max: Infinity, color: "#EF4444" },
]

function resolveColor(value, variant) {
    const stops = variant === "budget" ? BUDGET_COLOR_STOPS : GOAL_COLOR_STOPS
    return (stops.find((stop) => value < stop.max) ?? stops[stops.length - 1]).color
}

export default function CircularProgress({ value, height, width, margin, variant = "goal" }) {
    const color = resolveColor(value, variant)
    return (
        <>
            <div style={{ width: `${width}px`, height: `${height}px`, margin: `${margin}` }}>
                <CircularProgressbar
                    value={value}
                    text={`${value}%`}
                    background
                    backgroundPadding={0}
                    styles={buildStyles({
                        backgroundColor: "transparent",
                        textColor: color,
                        pathColor: color,
                        trailColor: "#eee",
                        strokeLinecap: "butt"
                    })}
                />
            </div>
        </>
    )
}
