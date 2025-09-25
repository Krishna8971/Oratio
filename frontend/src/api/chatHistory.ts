import { api } from "./client";

export interface ChatHistoryItem {
    id: number;
    original_text: string;
    analysis_result: {
        original_text: string;
        summary: {
            biased_count: number;
            score: number;
        };
        sentences: Array<{
            sentence: string;
            biased_spans: Array<{
                text: string;
                start: number;
                end: number;
                type: string;
            }>;
            suggestion: string;
        }>;
    };
    created_at: string;
    provider_used: string;
}

export interface ChatHistoryResponse {
    history: ChatHistoryItem[];
    total_count: number;
}

export interface ChatHistoryParams {
    limit?: number;
    offset?: number;
}

/**
 * Get user's chat history with pagination
 */
export async function getChatHistory(params: ChatHistoryParams = {}): Promise<ChatHistoryResponse> {
    const { limit = 50, offset = 0 } = params;
    const { data } = await api.get<ChatHistoryResponse>("/chat/history", {
        params: { limit, offset }
    });
    return data;
}

/**
 * Delete a specific chat history item
 */
export async function deleteChatHistoryItem(historyId: number): Promise<{ message: string }> {
    const { data } = await api.delete<{ message: string }>(`/chat/history/${historyId}`);
    return data;
}

/**
 * Clear all chat history for the current user
 */
export async function clearChatHistory(): Promise<{ message: string }> {
    const { data } = await api.delete<{ message: string }>("/chat/history");
    return data;
}

/**
 * Get AI provider status
 */
export async function getAIStatus(): Promise<{
    current_provider: string;
    gemini_available: boolean;
    gemini_quota_exceeded: boolean;
    groq_available: boolean;
    fallback_enabled: boolean;
}> {
    const { data } = await api.get("/status");
    return data;
}
