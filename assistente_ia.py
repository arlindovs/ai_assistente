import sqlite3
from datetime import datetime
import gradio as gr
from llama_index import load_index_from_storage, LLMPredictor, ServiceContext, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from langchain_community.llms import Ollama
import chromadb

def carregar_query_engines():
    llm_predictor = LLMPredictor(llm=Ollama(model="llama3"))
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, embed_model="local"
    )
    db = chromadb.PersistentClient(path="./chroma_db")
    collections = [
        ("chamados", db.get_or_create_collection("chamados_ia")),
        ("conversas", db.get_or_create_collection("conversas_ia")),
        ("documentos", db.get_or_create_collection("documentos_texto")),
    ]
    storage_context = StorageContext.from_defaults(persist_dir="./chroma_db")
    query_engines = []
    for nome, coll in collections:
        store = ChromaVectorStore(chroma_collection=coll)
        idx = load_index_from_storage(
            storage_context=storage_context,
            service_context=service_context,
            vector_store=store
        )
        query_engines.append((nome, idx.as_query_engine()))
    return query_engines

def salvar_conversa(pergunta, resposta, atendente):
    conn = sqlite3.connect("conversas_chat.db")
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS conversas (
                                                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                       atendente TEXT,
                                                       pergunta TEXT,
                                                       resposta TEXT,
                                                       data TIMESTAMP
              )
              ''')
    c.execute(
        "INSERT INTO conversas (atendente, pergunta, resposta, data) VALUES (?, ?, ?, ?)",
        (atendente, pergunta, resposta, datetime.now())
    )
    conn.commit()
    conn.close()

print("Carregando indices vetoriais locais do ChromaDB...")
query_engines = carregar_query_engines()
print("Assistente otimizado pronto!")

def responder_chat(mensagem, historico, atendente_nome):
    prompt = (
        "Responda APENAS em português do Brasil, de forma clara, objetiva e profissional. "
        f"Pergunta: {mensagem}"
    )
    trechos = []
    for nome, engine in query_engines:
        # Recupera o trecho mais similar de cada base (top_k=1)
        result = engine.retrieve(prompt)
        for r in result:
            content = getattr(r, 'text', '') or getattr(r, 'get_content', lambda: '')()
            if not content:
                continue
            trechos.append(f"[Base: {nome}] {content.strip()}")

    # Junta todos os trechos em um só contexto para o LLM
    contexto = "\n\n".join(trechos)
    llm_prompt = (
        "Responda APENAS em português do Brasil.\n"
        "Seja direto, preciso, claro e profissional.\n"
        "Baseie sua resposta EXCLUSIVAMENTE nas informações fornecidas nos trechos abaixo, retirados das bases do sistema.\n"
        "NÃO invente informações e não utilize conhecimento próprio fora dos trechos.\n"
        "Inclua dados concretos, procedimentos, exemplos ou detalhes relevantes sempre que possível.\n"
        "Se não houver informação suficiente para responder, diga claramente: "
        "'Não foi possível encontrar uma resposta exata para sua pergunta com base nas informações disponíveis.'\n\n"
        f"Trechos disponíveis:\n{contexto}\n\nPergunta do usuário: {mensagem}\nResposta:"
    )

    # UMA chamada ao LLM (Ollama)
    llm = Ollama(model="llama3")
    resposta_final = llm(llm_prompt)

    historico = historico or []
    historico.append((mensagem, resposta_final.strip()))
    salvar_conversa(mensagem, resposta_final.strip(), atendente_nome)
    return "", historico, historico

with gr.Blocks(title="Assistente IA - Suporte") as demo:
    gr.Markdown("# Assistente IA - Suporte\nPreencha o nome do atendente para iniciar o atendimento.")
    with gr.Row():
        atendente_input = gr.Textbox(label="Nome do atendente", placeholder="Digite o nome do atendente...", interactive=True, visible=True)
        iniciar_btn = gr.Button("Iniciar Atendimento", visible=True)
    chatbot = gr.Chatbot(label="Assistente IA", type='tuples', visible=False)
    with gr.Row():
        msg = gr.Textbox(placeholder="Digite sua pergunta...", label="Pergunta", visible=False)
        clear = gr.Button("Limpar Chat", visible=False)
    state = gr.State([])
    atendente_state = gr.State("")

    def habilitar_chat(nome):
        if nome.strip() == "":
            # Mantém escondido se não preencher nome
            return gr.update(visible=True), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        # Esconde nome+botão e mostra chat, caixa e limpar
        return (
            gr.update(visible=False),  # atendente_input
            gr.update(visible=False),  # iniciar_btn
            gr.update(visible=True),   # chatbot
            gr.update(visible=True),   # msg
            gr.update(visible=True),   # clear
        )

    iniciar_btn.click(
        habilitar_chat,
        inputs=[atendente_input],
        outputs=[atendente_input, iniciar_btn, chatbot, msg, clear]
    )

    def submit_message(user_message, chat_history, atendente_nome):
        return responder_chat(user_message, chat_history, atendente_nome)

    msg.submit(
        submit_message,
        [msg, state, atendente_input],
        [msg, chatbot, state]
    )
    clear.click(lambda: ("", []), None, [msg, chatbot, state])


demo.launch(share=True)
