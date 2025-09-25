import { Route, Routes, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Review from "./pages/Review";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import { useAuthStore } from "./store/auth";

function ProtectedRoute({ children }: { children: React.ReactElement }) {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    if (!isAuthenticated) return <Navigate to="/login" replace />;
    return children;
}

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/review" element={<ProtectedRoute><Review /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

// Removed Vite starter demo code that re-declared App
