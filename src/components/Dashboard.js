import React, { useEffect, useState } from "react";
import { api, setAuthToken } from "../api";
import { useAuth } from "../AuthContext";

export default function Dashboard() {
    const { token, logout } = useAuth();
    const [status, setStatus] = useState({ assistente_rodando: false, cpu: 0, mem: 0 });
    const [loading, setLoading] = useState(false);
    const [mensagem, setMensagem] = useState("");

    useEffect(() => {
        setAuthToken(token);
        atualizarStatus();
        // Opcional: atualizar status periodicamente
        const interval = setInterval(atualizarStatus, 5000);
        return () => clearInterval(interval);
    }, [token]);

    const atualizarStatus = async () => {
        try {
            const resp = await api.get("/status");
            setStatus(resp.data);
        } catch (err) {
            setStatus({ assistente_rodando: false, cpu: 0, mem: 0 });
        }
    };

    const acao = async (rota, mensagemSucesso) => {
        setLoading(true);
        setMensagem("");
        try {
            await api.post(rota);
            setMensagem(mensagemSucesso);
            atualizarStatus();
        } catch {
            setMensagem("Falha ao executar ação.");
        }
        setLoading(false);
    };

    return (
        <div style={{ maxWidth: 600, margin: "40px auto", border: "1px solid #ccc", borderRadius: 10, padding: 20 }}>
            <h2>Painel de Controle</h2>
            <div>
                <b>Status do assistente:</b>{" "}
                <span style={{ color: status.assistente_rodando ? "green" : "red" }}>
          {status.assistente_rodando ? "Rodando" : "Parado"}
        </span>
                <br />
                <b>CPU:</b> {status.cpu} % &nbsp; <b>RAM:</b> {status.mem} %
            </div>
            <br />
            <button onClick={() => acao("/start_assistente", "Assistente iniciado!")}>Iniciar Assistente</button>
            <button onClick={() => acao("/stop_assistente", "Assistente parado!")} style={{ marginLeft: 10 }}>
                Parar Assistente
            </button>
            <br /><br />
            <button onClick={() => acao("/extrair_chamados", "Extração de chamados iniciada!")}>Extrair Chamados</button>
            <button onClick={() => acao("/indexar_arquivos", "Indexação de arquivos iniciada!")} style={{ marginLeft: 10 }}>
                Indexar Arquivos
            </button>
            <button onClick={() => acao("/indexar_conversas", "Indexação de conversas iniciada!")} style={{ marginLeft: 10 }}>
                Indexar Conversas
            </button>
            <br /><br />
            <button onClick={() => acao("/limpar_chromadb", "ChromaDB em limpeza!")} style={{ backgroundColor: "#e77" }}>
                Limpar ChromaDB
            </button>
            <br /><br />
            <button onClick={logout}>Logout</button>
            {mensagem && <div style={{ color: "blue", marginTop: 15 }}>{mensagem}</div>}
        </div>
    );
}
