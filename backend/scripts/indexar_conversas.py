from llama_index import GPTVectorStoreIndex, Document, LLMPredictor, ServiceContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from langchain_community.llms import Ollama
import chromadb
import sqlite3

def carregar_conversas():
    conn = sqlite3.connect("../db/conversas_chat.db")
    c = conn.cursor()
    c.execute("SELECT pergunta, resposta FROM conversas")
    docs = []
    for pergunta, resposta in c.fetchall():
        texto = f"Pergunta: {pergunta}\nResposta: {resposta}"
        docs.append(Document(text=texto))
    conn.close()
    return docs

def indexar_conversas_chroma(docs):
    llm_predictor = LLMPredictor(
        llm=Ollama(model="llama3")
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model="local"
    )
    db = chromadb.PersistentClient(path="../../chroma_db")
    chroma_store = ChromaVectorStore(chroma_collection=db.get_or_create_collection("conversas_ia"))
    index = GPTVectorStoreIndex.from_documents(
        docs,
        service_context=service_context,
        vector_store=chroma_store
    )
    index.storage_context.persist(persist_dir="../../chroma_db/conversas")
    print("Conversas indexadas na coleção 'conversas_ia' e persistidas.")


if __name__ == "__main__":
    conversas = carregar_conversas()
    if conversas:
        indexar_conversas_chroma(conversas)
    else:
        print("Nenhuma conversa para indexar.")
