import chromadb

# Caminho do banco ChromaDB (ajuste se necessário)
CHROMA_PATH = "./chroma_db"

def limpar_todas_collections_chromadb(chroma_path):
    db = chromadb.PersistentClient(path=chroma_path)
    collections = db.list_collections()
    if not collections:
        print("Nenhuma collection encontrada no banco ChromaDB.")
        return
    print("Collections encontradas:")
    for c in collections:
        print(f"- {c.name} ({c.count()} documentos)")

    confirm = input(f"\nTEM CERTEZA que deseja apagar TODOS os documentos de TODAS as collections acima? (s/N): ")
    if confirm.strip().lower() == "s":
        for c in collections:
            print(f"Limpando collection '{c.name}'...")
            ids = c.get()["ids"]
            if ids:
                c.delete(ids=ids)
                print(f"{len(ids)} documentos removidos de '{c.name}'.")
            else:
                print(f"Collection '{c.name}' já estava vazia.")


if __name__ == "__main__":
    limpar_todas_collections_chromadb(CHROMA_PATH)
