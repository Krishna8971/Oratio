import { useState, forwardRef, useImperativeHandle } from "react";
import { useChatHistory } from "../hooks/useChatHistory";
import { type ChatHistoryItem } from "../api/chatHistory";

interface ChatHistoryProps {
    onSelect: (item: ChatHistoryItem) => void;
    onRefresh?: () => void;
}

export interface ChatHistoryRef {
    refresh: () => void;
}

const ChatHistory = forwardRef<ChatHistoryRef, ChatHistoryProps>(({ onSelect, onRefresh }, ref) => {
    const { 
        history, 
        totalCount, 
        loading, 
        error, 
        hasMore, 
        loadMore, 
        refresh, 
        deleteItem, 
        clearAll 
    } = useChatHistory(20);
    
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [showConfirmClear, setShowConfirmClear] = useState(false);

    useImperativeHandle(ref, () => ({
        refresh: () => refresh()
    }));

    const handleDelete = async (id: number, event: React.MouseEvent) => {
        event.stopPropagation();
        setDeletingId(id);
        try {
            await deleteItem(id);
        } catch (err) {
            alert(`Failed to delete: ${err}`);
        } finally {
            setDeletingId(null);
        }
    };

    const handleClearAll = async () => {
        try {
            await clearAll();
            setShowConfirmClear(false);
            onRefresh?.();
        } catch (err) {
            alert(`Failed to clear history: ${err}`);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMins < 1) return "Just now";
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    const truncateText = (text: string, maxLength: number = 50) => {
        return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
    };

    return (
        <aside className="chat-history">
            <div className="chat-history-header">
                <h3>Chat History</h3>
                <div className="chat-history-actions">
                    <button 
                        className="refresh-btn" 
                        onClick={refresh}
                        disabled={loading}
                        title="Refresh"
                    >
                        ↻
                    </button>
                    {history.length > 0 && (
                        <button 
                            className="clear-btn" 
                            onClick={() => setShowConfirmClear(true)}
                            title="Clear all history"
                        >
                            🗑️
                        </button>
                    )}
                </div>
            </div>

            {showConfirmClear && (
                <div className="confirm-dialog">
                    <p>Clear all chat history?</p>
                    <div className="confirm-actions">
                        <button onClick={handleClearAll} className="confirm-yes">Yes</button>
                        <button onClick={() => setShowConfirmClear(false)} className="confirm-no">No</button>
                    </div>
                </div>
            )}

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={refresh}>Retry</button>
                </div>
            )}

            <div className="chat-history-content">
                {loading && history.length === 0 ? (
                    <div className="loading">Loading history...</div>
                ) : history.length === 0 ? (
                    <div className="empty-state">
                        <p>No chat history yet</p>
                        <p>Start analyzing text to see your history here</p>
                    </div>
                ) : (
                    <ul className="history-list">
                        {history.map((item) => (
                            <li key={item.id} className="history-item">
                                <button 
                                    className="history-item-content"
                                    onClick={() => onSelect(item)}
                                >
                                    <div className="history-item-text">
                                        {truncateText(item.original_text)}
                                    </div>
                                    <div className="history-item-meta">
                                        <span className="bias-score">
                                            Score: {item.analysis_result.summary.score}
                                        </span>
                                    </div>
                                </button>
                                <button 
                                    className="delete-item-btn"
                                    onClick={(e) => handleDelete(item.id, e)}
                                    disabled={deletingId === item.id}
                                    title="Delete this item"
                                >
                                    {deletingId === item.id ? "..." : "×"}
                                </button>
                            </li>
                        ))}
                    </ul>
                )}

                {hasMore && (
                    <button 
                        className="load-more-btn"
                        onClick={loadMore}
                        disabled={loading}
                    >
                        {loading ? "Loading..." : `Load more (${totalCount - history.length} remaining)`}
                    </button>
                )}
            </div>
        </aside>
    );
});

ChatHistory.displayName = 'ChatHistory';

export default ChatHistory;
