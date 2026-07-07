import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json
import re
import requests
from playwright.sync_api import sync_playwright


url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"


# Browser automatico
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(locale="it-IT")

    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(5000)

    testo = page.locator("body").inner_text()

    browser.close()


# Prende prezzo USD
prezzo_usd = "Non trovato"

posizione = testo.find("Totale")

if posizione != -1:
    parte = testo[posizione:posizione + 150]

    prezzi = re.findall(
        r"([0-9]+[.,][0-9]+)\s*USD",
        parte
    )

    if prezzi:
        prezzo_usd = prezzi[-1].replace(",", ".")


# Cambio automatico USD EUR
prezzo = prezzo_usd

if prezzo_usd != "Non trovato":
    try:
        risposta = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=10
        )

        dati = risposta.json()

        cambio = dati["rates"]["EUR"]

        prezzo = round(
            float(prezzo_usd) * cambio,
            2
        )

    except Exception as e:
        print("Errore cambio:", e)
        prezzo = "Errore cambio"


# Google Sheets
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


ora = datetime.now(
    ZoneInfo("Europe/Rome")
).strftime("%d/%m/%Y %H:%M:%S")


sheet.append_row([
    ora,
    prezzo
])


print("USD:", prezzo_usd)
print("EUR:", prezzo)
print("Ora:", ora)
