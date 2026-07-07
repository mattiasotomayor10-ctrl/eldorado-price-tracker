import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import re


url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"


# Scarica pagina Eldorado
html = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "it-IT,it;q=0.9"
    }
).text


# Cerca il prezzo corretto vicino a Mega Fan
prezzo = "Non trovato"

posizione = html.lower().find("mega fan")

if posizione != -1:
    parte = html[posizione:posizione + 3000]

    prezzi = re.findall(
        r"([0-9]+[.,][0-9]+)",
        parte
    )

    if prezzi:
        prezzo = prezzi[0].replace(",", ".")


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


# Salva nel foglio
sheet.append_row([
    ora,
    prezzo
])


print("Salvato:", ora, prezzo)
