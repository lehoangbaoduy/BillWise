
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Blank() {

    return (
        <>
            <Layout breadcrumbTitle="title">
                <Link href="#">Create a Blank Page</Link>
            </Layout>
        </>
    )
}