import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({
    baseURL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Attach Authorization header if a token is present
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("oratio_token");
    if (token) {
        config.headers = config.headers ?? {};
        config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
});

export async function healthcheck(): Promise<boolean> {
    try {
        const res = await api.get("/health");
        return res.status === 200 && res.data?.status === "ok";
    } catch {
        return false;
    }
}

// Auth API helpers
export async function login(email: string, password: string): Promise<string> {
    const { data } = await api.post<{ access_token: string }>("/auth/login", { email, password });
    return data.access_token;
}

export async function signup(email: string, password: string): Promise<string> {
    const { data } = await api.post<{ access_token: string }>("/auth/signup", { email, password });
    return data.access_token;
}

export async function getCurrentUser(): Promise<{ email: string; id: number }> {
    const { data } = await api.get<{ email: string; id: number }>("/auth/me");
    return data;
}


