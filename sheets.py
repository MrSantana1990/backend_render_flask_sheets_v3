import json
import os
from typing import List, Dict
from unidecode import unidecode

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _norm(s: str) -> str:
    return unidecode(str(s or "")).strip().lower()

def _a1_tab(tab: str) -> str:
    # Sempre quote o nome da aba em A1 notation (lida com espaços/acentos)
    return f"'{str(tab).replace(\"'\", \"''\")}'"


class Sheets:
    def __init__(self, spreadsheet_id: str, credentials_json: str):
        self.spreadsheet_id = spreadsheet_id
        info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        self.service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    def get_rows(self, tab: str) -> List[Dict]:
        res = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=f"{_a1_tab(tab)}!A:Z")
            .execute()
        )
        values = res.get("values", [])
        if not values:
            return []

        headers = [_norm(h) for h in values[0]]
        out: List[Dict] = []
        for row in values[1:]:
            if not any(str(c).strip() for c in row):
                continue
            item = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
            out.append(item)
        return out

    def append_row(self, tab: str, ordered_values: List[str]) -> None:
        body = {"values": [ordered_values]}
        try:
            (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{_a1_tab(tab)}!A1",
                    valueInputOption="USER_ENTERED",  # mais tolerante
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
        except HttpError as e:
            # Propaga como 400 amigável (devolve a mensagem real do Sheets)
            from flask import abort
            abort(400, description=e.reason or "Sheets append error")
