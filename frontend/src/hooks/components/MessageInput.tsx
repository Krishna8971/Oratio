import { useState } from "react";

export default function MessageInput({ onSend }: { onSend: (text: string) => void }) {
    const [text, setText] = useState("");

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!text.trim()) return;
        onSend(text.trim());
        setText("");
    }

    return (
        <form className="message-input" onSubmit={handleSubmit}>
            <input
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type text to analyze..."
            />
            <button type="submit">Analyze</button>
        </form>
    );
}


