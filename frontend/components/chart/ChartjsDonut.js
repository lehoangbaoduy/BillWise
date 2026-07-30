
'use client'
import 'chart.js/auto'
import { Doughnut } from "react-chartjs-2"

export default function ChartjsDonut() {
    const data = {
        datasets: [
            {
                data: [66, 34],
                backgroundColor: [
                    "rgba(47, 44, 216,1)",
                    // "rgba(47, 44, 216,0.5)",
                    "rgba(47, 44, 216,0.05)",
                ],
            },
        ],
        labels: ["Artwork Sold", "Artwork Cancel"],
    }

    const options = {
        responsive: false,
        cutout: 80,
        maintainAspectRatio: false,
        animation: {
            animateRotate: true,
            animateScale: true,
        },
        plugins: {
            legend: {
                display: false,
            }
        },
    }
    return (
        <><Doughnut data={data} height={200} options={options} id="chartjsDonut" /></>
    )
}
