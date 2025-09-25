import { useState } from "react";
import { analyzeText, type AnalyzeResponse } from "../api/analyze";
import MessageInput from "./MessageInput";

interface ChatProps {
    onResult: (result: AnalyzeResponse) => void;
}

export default function Chat({ onResult }: ChatProps) {
    const [messages, setMessages] = useState<{ role: "user" | "system"; content: string }[]>([]);
    const [loading, setLoading] = useState(false);

    async function handleSend(text: string) {
        const newMessages: { role: "user" | "system"; content: string }[] = [...messages, { role: "user", content: text }];
        setMessages(newMessages);
        setLoading(true);
        try {
            const res = await analyzeText({ text });
            onResult(res);
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


