import React, { useState } from "react";
import { api, setAuthToken } from "../api";
import { useAuth } from "../AuthContext";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [erro, setErro] = useState("");
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErro("");
        try {
            const resp = await api.post("/login", { username, password });
            setAuthToken(resp.data.token);
            login(resp.data.token);
        } catch (err) {
            setErro("Usuário ou senha inválidos!");
        }
    };

    return (
        <div style={{ maxWidth: 300, margin: "100px auto", border: "1px solid #ccc", padding: 20, borderRadius: 8 }}>
            <h2>Painel Assistente IA</h2>
            <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Usuário" value={username} onChange={e => setUsername(e.target.value)} required /><br />
                <input type="password" placeholder="Senha" value={password} onChange={e => setPassword(e.target.value)} required /><br />
                <button type="submit" style={{ width: "100%" }}>Entrar</button>
            </form>
            {erro && <div style={{ color: "red", marginTop: 10 }}>{erro}</div>}
        </div>
    );
}
