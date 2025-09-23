import os
import time
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from sheets import Sheets

SHEETS_ID = os.getenv("SHEETS_ID")
CREDS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
ALLOWED = os.getenv("ALLOWED_ORIGINS", "*")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["*"]
}})

sheets = Sheets(SHEETS_ID, CREDS_JSON)


def now_iso():
    return datetime.now(timezone.utc).isoformat()

def new_id():
    # ID estável e simples
    return str(int(time.time() * 1000))


# ---------- Helpers de mapeamento ----------
def map_out(rows, mapping):
    """Converte chaves normalizadas do Sheets para as chaves da API."""
    out = []
    for r in rows:
        obj = {}
        for api_key, norm_key in mapping.items():
            obj[api_key] = r.get(norm_key, "")
        # descarta linhas realmente vazias (ex.: sem titulo/nome)
        if any(v for v in obj.values()):
            out.append(obj)
    return out


# ---------- Avisos ----------
AVISOS_TAB = "Avisos"
AVISOS_HEADERS_ORDER = ["ID", "Timestamp", "Titulo", "Mensagem", "Autor", "Prioridade", "Status"]
AVISOS_MAPPING = {
    "id": "id",
    "timestamp": "timestamp",
    "titulo": "titulo",
    "mensagem": "mensagem",
    "autor": "autor",
    "prioridade": "prioridade",
    "status": "status",
}

@app.get("/api/health")
def health():
    return jsonify(
        {
            "message": "AD Jardim Marcia Backend is running",
            "status": "OK",
            "timestamp": now_iso(),
        }
    )

@app.post("/api/avisos")
def add_aviso():
    data = request.get_json(force=True) or {}
    row = [
        new_id(),
        now_iso(),
        data.get("titulo", ""),
        data.get("mensagem", ""),
        data.get("autor", ""),
        data.get("prioridade", ""),
        data.get("status", "Pendente"),
    ]
    sheets.append_row(AVISOS_TAB, row)
    return jsonify({"success": True, "data": {
        "id": row[0],
        "timestamp": row[1],
        "titulo": row[2],
        "mensagem": row[3],
        "autor": row[4],
        "prioridade": row[5],
        "status": row[6],
    }})

@app.get("/api/avisos")
def list_avisos():
    rows = sheets.get_rows(AVISOS_TAB)
    data = map_out(rows, AVISOS_MAPPING)
    # opcional: ordena por timestamp desc
    data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return jsonify({"success": True, "data": data})


# ---------- Louvores ----------
LOUVORES_TAB = "Louvores"
LOUVORES_HEADERS_ORDER = ["ID", "Timestamp", "Nome", "Musica", "Artista", "LinkYouTube", "Observacoes", "Status"]
LOUVORES_MAPPING = {
    "id": "id",
    "timestamp": "timestamp",
    "nome": "nome",
    "musica": "musica",
    "artista": "artista",
    "linkYouTube": "linkyoutube",
    "observacoes": "observacoes",
    "status": "status",
}

@app.post("/api/louvores")
def add_louvor():
    data = request.get_json(force=True) or {}
    row = [
        new_id(),
        now_iso(),
        data.get("Nome", data.get("nome", "")),
        data.get("Musica", data.get("musica", "")),
        data.get("Artista", data.get("artista", "")),
        data.get("LinkYouTube", data.get("linkYouTube", data.get("linkyoutube", ""))),
        data.get("Observacoes", data.get("observacoes", "")),
        data.get("Status", data.get("status", "Pendente")),
    ]
    sheets.append_row(LOUVORES_TAB, row)
    return jsonify({"success": True, "data": {
        "id": row[0], "timestamp": row[1], "nome": row[2], "musica": row[3],
        "artista": row[4], "linkYouTube": row[5], "observacoes": row[6], "status": row[7]
    }})

@app.get("/api/louvores")
def list_louvores():
    rows = sheets.get_rows(LOUVORES_TAB)
    return jsonify({"success": True, "data": map_out(rows, LOUVORES_MAPPING)})


# ---------- Orações ----------
ORACOES_TAB = "Orações"  # a aba está com acento nas capturas
ORACOES_HEADERS_ORDER = ["ID", "Timestamp", "Nome", "Pedido", "Reservado", "Status"]
ORACOES_MAPPING = {
    "id": "id",
    "timestamp": "timestamp",
    "nome": "nome",
    "pedido": "pedido",
    "reservado": "reservado",
    "status": "status",
}

@app.post("/api/oracoes")
def add_oracao():
    data = request.get_json(force=True) or {}
    row = [
        new_id(),
        now_iso(),
        data.get("Nome", data.get("nome", "")),
        data.get("Pedido", data.get("pedido", "")),
        data.get("Reservado", data.get("reservado", "")),
        data.get("Status", data.get("status", "Pendente")),
    ]
    sheets.append_row(ORACOES_TAB, row)
    return jsonify({"success": True, "data": {
        "id": row[0], "timestamp": row[1], "nome": row[2],
        "pedido": row[3], "reservado": row[4], "status": row[5]
    }})

@app.get("/api/oracoes")
def list_oracoes():
    rows = sheets.get_rows(ORACOES_TAB)
    return jsonify({"success": True, "data": map_out(rows, ORACOES_MAPPING)})


# ---------- Visitantes ----------
VISITANTES_TAB = "Visitantes"
VISITANTES_HEADERS_ORDER = ["ID", "Timestamp", "Nome", "Telefone", "Email", "Endereco", "ComoConheceu", "Status"]
VISITANTES_MAPPING = {
    "id": "id",
    "timestamp": "timestamp",
    "nome": "nome",
    "telefone": "telefone",
    "email": "email",
    "endereco": "endereco",
    "comoConheceu": "comoconheceu",
    "status": "status",
}

@app.post("/api/visitantes")
def add_visitante():
    data = request.get_json(force=True) or {}
    row = [
        new_id(),
        now_iso(),
        data.get("Nome", data.get("nome", "")),
        data.get("Telefone", data.get("telefone", "")),
        data.get("Email", data.get("email", "")),
        data.get("Endereco", data.get("endereco", "")),
        data.get("ComoConheceu", data.get("comoConheceu", data.get("comoconheceu", ""))),
        data.get("Status", data.get("status", "Novo")),
    ]
    sheets.append_row(VISITANTES_TAB, row)
    return jsonify({"success": True, "data": {
        "id": row[0], "timestamp": row[1], "nome": row[2], "telefone": row[3],
        "email": row[4], "endereco": row[5], "comoConheceu": row[6], "status": row[7]
    }})

@app.get("/api/visitantes")
def list_visitantes():
    rows = sheets.get_rows(VISITANTES_TAB)
    return jsonify({"success": True, "data": map_out(rows, VISITANTES_MAPPING)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
