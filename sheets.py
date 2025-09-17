
import os, json
from datetime import datetime, timezone
import gspread
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS_AVISOS = ["ID", "Timestamp", "Título", "Conteúdo", "Autor", "Prioridade", "Status"]

def _load_credentials():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        info = json.loads(creds_json)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        return service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    raise RuntimeError("Missing GOOGLE_CREDENTIALS_JSON or GOOGLE_APPLICATION_CREDENTIALS")

class SheetsRepo:
    def __init__(self, spreadsheet_id: str):
        if not spreadsheet_id:
            raise RuntimeError("SHEETS_ID not set")
        creds = _load_credentials()
        self.gc = gspread.authorize(creds)
        self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
        # Worksheet
        try:
            self.ws_avisos = self.spreadsheet.worksheet("Avisos")
        except gspread.WorksheetNotFound:
            self.ws_avisos = self.spreadsheet.add_worksheet(title="Avisos", rows=200, cols=10)
            self.ws_avisos.append_row(HEADERS_AVISOS)
        headers = self.ws_avisos.row_values(1)
        if not headers:
            self.ws_avisos.update("A1:G1", [HEADERS_AVISOS])

    def _next_id(self):
        vals = self.ws_avisos.col_values(1)
        if len(vals) <= 1:
            return 1
        nums = [int(v) for v in vals[1:] if v.isdigit()]
        return (max(nums) + 1) if nums else len(vals)

    def create_aviso(self, titulo, mensagem, autor, prioridade, status):
        _id = self._next_id()
        ts = datetime.now(timezone.utc).isoformat()
        self.ws_avisos.append_row([_id, ts, titulo, mensagem, autor, prioridade, status])
        return {"id": _id, "timestamp": ts, "titulo": titulo, "mensagem": mensagem, "autor": autor, "prioridade": prioridade, "status": status}

    def list_avisos(self):
        rows = self.ws_avisos.get_all_records(head=1)
        out = []
        for r in rows:
            out.append({
                "id": r.get("ID"),
                "timestamp": r.get("Timestamp"),
                "titulo": r.get("Título"),
                "mensagem": r.get("Conteúdo"),
                "autor": r.get("Autor"),
                "prioridade": r.get("Prioridade"),
                "status": r.get("Status"),
            })
        return out
