'use client'
import 'chart.js/auto'
import { Bar } from "react-chartjs-2"

export default function DashboardSpendTrendChart({ labels, amounts }) {
    const data = {
        labels,
        datasets: [
            {
                label: "Spending",
                data: amounts,
                backgroundColor: "rgba(47, 44, 216, 1)",
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
        <div style={{ height: 300, width: "100%" }} aria-label="Monthly spending trend across the year">
            <Bar data={data} options={options} id="dashboardSpendTrendChart" />
        </div>
    )
}
