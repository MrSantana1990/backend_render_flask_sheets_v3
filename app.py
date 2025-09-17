
import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from sheets import SheetsRepo

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,https://jd-marcia.netlify.app")
ORIGINS = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
PORT = int(os.getenv("PORT", "10000"))
SHEETS_ID = os.getenv("SHEETS_ID")

app = Flask(__name__)
CORS(app, origins=ORIGINS, supports_credentials=False)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("app")

repo = None
try:
    repo = SheetsRepo(SHEETS_ID)
except Exception as e:
    log.error("Failed to initialize SheetsRepo: %s", e)

@app.get("/api/health")
def health():
    return jsonify({
        "message": "AD Jardim Marcia Backend is running",
        "status": "OK",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.get("/api/avisos")
def list_avisos():
    if not repo:
        return jsonify({"error": "Sheets repo not initialized", "success": False}), 500
    try:
        items = repo.list_avisos()
        return jsonify({"success": True, "data": items})
    except Exception:
        log.exception("GET /api/avisos failed")
        return jsonify({"error": "Erro ao acessar planilha", "success": False}), 500

@app.post("/api/avisos")
def create_aviso():
    if not repo:
        return jsonify({"error": "Sheets repo not initialized", "success": False}), 500
    payload = request.get_json(force=True, silent=False) or {}

    titulo = (payload.get("titulo") or "").strip()
    mensagem = (payload.get("mensagem") or payload.get("conteudo") or "").strip()
    autor = (payload.get("autor") or "").strip()
    prioridade = (payload.get("prioridade") or "Normal").strip()
    status = (payload.get("status") or "Pendente").strip()

    if not titulo or not mensagem:
        return jsonify({"error": "Campos obrigatórios: titulo, mensagem", "success": False}), 400

    try:
        created = repo.create_aviso(titulo=titulo, mensagem=mensagem, autor=autor, prioridade=prioridade, status=status)
        return jsonify({"success": True, "data": created})
    except Exception:
        log.exception("POST /api/avisos failed")
        return jsonify({"error": "Erro ao acessar planilha", "success": False}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
