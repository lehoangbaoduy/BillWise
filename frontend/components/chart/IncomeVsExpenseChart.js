'use client'
import 'chart.js/auto'
import { Bar } from "react-chartjs-2"

export default function IncomeVsExpenseChart({ labels, income, expenses }) {
    const data = {
        labels,
        datasets: [
            { label: "Income", data: income, backgroundColor: "#12A347" },
            { label: "Expenses", data: expenses, backgroundColor: "#DC2626" },
        ],
    }

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: true, position: "bottom" },
        },
        scales: {
            x: { grid: { display: true, drawBorder: false, color: "rgba(0,0,0,0.05)" } },
            y: { grid: { display: false, drawBorder: false }, beginAtZero: true },
        },
    }

    return (
        <div style={{ height: 320, width: "100%" }} aria-label="Income versus expenses by month">
            <Bar data={data} options={options} id="incomeVsExpenseChart" />
        </div>
    )
}
