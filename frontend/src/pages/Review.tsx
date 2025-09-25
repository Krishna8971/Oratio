import { useEffect, useState, useRef } from "react";
import Header from "../components/Header";
import Chat from "../components/Chat";
import ChatHistory, { type ChatHistoryRef } from "../components/ChatHistory";
import { type AnalyzeResponse } from "../api/analyze";
import { type ChatHistoryItem } from "../api/chatHistory";
import { useAuthStore } from "../store/auth";
import { useNavigate } from "react-router-dom";
import "../styles/review.css";

export default function Review() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuthStore();
    const [result, setResult] = useState<AnalyzeResponse | null>(null);
    const [selectedHistoryItem, setSelectedHistoryItem] = useState<ChatHistoryItem | null>(null);
    const historyRefreshRef = useRef<ChatHistoryRef>(null);

    useEffect(() => {
        if (!isAuthenticated) navigate("/login");
    }, [isAuthenticated, navigate]);

    const handleHistorySelect = (item: ChatHistoryItem) => {
        setSelectedHistoryItem(item);
        setResult(item.analysis_result);
    };

    const handleAnalysisComplete = () => {
        // Refresh chat history when new analysis is completed
        historyRefreshRef.current?.refresh();
    };

    const handleHistoryRefresh = () => {
        // Clear selected history item when refreshing
        setSelectedHistoryItem(null);
        setResult(null);
    };

    return (
        <div className="review-layout">
            <Header />
            <div className="review-content">
                <div className="left-pane">
                    <ChatHistory 
                        onSelect={handleHistorySelect}
                        onRefresh={handleHistoryRefresh}
                        ref={historyRefreshRef}
                    />
                    <Chat 
                        onResult={setResult}
                        onAnalysisComplete={handleAnalysisComplete}
                    />
                </div>
                <div className="right-pane">
                    {result ? (
                        <div className="results">
                            <div className="results-header">
                                <h2>Analysis Results</h2>
                            </div>
                            
                            <div className="summary-section">
                                <h3>Summary</h3>
                                <div className="summary-stats">
                                    <div className="stat">
                                        <span className="stat-label">Bias Score:</span>
                                        <span className={`stat-value ${result.summary.score > 0.5 ? 'high' : result.summary.score > 0.2 ? 'medium' : 'low'}`}>
                                            {result.summary.score}
                                        </span>
                                    </div>
                                    <div className="stat">
                                        <span className="stat-label">Biased Elements:</span>
                                        <span className="stat-value">{result.summary.biased_count}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="sentences-section">
                                <h3>Sentence Analysis</h3>
                                <div className="sentences-list">
                                    {result.sentences.map((sentence, idx) => (
                                        <div key={idx} className="sentence-item">
                                            <div className="sentence-text">
                                                {sentence.sentence}
                                            </div>
                                            {sentence.biased_spans.length > 0 && (
                                                <div className="biased-spans">
                                                    <strong>Biased elements:</strong>
                                                    {sentence.biased_spans.map((span, spanIdx) => (
                                                        <span key={spanIdx} className="biased-span">
                                                            "{span.text}" ({span.type})
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                            {sentence.suggestion !== sentence.sentence && (
                                                <div className="suggestion">
                                                    <strong>Suggestion:</strong> {sentence.suggestion}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="placeholder">
                            <h3>Welcome to Oratio</h3>
                            <p>Start analyzing text for bias by typing in the chat on the left, or select an item from your chat history.</p>
                            <div className="placeholder-features">
                                <div className="feature">
                                    <strong>🤖 AI-Powered Analysis</strong>
                                    <p>Uses advanced AI to detect various types of bias</p>
                                </div>
                                <div className="feature">
                                    <strong>📚 Chat History</strong>
                                    <p>All your analyses are automatically saved</p>
                                </div>
                                <div className="feature">
                                    <strong>🔄 Fallback System</strong>
                                    <p>Automatically switches between AI providers for reliability</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}


