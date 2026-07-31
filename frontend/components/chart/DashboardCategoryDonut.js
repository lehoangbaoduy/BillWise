'use client'
import 'chart.js/auto'
import { Doughnut } from "react-chartjs-2"

const COLORS = [
    "rgba(47, 44, 216, 1)",
    "rgba(47, 44, 216, 0.75)",
    "rgba(47, 44, 216, 0.55)",
    "rgba(47, 44, 216, 0.35)",
    "rgba(47, 44, 216, 0.2)",
    "rgba(47, 44, 216, 0.1)",
]

export default function DashboardCategoryDonut({ labels, amounts }) {
    const data = {
        labels,
        datasets: [
            {
                data: amounts,
                backgroundColor: labels.map((_, index) => COLORS[index % COLORS.length]),
            },
        ],
    }

    const options = {
        responsive: true,
        cutout: 80,
        maintainAspectRatio: false,
        animation: {
            animateRotate: true,
            animateScale: true,
        },
        plugins: {
            legend: {
                display: true,
                position: "bottom",
            },
        },
    }

    return (
        <div style={{ height: 220, width: "100%" }} aria-label="Monthly expenses breakdown by category">
            <Doughnut data={data} options={options} id="dashboardCategoryDonut" />
        </div>
    )
}
