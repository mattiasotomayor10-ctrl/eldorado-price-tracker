import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import re


url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"


# Scarica la pagina
html = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "it-IT,it;q=0.9"
    }
).text


# Cerca il prezzo
prezzo = "Non trovato"

patterns = [
    r"€\s?([0-9]+[.,][0-9]+)",
    r"([0-9]+[.,][0-9]+)\s?€",
    r'"price"\s*:\s*"?([0-9]+[.,][0-9]+)',
    r'"amount"\s*:\s*"?([0-9]+[.,][0-9]+)'
]

for pattern in patterns:
    risultato = re.search(pattern, html, re.IGNORECASE)
    if risultato:
        prezzo = risultato.group(1).replace(",", ".")
        break


# Collegamento Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.environ["GOOGLE_CREDENTIALS"]),
    scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1UdzDqGlSTkgkz3jH1fgsm2hLIJZbtBs5jnzBO0vPdAY"
).sheet1


# Ora italiana
ora = datetime.now(
    ZoneInfo("Europe/Rome")
).strftime("%d/%m/%Y %H:%M:%S")


# Scrive nel foglio
sheet.append_row([
    ora,
    prezzo
])


print("Salvato:", ora, prezzo)
