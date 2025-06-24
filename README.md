# Assistente IA de Atendimento – Chatbot Local com LlamaIndex + ChromaDB + Ollama

Este projeto implementa um assistente virtual para atendimento e suporte técnico, que responde perguntas com base nos chamados do seu MySQL, documentos fornecidos e também aprende com as conversas dos usuários. Utiliza IA local (Llama3 via Ollama) e vetorização com ChromaDB, garantindo que dados sensíveis não saiam do ambiente local.

---

## Arquitetura do Projeto

O sistema é composto por:

- **Backend:** Desenvolvido em Python com FastAPI, responsável por:
    - Gerenciar a API para o frontend.
    - Controlar o ciclo de vida do assistente de IA.
    - Orquestrar a extração de dados de diversas fontes (MySQL, arquivos).
    - Indexar os dados no ChromaDB para busca vetorial.
    - Interagir com o modelo de linguagem Llama3 através do Ollama.
    - Armazenar o histórico de conversas em um banco de dados SQLite.
- **Frontend:** Uma aplicação React que fornece um Dashboard para:
    - Autenticação de usuários.
    - Visualizar o status do sistema (uso de CPU/memória, status do assistente).
    - Iniciar e parar o processo do assistente de IA.
    - Disparar processos de extração e indexação de chamados do MySQL.
    - Disparar processos de indexação de arquivos locais.
    - Disparar processos de indexação de conversas anteriores.
    - Limpar a base de dados vetorial (ChromaDB).
- **Assistente de IA (Chat Interface):** Uma interface de chat construída com Gradio, acessível via navegador, onde os usuários interagem diretamente com o assistente.
- **Banco de Dados Vetorial:** ChromaDB é utilizado para armazenar os embeddings dos textos e permitir buscas semânticas rápidas.
- **Modelo de Linguagem:** Llama3 (rodando via Ollama) é o cérebro por trás da geração de respostas.
- **Banco de Dados Relacional:**
    - MySQL/MariaDB: Fonte dos chamados originais.
    - SQLite: Armazena o histórico das conversas do chat para aprendizado e auditoria.

---

## Funcionalidades

- **Backend & Core IA:**
    - Extração automática dos chamados do MySQL e indexação vetorial local no ChromaDB.
    - Indexação de arquivos de texto, DOCX, DOC e PDF de uma pasta local.
    - Indexação incremental das conversas salvas em SQLite, permitindo que o bot aprenda com interações passadas.
    - Consulta simultânea a múltiplas bases de conhecimento (chamados, documentos, conversas) para fornecer a resposta mais relevante.
    - Respostas sempre em português, com anonimização de nomes e tratamento especial para perguntas sobre a identidade do bot.
    - Roda 100% local: NÃO envia dados sensíveis para nuvem ou APIs externas.
- **Frontend (Dashboard de Gerenciamento):**
    - Autenticação segura de usuários via JWT.
    - Monitoramento do status do sistema (CPU, memória, status do assistente).
    - Controles para iniciar/parar o assistente de IA (processo Gradio).
    - Botões para acionar a extração de chamados do MySQL.
    - Botões para acionar a indexação de arquivos da pasta `arquivos_para_indexar/`.
    - Botões para acionar a indexação de conversas do banco SQLite.
    - Funcionalidade para limpar completamente o ChromaDB.
- **Interface de Chat (Gradio):**
    - Interface web simples e intuitiva para interagir com o assistente.
    - Histórico de chat visível durante a sessão.
    - Exige nome do atendente para iniciar o atendimento (registrado junto com a conversa).

---

## Tecnologias Utilizadas

- **Backend:** Python, FastAPI, LlamaIndex, Langchain, Ollama, ChromaDB, SQLite, python-dotenv, mysql-connector-python, psutil, python-jose.
- **Frontend:** React, JavaScript, HTML, CSS.
- **Assistente IA:** Gradio.
- **Banco de Dados (Fonte):** MySQL/MariaDB.

---

## Estrutura de Diretórios

```
.
├── backend/                    # Código do backend FastAPI e scripts de IA
│   ├── main.py                 # Arquivo principal da API FastAPI
│   ├── requirements.txt        # Dependências Python do backend
│   ├── scripts/                # Scripts para extração, indexação, e o assistente Gradio
│   │   ├── assistente_ia.py    # Lógica do chatbot Gradio e interação com LlamaIndex/Ollama
│   │   ├── extrair_chamados.py # Script para extrair dados do MySQL
│   │   ├── indexar_arquivos.py # Script para indexar arquivos locais
│   │   ├── indexar_conversas.py# Script para indexar conversas do SQLite
│   │   └── limpar_chromadb.py  # Script para apagar o ChromaDB
│   └── db/                     # Banco de dados SQLite para conversas
│       └── conversas_chat.db   # (criado após a primeira conversa)
├── chroma_db/                  # Diretório de persistência do ChromaDB (criado automaticamente)
│   ├── chamados/
│   ├── conversas/
│   └── documentos/
├── arquivos_para_indexar/      # Pasta para colocar arquivos (.txt, .pdf, .docx, .doc) a serem indexados
├── src/                        # Código do frontend React
│   ├── App.js                  # Componente raiz do React
│   ├── AuthContext.js          # Gerenciamento de estado de autenticação
│   ├── api.js                  # Funções de chamada à API backend
│   └── components/             # Componentes React reutilizáveis (Login, Dashboard, etc.)
├── .env.example                # Arquivo de exemplo para variáveis de ambiente
├── .gitignore
└── README.md                   # Este arquivo
```

