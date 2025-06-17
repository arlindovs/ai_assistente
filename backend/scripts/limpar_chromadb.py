import shutil
import os

CHROMA_PATH = "../../chroma_db"  # ajuste se usar outro caminho!

def remover_chromadb_completo(chroma_path):
    chroma_path = os.path.abspath(chroma_path)
    if os.path.exists(chroma_path):
        confirm = input(f"ATENÇÃO: Isso vai REMOVER COMPLETAMENTE o diretório e todas as collections em '{chroma_path}'.\nTem certeza? (s/N): ")
        if confirm.strip().lower() == "s":
            shutil.rmtree(chroma_path)
            print(f"Diretório '{chroma_path}' removido com sucesso!")
        else:
            print("Operação cancelada.")
    else:
        print(f"O diretório '{chroma_path}' já não existe.")

if __name__ == "__main__":
    remover_chromadb_completo(CHROMA_PATH)