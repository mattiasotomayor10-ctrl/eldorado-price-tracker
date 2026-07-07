import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json
import re
from playwright.sync_api import sync_playwright


url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(locale="it-IT")

    page.goto(url, wait_until="networkidle")

    page.wait_for_timeout(5000)

    testo = page.locator("body").inner_text()

    browser.close()


# Cerca il prezzo di Premium Mega Fan - 12 Mesi
prezzo = "Non trovato"

posizione = testo.find("Premium Mega Fan - 12 Mesi")

if posizione != -1:
    parte = testo[posizione:posizione + 200]

    risultato = re.search(
        r"([0-9]+,[0-9]+)\s*USD",
        parte
    )

    if risultato:
        prezzo = risultato.group(1).replace(",", ".")


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


print("Prezzo salvato:", prezzo)
print("Ora:", ora)


