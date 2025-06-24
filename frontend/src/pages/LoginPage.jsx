import React, { useState } from "react";
import { api, setAuthToken } from "@/api/apiClient";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [erro, setErro] = useState("");
    const { login: authLogin } = useAuth(); // Renomeado para evitar conflito com nome de componente

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErro("");
        try {
            const resp = await api.post("/login", { username, password });
            setAuthToken(resp.data.token);
            authLogin(resp.data.token); // Usa a função renomeada
        } catch (err) {
            setErro("Usuário ou senha inválidos!");
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">Painel Assistente IA</CardTitle>
                    <CardDescription className="text-center">
                        Faça login para continuar
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Usuário</Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Seu usuário"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Senha</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Sua senha"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        {erro && <p className="text-sm text-red-600">{erro}</p>}
                        <Button type="submit" className="w-full">
                            Entrar
                        </Button>
                    </form>
                </CardContent>
                {/* <CardFooter>
                    <p className="text-xs text-center text-gray-500">
                        Esqueceu a senha? Contate o administrador.
                    </p>
                </CardFooter> */}
            </Card>
        </div>
    );
}
