import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import logo from "../assets/logooratio.png";
import bgImage from "../assets/bgoratio.png";
import "../styles/home.css";
import { useAuthStore } from "../store/auth";

export default function Home() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuthStore();

    return (
        <div className="home-layout">
            <Header />
            <div className="home-content">
                <section className="home-left">
                    <div className="logo-section">
                        <img src={logo} alt="Oratio Logo" className="center-logo" />
                        <div className="logo">ORATIO</div>
                    </div>
                    <div className="cta-toggle">BIAS DETECTION</div>
                </section>
                <section className="home-right" style={{ backgroundImage: `url(${bgImage})` }}>
                    <h1>Spot the bias.<br/>Speak with clarity.</h1>
                    <div className="home-actions">
                        <button className="primary" onClick={() => navigate(isAuthenticated ? "/review" : "/login")}>Upload File</button>
                        <Link to={isAuthenticated ? "/review" : "/login"} className="secondary">Type Text</Link>
                    </div>
                </section>
            </div>
        </div>
    );
}


