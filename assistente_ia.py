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
    chamados_store = ChromaVectorStore(chroma_collection=db.get_or_create_collection("chamados_ia"))
    conversas_store = ChromaVectorStore(chroma_collection=db.get_or_create_collection("conversas_ia"))
    storage_context = StorageContext.from_defaults(persist_dir="./chroma_db")

    chamados_index = load_index_from_storage(
        storage_context=storage_context,
        service_context=service_context,
        vector_store=chamados_store
    )
    conversas_index = load_index_from_storage(
        storage_context=storage_context,
        service_context=service_context,
        vector_store=conversas_store
    )
    return chamados_index.as_query_engine(), conversas_index.as_query_engine()

def salvar_conversa(pergunta, resposta):
    conn = sqlite3.connect("conversas_chat.db")
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS conversas (
                                                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                       pergunta TEXT,
                                                       resposta TEXT,
                                                       data TIMESTAMP
              )
              ''')
    c.execute(
        "INSERT INTO conversas (pergunta, resposta, data) VALUES (?, ?, ?)",
        (pergunta, resposta, datetime.now())
    )
    conn.commit()
    conn.close()

print("Carregando index vetorial local do ChromaDB...")
chamados_engine, conversas_engine = carregar_query_engines()
print("Assistente pronto!")

def responder_chat(mensagem, historico):
    prompt = (
        "Responda APENAS em português do Brasil, de forma clara, objetiva e profissional. "
        f"Pergunta: {mensagem}"
    )
    result_chamados = chamados_engine.query(prompt)
    result_conversas = conversas_engine.query(prompt)

    # Tenta pegar a melhor resposta baseado no score (se houver)
    score_chamados = getattr(result_chamados, "score", None)
    score_conversas = getattr(result_conversas, "score", None)

    # Se ambos têm score, escolha a de maior score (menor distância ou maior similaridade)
    # Adapte conforme seu objeto, pode ser 'similarity', 'score', ou 'confidence'
    if score_chamados is not None and score_conversas is not None:
        if score_chamados >= score_conversas:
            resposta_final = result_chamados.response.strip()
        else:
            resposta_final = result_conversas.response.strip()
    else:
        # Se não houver score, escolha a resposta mais longa (fallback simples)
        resposta_final = (
            result_chamados.response.strip()
            if len(result_chamados.response) >= len(result_conversas.response)
            else result_conversas.response.strip()
        )

    historico = historico or []
    historico.append((mensagem, resposta_final))
    salvar_conversa(mensagem, resposta_final)
    return "", historico, historico

with gr.Blocks(title="Assistente IA - Suporte") as demo:
    gr.Markdown("# Assistente IA - Suporte\nFaça perguntas sobre chamados. As respostas serão sempre em português.")
    chatbot = gr.Chatbot(label="Assistente IA (Chamados)", type='tuples')
    with gr.Row():
        msg = gr.Textbox(placeholder="Digite sua pergunta sobre os chamados...", label="Pergunta")
        clear = gr.Button("Limpar Chat")
    state = gr.State([])

    def submit_message(user_message, chat_history):
        return responder_chat(user_message, chat_history)

    msg.submit(submit_message, [msg, state], [msg, chatbot, state])
    clear.click(lambda: ("", []), None, [msg, chatbot, state])

demo.launch(share=True)
