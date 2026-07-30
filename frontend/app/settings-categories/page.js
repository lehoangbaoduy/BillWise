
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import Link from "next/link"
export default function SettingsCategories() {

    return (
        <>
            <Layout breadcrumbTitle="Categories">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu/>
                        <div className="row">
                            <div className="col-xxl-4 col-xl-4 col-lg-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Create a new categories</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="create-new-category">
                                            <form className="row">
                                                <div className="mb-3 col-12">
                                                    <label className="form-label">Name </label>
                                                    <input type="text" className="form-control" placeholder="category name" />
                                                </div>
                                                <div className="mb-3 col-12">
                                                    <label className="form-label">Type </label>
                                                    <select id="inputState" className="form-select">
                                                        <option selected>Choose...</option>
                                                        <option>Income</option>
                                                        <option>Expenses</option>
                                                    </select>
                                                </div>
                                                <div className="mb-3 col-6">
                                                    <label className="form-label">Icon </label>
                                                    <select id="inputState" className="form-select">
                                                        <option selected>Choose...</option>
                                                        <option>...</option>
                                                    </select>
                                                </div>
                                                <div className="mb-3 col-6">
                                                    <label className="form-label">Color </label>
                                                    <select id="inputState" className="form-select">
                                                        <option selected>Choose...</option>
                                                        <option>...</option>
                                                    </select>
                                                </div>
                                                <div className="col-12">
                                                    <button className="btn btn-success w-100">Create new category</button>
                                                </div>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xxl-8 col-xl-8 col-lg-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Income Categories</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="category-type">
                                            <ul>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-purple-500 fi fi-rr-usd-circle" /> Salary</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-red-500 fi fi-rr-store-alt" /> Business</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-orange-500 fi fi-rr-life-ring" /> Client</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-amber-500 fi fi-rr-gift" /> Gifts</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-yellow-500 fi fi-bs-user-shield" /> Insurance
                                                        </span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-lime-500 fi fi-rr-sack-dollar" /> Loan</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-green-500 fi fi-rr-add-document" /> Other</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Expense Categories</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="category-type">
                                            <ul>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-emerald-500 fi fi-rr-barber-shop" />
                                                            Beauty</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-teal-500 fi fi-rr-receipt" /> Bills &amp;
                                                            Fees</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-cyan-500 fi fi-rr-car-side" /> Car</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-sky-500 fi fi-rr-graduation-cap" />
                                                            Education</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-blue-500 fi fi-rr-clapperboard-play" />
                                                            Entertainment</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-indigo-500 fi fi-sr-family" /> Family</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-violet-500 fi fi-rr-hamburger-soda" /> Food &amp;
                                                            Drink</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-purple-500 fi fi-rr-money-bills-simple" />
                                                            Salary</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-fuchsia-500 fi fi-rs-pineapple" />
                                                            Groceries</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-pink-500 fi fi-rr-user-md" /> Healthcare</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-purple-500 fi fi-rr-home" /> Home</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-rose-500 fi fi-rs-shopping-bag" />
                                                            Shopping</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-orange-500 fi fi-br-running" /> Sports </span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-emerald-500 fi fi-rr-bowling" /> Hobbies</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-teal-500 fi fi-rr-plane" /> Travel</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-cyan-500 fi fi-rr-bus" />
                                                            Transport</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                                <li>
                                                    <div className="left-category">
                                                        <span className="drag-icon"><i className="fi fi-ss-grip-lines" /></span>
                                                        <span className="category-icon"><i className="bg-indigo-500 fi fi-rr-briefcase" /> Work</span>
                                                    </div>
                                                    <div className="right-category">
                                                        <span><i className="fi fi-rs-pencil" /></span>
                                                        <span><i className="fi fi-rr-eye" /></span>
                                                        <span><i className="fi fi-rr-trash" /></span>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}