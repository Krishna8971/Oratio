import { useState, useEffect, useCallback } from "react";
import { 
    getChatHistory, 
    deleteChatHistoryItem, 
    clearChatHistory, 
    type ChatHistoryItem,
    type ChatHistoryResponse 
} from "../api/chatHistory";

export interface UseChatHistoryReturn {
    history: ChatHistoryItem[];
    totalCount: number;
    loading: boolean;
    error: string | null;
    hasMore: boolean;
    loadMore: () => void;
    refresh: () => void;
    deleteItem: (id: number) => Promise<void>;
    clearAll: () => Promise<void>;
}

export function useChatHistory(initialLimit: number = 20): UseChatHistoryReturn {
    const [history, setHistory] = useState<ChatHistoryItem[]>([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [offset, setOffset] = useState(0);
    const [limit] = useState(initialLimit);

    const loadHistory = useCallback(async (resetOffset: boolean = false) => {
        setLoading(true);
        setError(null);
        
        try {
            const currentOffset = resetOffset ? 0 : offset;
            const response: ChatHistoryResponse = await getChatHistory({
                limit,
                offset: currentOffset
            });

            if (resetOffset) {
                setHistory(response.history);
                setOffset(response.history.length);
            } else {
                setHistory(prev => [...prev, ...response.history]);
                setOffset(prev => prev + response.history.length);
            }
            
            setTotalCount(response.total_count);
        } catch (err: any) {
            console.error("Failed to load chat history:", err);
            setError(err.response?.data?.detail || err.message || "Failed to load chat history");
        } finally {
            setLoading(false);
        }
    }, [limit, offset]);

    const loadMore = useCallback(() => {
        if (!loading && history.length < totalCount) {
            loadHistory(false);
        }
    }, [loading, history.length, totalCount, loadHistory]);

    const refresh = useCallback(() => {
        setOffset(0);
        loadHistory(true);
    }, [loadHistory]);

    const deleteItem = useCallback(async (id: number) => {
        try {
            await deleteChatHistoryItem(id);
            setHistory(prev => prev.filter(item => item.id !== id));
            setTotalCount(prev => prev - 1);
        } catch (err: any) {
            console.error("Failed to delete chat history item:", err);
            throw new Error(err.response?.data?.detail || err.message || "Failed to delete item");
        }
    }, []);

    const clearAll = useCallback(async () => {
        try {
            await clearChatHistory();
            setHistory([]);
            setTotalCount(0);
            setOffset(0);
        } catch (err: any) {
            console.error("Failed to clear chat history:", err);
            throw new Error(err.response?.data?.detail || err.message || "Failed to clear history");
        }
    }, []);

    // Load initial history
    useEffect(() => {
        loadHistory(true);
    }, []);

    const hasMore = history.length < totalCount;

    return {
        history,
        totalCount,
        loading,
        error,
        hasMore,
        loadMore,
        refresh,
        deleteItem,
        clearAll
    };
}
