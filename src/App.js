import React from "react";
import { AuthProvider, useAuth } from "./AuthContext";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

function AppContent() {
    const { token } = useAuth();
    return token ? <Dashboard /> : <Login />;
}

function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}

export default App;
