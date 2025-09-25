import { api } from "./client";

export interface AnalyzeRequest {
    text: string;
}

export interface BiasedSpan {
    text: string;
    start: number;
    end: number;
    type: string;
}

export interface SentenceAnalysis {
    sentence: string;
    biased_spans: BiasedSpan[];
    suggestion: string;
}

export interface AnalyzeResponse {
    original_text: string;
    summary: Record<string, unknown>;
    sentences: SentenceAnalysis[];
}

export async function analyzeText(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
    const { data } = await api.post<AnalyzeResponse>("/analyze", payload);
    return data;
}


