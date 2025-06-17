import sqlite3
from datetime import datetime
import gradio as gr
from llama_index import load_index_from_storage, LLMPredictor, ServiceContext, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from langchain_community.llms import Ollama
import chromadb
import re
import os


def anonimizar_nomes(texto):
    # Expressão simples para detectar nomes tipo "João Silva", "Maria", "Carlos Alberto"
    # Você pode expandir com uma lista de nomes comuns ou uma lib de NER
    nomes_comuns = ["João", "Maria", "Carlos", "Ana", "José", "Paulo", "Pedro", "Lucas", "Marcos", "Luiz", "Rafael", "Fernanda", "Patrícia", "Jheniffer"]
    for nome in nomes_comuns:
        texto = re.sub(rf'\b{nome}\b', '[NOME_REMOVIDO]', texto)
    return texto

def identificar_pergunta_identidade(pergunta):
    perguntas_identidade = [
        r"(quem|qual).*você", r"(seu|sua).*(nome|identidade)", r"o que.*você", r"você é um robô", r"você.*skynet"
    ]
    pergunta = pergunta.lower()
    return any(re.search(p, pergunta) for p in perguntas_identidade)

def carregar_query_engines():
    llm_predictor = LLMPredictor(llm=Ollama(model="llama3"))
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, embed_model="local"
    )
    chroma_path = "../../chroma_db"
    db = chromadb.PersistentClient(path=chroma_path)
    collections_disponiveis = db.list_collections()

    # Nome lógico -> (nome da collection, subdiretório de persistência)
    collections_config = {
        "chamados": ("chamados_ia", "./chroma_db/chamados"),
        "conversas": ("conversas_ia", "./chroma_db/conversas"),
        "documentos": ("documentos_texto", "./chroma_db/documentos"),
    }

    query_engines = []
    for nome_logico, (nome_collection, persist_dir) in collections_config.items():
        existe = any(col.name == nome_collection for col in collections_disponiveis)
        docstore_json = os.path.join(persist_dir, "docstore.json")
        if existe and os.path.exists(docstore_json):
            try:
                coll = db.get_or_create_collection(nome_collection)
                store = ChromaVectorStore(chroma_collection=coll)
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                idx = load_index_from_storage(
                    storage_context=storage_context,
                    service_context=service_context,
                    vector_store=store
                )
                query_engines.append((nome_logico, idx.as_query_engine()))
                print(f"Collection '{nome_logico}' carregada com sucesso.")
            except Exception as e:
                print(f"[AVISO] Não foi possível carregar a collection '{nome_logico}': {e}")
        else:
            print(f"[INFO] Collection '{nome_logico}' não existe ou está sem índice. Ignorando.")
    return query_engines

def salvar_conversa(pergunta, resposta, atendente):
    conn = sqlite3.connect("../db/conversas_chat.db")
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
    # 1. Checagem especial para perguntas sobre identidade
    if identificar_pergunta_identidade(mensagem):
        resposta_final = (
            "Olá! Eu me chamo **Jheniffer**, sou uma assistente virtual profissional — prima do Jarvis, "
            "mas pode ficar tranquilo: não pretendo dominar o mundo nem criar a Skynet 😄. "
            "Estou aqui para ajudar você com informações do sistema!"
        )
        historico = historico or []
        historico.append((mensagem, resposta_final.strip()))
        salvar_conversa(mensagem, resposta_final.strip(), atendente_nome)
        return "", historico, historico

    prompt = (
        "Responda APENAS em português do Brasil, de forma clara, objetiva e profissional. "
        f"Pergunta: {mensagem}"
    )
    trechos = []
    for nome, engine in query_engines:
        result = engine.retrieve(prompt)
        for r in result:
            content = getattr(r, 'text', '') or getattr(r, 'get_content', lambda: '')()
            if not content:
                continue
            content = anonimizar_nomes(content)
            trechos.append(f"[Base: {nome}] {content.strip()}")

    contexto = "\n\n".join(trechos)
    print("CONTEXTOS UTILIZADOS:\n", contexto)
    llm_prompt = (
        "Responda APENAS em português do Brasil.\n"
        "Seja direto, preciso, claro e profissional.\n"
        "Baseie sua resposta EXCLUSIVAMENTE nas informações fornecidas das bases de conhecimento.\n"
        "Não revele ou utilize nomes de pessoas dos chamados (substitua nomes por [NOME_REMOVIDO] se necessário).\n"
        "Caso pergunte quem é você, responda: 'Sou Jheniffer, uma assistente virtual profissional, prima do Jarvis, mas sem pretensão de criar a Skynet.'\n"
        "Inclua dados concretos, procedimentos, exemplos ou detalhes relevantes sempre que possível.\n"
        "Se não houver informação suficiente para responder, diga claramente: "
        "'Não foi possível encontrar uma resposta exata para sua pergunta com base nas informações disponíveis. Informe para o clinete entrar em contato com o Suporte.'\n\n"
        f"Trechos disponíveis:\n{contexto}\n\nPergunta do usuário: {mensagem}\nResposta:"
    )

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
