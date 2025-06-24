import React, { useEffect, useState } from "react";
import { api, setAuthToken } from "@/api/apiClient";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { LogOut, Power, PowerOff, DatabaseZap, FileText, MessageSquare, RefreshCw, Trash2 } from "lucide-react";

// Componente para cada card de ação
const ActionCard = ({ title, description, children }) => (
    <Card>
        <CardHeader>
            <CardTitle>{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent className="space-y-2">
            {children}
        </CardContent>
    </Card>
);

export default function DashboardPage() {
    const { token, logout } = useAuth();
    const [status, setStatus] = useState({ assistente_rodando: false, cpu: 0, mem: 0 });
    const [loading, setLoading] = useState({}); // Objeto para rastrear loading por ação
    const [mensagem, setMensagem] = useState({ type: "", text: "" }); // type: "success" | "error"

    const handleLogout = () => {
        logout();
        // Opcional: redirecionar para a página de login ou limpar o token da API
        setAuthToken(null);
    };

    useEffect(() => {
        if (token) {
            setAuthToken(token);
            atualizarStatus();
            const interval = setInterval(atualizarStatus, 15000); // Aumentado para 15s
            return () => clearInterval(interval);
        }
    }, [token]);

    const atualizarStatus = async () => {
        try {
            const resp = await api.get("/status");
            setStatus(resp.data);
        } catch (err) {
            console.error("Erro ao atualizar status:", err);
            setStatus({ assistente_rodando: false, cpu: 0, mem: 0 });
            // Poderia setar uma mensagem de erro aqui se a falha for crítica
        }
    };

    const acao = async (actionName, rota, mensagemSucesso, options = {}) => {
        setLoading(prev => ({ ...prev, [actionName]: true }));
        setMensagem({ type: "", text: "" });
        try {
            await api.post(rota, options.body || {});
            setMensagem({ type: "success", text: mensagemSucesso });
            atualizarStatus();
        } catch (err) {
            console.error(`Erro ao executar ${actionName}:`, err);
            setMensagem({ type: "error", text: `Falha ao executar ação: ${actionName}.` });
        }
        setLoading(prev => ({ ...prev, [actionName]: false }));
    };

    return (
        <div className="min-h-screen bg-slate-100 p-4 md:p-8">
            <header className="mb-8 flex justify-between items-center">
                <h1 className="text-3xl font-bold text-slate-800">Painel de Controle</h1>
                <Button variant="outline" onClick={handleLogout} disabled={loading.logout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                </Button>
            </header>

            {mensagem.text && (
                <Alert variant={mensagem.type === "error" ? "destructive" : "default"} className="mb-6">
                    <AlertTitle>{mensagem.type === "error" ? "Erro!" : "Sucesso!"}</AlertTitle>
                    <AlertDescription>{mensagem.text}</AlertDescription>
                </Alert>
            )}

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Status Card */}
                <Card className="lg:col-span-1">
                    <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                            Status do Sistema
                            <Button variant="ghost" size="sm" onClick={atualizarStatus} disabled={loading.statusRefresh}>
                                <RefreshCw className={`h-4 w-4 ${loading.statusRefresh ? 'animate-spin' : ''}`} />
                            </Button>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="font-medium">Assistente IA:</span>
                            <Badge variant={status.assistente_rodando ? "default" : "destructive"} className="text-sm">
                                {status.assistente_rodando ? "Rodando" : "Parado"}
                            </Badge>
                        </div>
                        <div>
                            <div className="flex justify-between mb-1">
                                <span className="text-sm font-medium">Uso de CPU:</span>
                                <span className="text-sm">{status.cpu?.toFixed(1)}%</span>
                            </div>
                            <Progress value={status.cpu} className="h-2" />
                        </div>
                        <div>
                            <div className="flex justify-between mb-1">
                                <span className="text-sm font-medium">Uso de RAM:</span>
                                <span className="text-sm">{status.mem?.toFixed(1)}%</span>
                            </div>
                            <Progress value={status.mem} className="h-2" />
                        </div>
                    </CardContent>
                </Card>

                {/* Ações do Assistente */}
                <ActionCard title="Controle do Assistente IA">
                    <Button onClick={() => acao("start_assistente", "/start_assistente", "Assistente IA iniciado com sucesso!")} disabled={loading.start_assistente || status.assistente_rodando} className="w-full justify-start">
                        <Power className="mr-2 h-4 w-4" /> Iniciar Assistente
                    </Button>
                    <Button variant="outline" onClick={() => acao("stop_assistente", "/stop_assistente", "Assistente IA parado com sucesso!")} disabled={loading.stop_assistente || !status.assistente_rodando} className="w-full justify-start">
                        <PowerOff className="mr-2 h-4 w-4" /> Parar Assistente
                    </Button>
                </ActionCard>

                {/* Ações de Dados */}
                <ActionCard title="Gerenciamento de Dados">
                     <Button onClick={() => acao("extrair_chamados", "/extrair_chamados", "Extração de chamados do MySQL iniciada!")} disabled={loading.extrair_chamados} className="w-full justify-start">
                        <DatabaseZap className="mr-2 h-4 w-4" /> Extrair Chamados (MySQL)
                    </Button>
                    <Button onClick={() => acao("indexar_arquivos", "/indexar_arquivos", "Indexação de arquivos locais iniciada!")} disabled={loading.indexar_arquivos} className="w-full justify-start">
                        <FileText className="mr-2 h-4 w-4" /> Indexar Arquivos (Locais)
                    </Button>
                    <Button onClick={() => acao("indexar_conversas", "/indexar_conversas", "Indexação de conversas do chat iniciada!")} disabled={loading.indexar_conversas} className="w-full justify-start">
                        <MessageSquare className="mr-2 h-4 w-4" /> Indexar Conversas (Chat)
                    </Button>
                </ActionCard>

                {/* Manutenção */}
                <ActionCard title="Manutenção">
                    <Button variant="destructive" onClick={() => {
                        if (window.confirm("Tem certeza que deseja limpar TODA a base de dados vetorial (ChromaDB)? Esta ação não pode ser desfeita.")) {
                            acao("limpar_chromadb", "/limpar_chromadb", "Limpeza do ChromaDB iniciada!");
                        }
                    }} disabled={loading.limpar_chromadb} className="w-full justify-start">
                        <Trash2 className="mr-2 h-4 w-4" /> Limpar ChromaDB
                    </Button>
                </ActionCard>
            </div>
        </div>
    );
}
