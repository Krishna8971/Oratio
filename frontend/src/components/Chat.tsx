import { useState } from "react";
import { analyzeText, type AnalyzeResponse } from "../api/analyze";
import MessageInput from "./MessageInput";

interface ChatProps {
    onResult: (result: AnalyzeResponse) => void;
}

export default function Chat({ onResult }: ChatProps) {
    const [messages, setMessages] = useState<{ role: "user" | "system"; content: string }[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleSend(text: string) {
        const newMessages: { role: "user" | "system"; content: string }[] = [...messages, { role: "user", content: text }];
        setMessages(newMessages);
        setLoading(true);
        setError(null);
        
        try {
            const res = await analyzeText({ text });
            onResult(res);
        } catch (e: any) {
            console.error("Analysis error:", e);
            let errorMessage = "Analysis failed";
            
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
            setMessages(prev => [...prev, { role: "system", content: `Error: ${errorMessage}` }]);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="chat">
            <div className="chat-messages">
                {messages.map((m, idx) => (
                    <div key={idx} className={`chat-message ${m.role}`}>{m.content}</div>
                ))}
                {loading && <div className="chat-message system">Analyzing…</div>}
            </div>
            <MessageInput onSend={handleSend} />
        </div>
    );
}
