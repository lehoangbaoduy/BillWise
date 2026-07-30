'use client'
import { buildStyles, CircularProgressbar } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'


export default function CircularProgress({ value, height, width, margin }) {
    // const value = 80
    // const height = 80
    // const width = 80
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
                        textColor: "#51BB25",
                        pathColor: "#51BB25",
                        trailColor: "#eee",
                        strokeLinecap: "butt"
                    })}
                />
            </div>
        </>
    )
}