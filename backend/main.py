from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARQUIVO_MAQUINAS = "maquinas.json"
ARQUIVO_MANUTENCOES = "dados_manutencao.json"


def carregar_json(caminho, padrao):
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def carregar_maquinas():
    return carregar_json(ARQUIVO_MAQUINAS, [])


def salvar_maquinas(maquinas):
    salvar_json(ARQUIVO_MAQUINAS, maquinas)


def carregar_manutencoes():
    return carregar_json(ARQUIVO_MANUTENCOES, [])


def salvar_manutencoes(manutencoes):
    salvar_json(ARQUIVO_MANUTENCOES, manutencoes)


def diferenca_dias(data_inicial: str, data_final: str) -> int:
    d1 = datetime.strptime(data_inicial, "%Y-%m-%d").date()
    d2 = datetime.strptime(data_final, "%Y-%m-%d").date()
    return (d2 - d1).days


def calcular_status(maquina: dict, ultima_data: str | None):
    if not ultima_data:
        return "Atrasada"

    hoje = datetime.now().date().strftime("%Y-%m-%d")
    intervalo = int(maquina.get("intervalo_dias", 30))
    tolerancia = int(maquina.get("tolerancia_dias", 7))
    dias = diferenca_dias(ultima_data, hoje)

    if dias <= intervalo:
        return "OK"
    if dias <= intervalo + tolerancia:
        return "Atenção"
    return "Atrasada"


def calcular_proxima_data(ultima_data: str | None, intervalo_dias: int):
    if not ultima_data:
        return None
    data_base = datetime.strptime(ultima_data, "%Y-%m-%d").date()
    return (data_base + timedelta(days=intervalo_dias)).strftime("%Y-%m-%d")


def montar_maquinas_com_status():
    maquinas = carregar_maquinas()
    manutencoes = carregar_manutencoes()

    resultado = []
    for maquina in maquinas:
        manutencoes_maquina = [
            m for m in manutencoes if m.get("maquina_id") == maquina["id"]
        ]
        manutencoes_maquina.sort(key=lambda x: x.get("data", ""), reverse=True)

        ultima = manutencoes_maquina[0] if manutencoes_maquina else None
        ultima_data = ultima.get("data") if ultima else None

        maquina_saida = {
            **maquina,
            "ultima_manutencao": ultima_data,
            "proxima_prevista": calcular_proxima_data(
                ultima_data, int(maquina.get("intervalo_dias", 30))
            ),
            "status_atual": calcular_status(maquina, ultima_data),
        }
        resultado.append(maquina_saida)

    return resultado


@app.get("/")
def home():
    return {"status": "API funcionando"}


@app.get("/api/maquinas")
def listar_maquinas():
    return montar_maquinas_com_status()


@app.get("/api/manutencoes")
def listar_manutencoes():
    return carregar_manutencoes()


@app.post("/api/manutencoes/mobile")
def receber_manutencao(payload: dict):
    manutencoes = carregar_manutencoes()
    payload["id"] = len(manutencoes) + 1
    manutencoes.append(payload)
    salvar_manutencoes(manutencoes)
    return {"ok": True, "id": payload["id"]}


@app.put("/api/maquinas/{maquina_id}/regra")
def atualizar_regra_maquina(maquina_id: int, payload: dict):
    maquinas = carregar_maquinas()
    atualizada = None

    for maquina in maquinas:
        if maquina["id"] == maquina_id:
            if "intervalo_dias" in payload:
                maquina["intervalo_dias"] = int(payload["intervalo_dias"])
            if "tolerancia_dias" in payload:
                maquina["tolerancia_dias"] = int(payload["tolerancia_dias"])
            atualizada = maquina
            break

    if not atualizada:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")

    salvar_maquinas(maquinas)
    return {"ok": True, "maquina": atualizada}
