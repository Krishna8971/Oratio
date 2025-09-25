import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { useAuthStore } from "../store/auth";
import { signup as apiSignup } from "../api/client";
import "../styles/auth.css";

export default function Signup() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const { login } = useAuthStore();

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        
        // Basic validation
        if (!email || !password) {
            setError("Please fill in all fields");
            return;
        }
        
        if (!email.includes("@")) {
            setError("Please enter a valid email address");
            return;
        }
        
        if (password.length < 6) {
            setError("Password must be at least 6 characters long");
            return;
        }
        
        try {
            const token = await apiSignup(email, password);
            login(token);
            navigate("/review");
        } catch (e: any) {
            console.error("Signup error:", e);
            let errorMessage = "Signup failed";
            
            if (e?.response?.data) {
                if (typeof e.response.data === 'string') {
                    errorMessage = e.response.data;
                } else if (e.response.data.detail) {
                    if (typeof e.response.data.detail === 'string') {
                        errorMessage = e.response.data.detail;
                    } else if (Array.isArray(e.response.data.detail)) {
                        errorMessage = e.response.data.detail.map((err: any) => err.msg || err).join(', ');
                    }
                }
            } else if (e?.message) {
                errorMessage = e.message;
            }
            
            setError(errorMessage);
        }
    }

    return (
        <div className="auth-layout">
            <Header />
            <form className="auth-card" onSubmit={handleSubmit}>
                <h1>Sign Up</h1>
                {error && <div className="error">{error}</div>}
                <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
                <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
                <button type="submit" className="primary">Create account</button>
                <p>Already have an account? <Link to="/login">Log in</Link></p>
            </form>
        </div>
    );
}


