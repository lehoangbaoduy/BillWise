"use client"

export default function AuthField({ id, label, action, ...inputProps }) {
    return (
        <div className="auth-field">
            <div className="auth-field-label-row">
                <label htmlFor={id}>{label}</label>
                {action}
            </div>
            <input id={id} {...inputProps} />
        </div>
    )
}
