import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json
import re
from playwright.sync_api import sync_playwright


url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"


# Apri Eldorado
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


prezzo = "Non trovato"


# Cerca il prezzo finale USD
posizione = testo.find("Totale")

if posizione != -1:
    blocco = testo[posizione:posizione + 200]

    valori = re.findall(
        r"([0-9]+[.,][0-9]+)\s*USD",
        blocco
    )

    if valori:
        prezzo_usd = float(
            valori[-1].replace(",", ".")
        )

        # Cambio usato da Eldorado
        prezzo = round(
            prezzo_usd * 0.9009,
            2
        )


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


# Ora italiana
ora = datetime.now(
    ZoneInfo("Europe/Rome")
).strftime("%d/%m/%Y %H:%M:%S")


# Scrive nel foglio
sheet.append_row([
    ora,
    prezzo
])


print("Prezzo USD:", prezzo_usd if 'prezzo_usd' in locals() else "n/d")
print("Prezzo EUR:", prezzo)
print("Ora:", ora)
