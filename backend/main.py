from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
import subprocess, os, psutil, json, time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ['*'] para facilitar o teste. Troque para seu domínio depois!
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET = "supersecret"
USERS = {"admin": "senha123"}

def create_jwt(username):
    return jwt.encode({"user": username, "exp": time.time() + 3600}, SECRET, algorithm="HS256")
def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload.get("user")
    except:
        return None
def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_jwt(token)
    if not user: raise HTTPException(401, "Não autorizado")
    return user

@app.post("/api/login")
async def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    if USERS.get(username) == password:
        return {"token": create_jwt(username)}
    raise HTTPException(401, "Usuário ou senha inválidos.")

@app.get("/api/status")
def status(user=Depends(get_current_user)):
    running = any("assistente_ia.py" in " ".join(p.cmdline()) for p in psutil.process_iter(['cmdline']))
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return {"assistente_rodando": running, "cpu": cpu, "mem": mem}

@app.post("/api/start_assistente")
def start_assistente(user=Depends(get_current_user)):
    running = any("assistente_ia.py" in " ".join(p.cmdline()) for p in psutil.process_iter(['cmdline']))
    if not running:
        subprocess.Popen(["python3", "scripts/assistente_ia.py"])
        return {"status": "Assistente iniciado"}
    return {"status": "Já está rodando"}

@app.post("/api/stop_assistente")
def stop_assistente(user=Depends(get_current_user)):
    for p in psutil.process_iter(['pid', 'cmdline']):
        if "assistente_ia.py" in " ".join(p.cmdline()):
            p.terminate()
    return {"status": "Assistente parado"}

@app.post("/api/extrair_chamados")
def extrair_chamados(user=Depends(get_current_user)):
    subprocess.Popen(["python3", "scripts/extrair_chamados.py"])
    return {"status": "Extração iniciada"}

@app.post("/api/indexar_arquivos")
def indexar_arquivos(user=Depends(get_current_user)):
    subprocess.Popen(["python3", "scripts/indexar_arquivos.py"])
    return {"status": "Indexação de arquivos iniciada"}

@app.post("/api/indexar_conversas")
def indexar_conversas(user=Depends(get_current_user)):
    subprocess.Popen(["python3", "scripts/indexar_conversas.py"])
    return {"status": "Indexação de conversas iniciada"}

@app.post("/api/limpar_chromadb")
def limpar_chromadb(user=Depends(get_current_user)):
    subprocess.Popen(["python3", "scripts/limpar_chromadb.py"])
    return {"status": "Limpeza iniciada"}