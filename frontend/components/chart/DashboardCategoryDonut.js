'use client'
import 'chart.js/auto'
import { Doughnut } from "react-chartjs-2"
import { useIsDarkTheme } from "@/hooks/useIsDarkTheme"

// Validated via the dataviz skill's validate_palette.js against this app's
// pink primary (#C93B7D) as the anchor hue -- passes lightness band, chroma
// floor, adjacent-pair CVD separation (>=8 target) and the normal-vision
// floor (>=15) in both modes. Capped at 7 real slots (an 8th+ series never
// gets a generated hue); "Other" always takes the fixed neutral gray below
// instead of an 8th hue.
const LIGHT_PALETTE = ["#C93B7D", "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#4a3aa7", "#008300"]
const DARK_PALETTE = ["#DD5A8E", "#3987e5", "#d95926", "#199e70", "#c98500", "#9085e9", "#008300"]
const OTHER_COLOR = "#898781"

const MIN_LABEL_GAP = 18

function formatCurrency(value) {
    return `$${Number(value ?? 0).toFixed(2)}`
}

function colorForIndex(label, index, isDark) {
    if (label === "Other") return OTHER_COLOR
    const palette = isDark ? DARK_PALETTE : LIGHT_PALETTE
    return palette[index % palette.length]
}

// Greedy top-to-bottom push: keeps leader-line labels on the same side from
// visually overlapping when two categories sit at similar angles.
function resolveLabelOverlap(entries) {
    const sorted = [...entries].sort((a, b) => a.labelY - b.labelY)
    for (let i = 1; i < sorted.length; i++) {
        const minY = sorted[i - 1].labelY + MIN_LABEL_GAP
        if (sorted[i].labelY < minY) sorted[i].labelY = minY
    }
    return sorted
}

const centerTotalPlugin = {
    id: "centerTotal",
    afterDraw(chart) {
        const { total, isDark } = chart.config.options.plugins.centerTotal ?? {}
        const meta = chart.getDatasetMeta(0)
        if (!meta.data.length) return
        const { x, y } = meta.data[0].getProps(["x", "y"], true)
        const { ctx } = chart

        ctx.save()
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"

        ctx.font = "600 12px system-ui, -apple-system, sans-serif"
        ctx.fillStyle = isDark ? "#b9b9b9" : "#8a8a8a"
        ctx.fillText("Total Spent", x, y - 12)

        ctx.font = "700 20px system-ui, -apple-system, sans-serif"
        ctx.fillStyle = isDark ? "#f5f5f5" : "#2b2b2b"
        ctx.fillText(formatCurrency(total), x, y + 11)

        ctx.restore()
    },
}

const leaderLineLabelsPlugin = {
    id: "leaderLineLabels",
    afterDraw(chart) {
        const { isDark } = chart.config.options.plugins.leaderLineLabels ?? {}
        const meta = chart.getDatasetMeta(0)
        const labels = chart.data.labels
        const values = chart.data.datasets[0].data
        const total = values.reduce((sum, value) => sum + Number(value), 0)
        if (!total || !meta.data.length) return

        const lineColor = isDark ? "#5c5c5c" : "#c7c7c7"
        const textColor = isDark ? "#e6e6e6" : "#3b3b3b"

        const raw = meta.data.map((arc, index) => {
            const { x, y, outerRadius, startAngle, endAngle } = arc.getProps(
                ["x", "y", "outerRadius", "startAngle", "endAngle"],
                true
            )
            const midAngle = (startAngle + endAngle) / 2
            const side = Math.cos(midAngle) >= 0 ? 1 : -1
            const bendRadius = outerRadius + 14
            return {
                side,
                anchorX: x + Math.cos(midAngle) * outerRadius,
                anchorY: y + Math.sin(midAngle) * outerRadius,
                bendX: x + Math.cos(midAngle) * bendRadius,
                bendY: y + Math.sin(midAngle) * bendRadius,
                labelX: x + side * (outerRadius + 34),
                labelY: y + Math.sin(midAngle) * bendRadius,
                text: formatCurrency(values[index]),
            }
        })

        const left = resolveLabelOverlap(raw.filter((entry) => entry.side < 0))
        const right = resolveLabelOverlap(raw.filter((entry) => entry.side >= 0))

        const { ctx } = chart
        ctx.save()
        ctx.font = "500 11px system-ui, -apple-system, sans-serif"
        ctx.textBaseline = "middle"
        ctx.strokeStyle = lineColor
        ctx.lineWidth = 1

        for (const entry of [...left, ...right]) {
            ctx.beginPath()
            ctx.moveTo(entry.anchorX, entry.anchorY)
            ctx.lineTo(entry.bendX, entry.bendY)
            ctx.lineTo(entry.labelX, entry.labelY)
            ctx.stroke()

            ctx.textAlign = entry.side >= 0 ? "left" : "right"
            ctx.fillStyle = textColor
            ctx.fillText(entry.text, entry.labelX + entry.side * 4, entry.labelY)
        }

        ctx.restore()
    },
}

export default function DashboardCategoryDonut({ labels, amounts }) {
    const isDark = useIsDarkTheme()
    const total = amounts.reduce((sum, amount) => sum + Number(amount), 0)

    const data = {
        labels,
        datasets: [
            {
                data: amounts,
                backgroundColor: labels.map((label, index) => colorForIndex(label, index, isDark)),
                borderWidth: 0,
            },
        ],
    }

    const options = {
        responsive: true,
        cutout: "62%",
        maintainAspectRatio: false,
        layout: { padding: { top: 30, bottom: 10, left: 90, right: 90 } },
        animation: { animateRotate: true, animateScale: true },
        plugins: {
            legend: {
                display: true,
                position: "bottom",
                labels: { color: isDark ? "#e6e6e6" : "#3b3b3b", boxWidth: 12, boxHeight: 12, padding: 12 },
            },
            tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${formatCurrency(ctx.raw)}` } },
            centerTotal: { total, isDark },
            leaderLineLabels: { isDark },
        },
    }

    return (
        <div style={{ height: 380, width: "100%" }} aria-label="Monthly expenses breakdown by category">
            <Doughnut
                data={data}
                options={options}
                plugins={[centerTotalPlugin, leaderLineLabelsPlugin]}
                id="dashboardCategoryDonut"
            />
        </div>
    )
}
