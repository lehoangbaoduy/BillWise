'use client'
import 'chart.js/auto'
import { Bar, Line } from "react-chartjs-2"

export default function DashboardSpendTrendChart({ labels, amounts, variant = "bar", height = 300 }) {
    const ChartComponent = variant === "line" ? Line : Bar
    const data = {
        labels,
        datasets: [
            {
                label: "Spending",
                data: amounts,
                backgroundColor: "#C93B7D",
                ...(variant === "line" && {
                    borderColor: "#C93B7D",
                    pointBackgroundColor: "#C93B7D",
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                }),
            },
        ],
    }

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
        },
        scales: {
            x: {
                grid: {
                    display: true,
                    drawBorder: false,
                    color: "rgba(0,0,0,0.05)",
                },
            },
            y: {
                grid: {
                    display: false,
                    drawBorder: false,
                },
                beginAtZero: true,
            },
        },
    }

    return (
        <div style={{ height, width: "100%" }} aria-label="Monthly spending trend across the year">
            <ChartComponent data={data} options={options} id="dashboardSpendTrendChart" />
        </div>
    )
}
