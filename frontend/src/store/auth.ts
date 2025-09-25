import { create } from "zustand";

interface User {
    email: string;
    id: number;
}

interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: User | null;
    login: (token: string) => void;
    logout: () => void;
    setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    isAuthenticated: !!localStorage.getItem("oratio_token"),
    token: localStorage.getItem("oratio_token"),
    user: null,
    login: (token: string) => {
        localStorage.setItem("oratio_token", token);
        set({ isAuthenticated: true, token });
    },
    logout: () => {
        localStorage.removeItem("oratio_token");
        set({ isAuthenticated: false, token: null, user: null });
    },
    setUser: (user: User) => {
        set({ user });
    },
}));


