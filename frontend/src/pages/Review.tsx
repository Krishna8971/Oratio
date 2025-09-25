import { useEffect, useState } from "react";
import Header from "../components/Header";
import Chat from "../components/Chat";
import ChatHistory from "../components/ChatHistory";
import { type AnalyzeResponse } from "../api/analyze";
import { useAuthStore } from "../store/auth";
import { useNavigate } from "react-router-dom";
import "../styles/review.css";

export default function Review() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuthStore();
    const [history] = useState<{ id: string; title: string }[]>([]);
    const [result, setResult] = useState<AnalyzeResponse | null>(null);

    useEffect(() => {
        if (!isAuthenticated) navigate("/login");
    }, [isAuthenticated, navigate]);

    return (
        <div className="review-layout">
            <Header />
            <div className="review-content">
                <div className="left-pane">
                    <ChatHistory items={history} onSelect={() => {}} />
                    <Chat onResult={setResult} />
                </div>
                <div className="right-pane">
                    {result ? (
                        <div className="results">
                            <h2>Summary</h2>
                            <pre>{JSON.stringify(result.summary, null, 2)}</pre>
                            <h2>Sentences</h2>
                            <ul>
                                {result.sentences.map((s, idx) => (
                                    <li key={idx}>
                                        <div className="sentence">{s.sentence}</div>
                                        <div className="suggestion">{s.suggestion}</div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ) : (
                        <div className="placeholder">Start a review on the left.</div>
                    )}
                </div>
            </div>
        </div>
    );
}


