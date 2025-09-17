import json
import os
from typing import List, Dict
from unidecode import unidecode

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _norm(s: str) -> str:
    return unidecode(str(s or "")).strip().lower()


class Sheets:
    def __init__(self, spreadsheet_id: str, credentials_json: str):
        self.spreadsheet_id = spreadsheet_id

        # credentials_json pode ser o JSON bruto vindo da env
        info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        self.service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    def get_rows(self, tab: str) -> List[Dict]:
        res = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.spreadsheet_id, range=f"{tab}!A:Z")
            .execute()
        )
        values = res.get("values", [])
        if not values:
            return []

        headers = [_norm(h) for h in values[0]]
        out: List[Dict] = []
        for row in values[1:]:
            # pula linha totalmente vazia
            if not any(str(c).strip() for c in row):
                continue
            item = {}
            for i, h in enumerate(headers):
                item[h] = row[i] if i < len(row) else ""
            out.append(item)
        return out

    def append_row(self, tab: str, ordered_values: List[str]) -> None:
        body = {"values": [ordered_values]}
        (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{tab}!A1",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
