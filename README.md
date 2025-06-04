# Assistente IA de Atendimento – Chatbot Local com LlamaIndex + ChromaDB + Ollama

Este projeto implementa um assistente virtual para atendimento e suporte técnico, que responde perguntas com base nos chamados do seu MySQL e também aprende com as conversas dos usuários, utilizando IA local (Llama3 via Ollama) e vetorização com ChromaDB.

---

## Funcionalidades

- **Extração automática dos chamados do MySQL e indexação vetorial local**
- **Interface web de chat simples via Gradio**
- **Salva todas as conversas em banco SQLite**
- **Indexação incremental das conversas, sem sobrescrever o banco de chamados**
- **Consulta aos dois bancos de conhecimento (chamados + conversas) simultaneamente, retornando sempre a resposta mais relevante**
- **Respostas sempre em português**
- **Roda 100% local: NÃO envia dados sensíveis para nuvem ou APIs externas**

---

## Pré-requisitos

- Python 3.10+
- Docker rodando o Ollama OU Ollama instalado nativamente (para rodar Llama3)
- MySQL/MariaDB com os chamados e notas
- [Opcional] GPU para acelerar embeddings locais (não obrigatório)