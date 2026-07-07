import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json
import re
from playwright.sync_api import sync_playwright


url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months&currency=EUR"


# Apri Eldorado con browser
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        locale="it-IT",
        extra_http_headers={
            "Accept-Language": "it-IT,it;q=0.9"
        }
    )

    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(5000)

    testo = page.locator("body").inner_text()

    browser.close()


# Cerca prezzo EUR
prezzo = "Non trovato"

posizione = testo.find("Totale")

if posizione != -1:
    parte = testo[posizione:posizione + 200]

    prezzi = re.findall(
        r"([0-9]+[,.][0-9]+)\s*(EUR|€)",
        parte
    )

    if prezzi:
        prezzo = prezzi[-1][0].replace(",", ".")


# Se non trova EUR prova vicino al prodotto
if prezzo == "Non trovato":

    posizione = testo.find("Premium Mega Fan - 12 Mesi")

    if posizione != -1:
        parte = testo[posizione:posizione + 300]

        risultati = re.findall(
            r"([0-9]+[,.][0-9]+)\s*(EUR|€)",
            parte
        )

        if risultati:
            prezzo = risultati[-1][0].replace(",", ".")


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


print("Prezzo EUR:", prezzo)
print("Ora:", ora)
