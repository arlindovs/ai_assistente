from llama_index import GPTVectorStoreIndex, Document, LLMPredictor, ServiceContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from langchain_community.llms import Ollama
import chromadb
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env

def extrair_chamados():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )
    cursor = conn.cursor()
    # Preferência: SQL via arquivo externo
    sql_file = os.getenv("MYSQL_SELECT_FILE")
    if sql_file and os.path.isfile(sql_file):
        with open(sql_file, encoding="utf-8") as f:
            query = f.read()
            print("Query lida do arquivo:")
            print(query)
    else:
        query = os.getenv("MYSQL_SELECT")
        print("Query lida do .env:")
        print(query)
    cursor.execute(query)
    docs = []
    for titulo, descricao in cursor.fetchall():
        texto = f"Título: {titulo}\nDescrição: {descricao}"
        docs.append(Document(text=texto))
    cursor.close()
    conn.close()
    return docs

def indexar_no_chroma(docs):
    llm_predictor = LLMPredictor(
        llm=Ollama(
            model="llama3"
        )
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model="local"
    )
    db = chromadb.PersistentClient(path="../../chroma_db")
    chroma_store = ChromaVectorStore(chroma_collection=db.get_or_create_collection("chamados_ia"))
    index = GPTVectorStoreIndex.from_documents(
        docs,
        service_context=service_context,
        vector_store=chroma_store
    )
    index.storage_context.persist(persist_dir="./chroma_db/chamados")
    print("Index salvo em ./chroma_db/")

if __name__ == "__main__":
    print("Extraindo chamados do MySQL...")
    docs = extrair_chamados()
    print(f"Total de chamados extraídos: {len(docs)}")
    print("Indexando chamados no ChromaDB...")
    indexar_no_chroma(docs)
    print("Indexação concluída!")
