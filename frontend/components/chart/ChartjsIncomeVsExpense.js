
'use client'
import 'chart.js/auto'
import { Bar } from "react-chartjs-2"

export default function chartjsIncomeVsExpense() {
    const data = {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"],
        datasets: [{
            label: 'a',
            data: [5, 6, 4.5, 5.5, 3, 6, 4.5, 6, 8, 3],
            backgroundColor: 'rgba(47, 44, 216,1)',
        },
        {
            label: 'b',
            data: [4, 5, 3.5, 4.5, 2, 5, 3.5, 5, 7, 2],
            backgroundColor: 'rgba(47, 44, 216,0.2)',
        }]
    }

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            }
        },
        scales: {
            x: {
                grid: {
                    display: true,
                    drawBorder: false,
                    color: "rgba(0,0,0,0.05)"
                }
            },
            y: {
                grid: {
                    display: false,
                    drawBorder: false,
                }
            },
        },
    }
    return (
        <><Bar data={data} height={300} options={options} id="chartjsIncomeVsExpense" /></>
    )
}
