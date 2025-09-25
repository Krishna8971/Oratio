import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import logo from "../assets/logooratio.png";
import "../styles/global.css";

export default function Header() {
    const navigate = useNavigate();
    const { isAuthenticated, logout } = useAuthStore();

    return (
        <header className="header">
            <div className="header-left">
                <Link to="/" className="brand">
                    <img src={logo} alt="Oratio Logo" className="brand-logo" />
                    ORATIO
                </Link>
            </div>
            <nav className="header-right">
                {isAuthenticated ? (
                    <>
                        <Link to="/review" className="nav-link">Review</Link>
                        <button className="nav-button" onClick={() => { logout(); navigate("/"); }}>Logout</button>
                    </>
                ) : (
                    <>
                        <Link to="/login" className="nav-link">Login</Link>
                        <Link to="/signup" className="nav-link">Sign Up</Link>
                    </>
                )}
            </nav>
        </header>
    );
}
