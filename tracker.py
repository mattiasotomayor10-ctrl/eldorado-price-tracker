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


# Salva una copia per analizzare la pagina
with open("pagina_debug.txt", "w", encoding="utf-8") as f:
    f.write(html)


# Cerca il prezzo
prezzo = "Non trovato"

# Cerca numeri vicino alle parole del prodotto
parole = [
    "mega fan",
    "premium mega fan",
    "12 months",
    "12 mesi"
]

for parola in parole:
    posizione = html.lower().find(parola)

    if posizione != -1:
        parte = html[posizione:posizione + 5000]

        risultati = re.findall(
            r"(?:€\s*)?([0-9]+[.,][0-9]+)",
            parte
        )

        if risultati:
            prezzo = risultati[0].replace(",", ".")
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

