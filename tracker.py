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

    page = browser.new_page(
        locale="it-IT",
        extra_http_headers={
            "Accept-Language": "it-IT,it;q=0.9"
        }
    )

    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(5000)

    testo = page.locator("body").inner_text()

    # DEBUG: mostra cosa vede il browser
    print("TESTO PAGINA:")
    print(testo[:3000])

    browser.close()


prezzo = "Non trovato"


# Cerca il prezzo vicino a Totale
posizione = testo.find("Totale")

if posizione != -1:
    blocco = testo[posizione:posizione + 200]

    valori = re.findall(
        r"([0-9]+[.,][0-9]+)\s*(USD|EUR|€)",
        blocco
    )

    if valori:
        numero = valori[-1][0].replace(",", ".")
        valuta = valori[-1][1]

        if valuta == "EUR" or valuta == "€":
            prezzo = numero
        else:
            # fallback temporaneo
            prezzo = round(float(numero) * 0.9026, 2)


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
