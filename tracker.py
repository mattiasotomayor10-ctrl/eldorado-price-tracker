import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import re

url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"

html = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
).text

# Cerca il prezzo nella pagina
match = re.search(r"€\s?([0-9]+[.,][0-9]+)", html)

if match:
    prezzo = match.group(1).replace(",", ".")
else:
    prezzo = "Non trovato"

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

# Scrive data, ora e prezzo
sheet.append_row([
    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    prezzo
])

print("Prezzo salvato:", prezzo)