---

## Pré-requisitos

- Python 3.10+
- Node.js e npm/yarn (para o frontend React)
- Docker rodando o Ollama OU Ollama instalado nativamente.
    - Modelo Llama3 puxado e disponível no Ollama (`ollama pull llama3`)
- MySQL/MariaDB com uma base de dados contendo os chamados e notas.
- Arquivo `.env` configurado na raiz do projeto (copie de `.env.example` e preencha).
- [Opcional] GPU para acelerar embeddings locais e inferência do Llama3 (não obrigatório, mas recomendado para melhor performance).

---

## Como Rodar

1.  **Clone o repositório:**
    ```bash
    git clone <url_do_repositorio>
    cd <nome_do_repositorio>
    ```

2.  **Configure as Variáveis de Ambiente:**
    - Copie o arquivo `.env.example` para `.env` na raiz do projeto:
      ```bash
      cp .env.example .env
      ```
    - Edite o arquivo `.env` com as suas configurações:
        - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_PORT`
        - `MYSQL_SELECT` (query SQL direta) OU `MYSQL_SELECT_FILE` (caminho para um arquivo `.sql` com a query). O arquivo tem precedência.
        - `SECRET_KEY_JWT`: Uma chave secreta forte para os tokens JWT.

3.  **Backend:**
    - Navegue até a pasta `backend`:
      ```bash
      cd backend
      ```
    - Crie um ambiente virtual (recomendado) e ative-o:
      ```bash
      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      # venv\Scripts\activate    # Windows
      ```
    - Instale as dependências Python:
      ```bash
      pip install -r requirements.txt
      ```
    - Volte para a raiz do projeto:
      ```bash
      cd ..
      ```
    - Rode o servidor FastAPI (a partir da raiz do projeto):
      ```bash
      uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
      ```
      O backend estará acessível em `http://localhost:8000`.

4.  **Frontend:**
    - Em um novo terminal, navegue até a pasta `src`:
      ```bash
      cd src
      ```
    - Instale as dependências do Node.js:
      ```bash
      npm install
      # ou
      # yarn install
      ```
    - Inicie o servidor de desenvolvimento React:
      ```bash
      npm start
      # ou
      # yarn start
      ```
      O frontend estará acessível em `http://localhost:3000`.

5.  **Ollama e Llama3:**
    - Certifique-se que o Ollama está rodando e o modelo Llama3 foi baixado:
      ```bash
      ollama pull llama3
      ```
      (Se for a primeira vez, pode demorar um pouco).

6.  **Uso:**
    - Acesse o Dashboard React em `http://localhost:3000` para logar (usuário padrão: `admin`, senha: `senha123` - configurado em `backend/main.py`) e gerenciar o sistema.
    - No Dashboard:
        - **Extraia os chamados do MySQL:** Clique no botão correspondente.
        - **Indexe arquivos:** Coloque arquivos em `arquivos_para_indexar/` e clique no botão de indexar arquivos.
        - **Inicie o Assistente IA:** Clique para iniciar o processo Gradio.
    - Após iniciar o assistente, a interface de chat Gradio geralmente fica disponível em `http://localhost:7860` (verifique o console do processo `assistente_ia.py` para a URL exata, especialmente se a porta estiver em uso ou se `share=True` gerar uma URL pública).
    - Converse com o assistente! As conversas serão salvas e podem ser indexadas posteriormente através do Dashboard para melhorar futuras respostas.

---

## Variáveis de Ambiente (`.env`)

Certifique-se de configurar as seguintes variáveis no seu arquivo `.env` na raiz do projeto:

-   `MYSQL_HOST`: Host do seu servidor MySQL/MariaDB.
-   `MYSQL_USER`: Usuário para conectar ao MySQL.
-   `MYSQL_PASSWORD`: Senha para o usuário MySQL.
-   `MYSQL_DATABASE`: Nome da base de dados MySQL.
-   `MYSQL_PORT`: Porta do servidor MySQL (padrão `3306`).
-   `MYSQL_SELECT`: A query SQL completa para extrair os dados dos chamados. Exemplo: `"SELECT titulo, descricao_problema FROM chamados_table"`.
-   `MYSQL_SELECT_FILE`: (Opcional) Caminho para um arquivo `.sql` contendo a query de seleção. Se definido, sobrescreve `MYSQL_SELECT`. Exemplo: `"./config/minha_query.sql"`.
-   `SECRET_KEY_JWT`: Uma chave secreta aleatória e longa para a segurança dos tokens JWT. Você pode gerar uma usando `openssl rand -hex 32`.

---

## Licença

Este projeto é licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.