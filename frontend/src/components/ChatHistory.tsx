interface ChatHistoryProps {
    items: { id: string; title: string }[];
    onSelect: (id: string) => void;
}

export default function ChatHistory({ items, onSelect }: ChatHistoryProps) {
    return (
        <aside className="chat-history">
            <div className="chat-history-header">History</div>
            <ul>
                {items.map((i) => (
                    <li key={i.id}>
                        <button className="history-item" onClick={() => onSelect(i.id)}>{i.title}</button>
                    </li>
                ))}
            </ul>
        </aside>
    );
}
