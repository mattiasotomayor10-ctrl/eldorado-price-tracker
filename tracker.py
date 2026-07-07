import requests
from datetime import datetime

url = "https://www.eldorado.gg/it/crunchyroll-premium/t/253?attribute_value_id=premium-mega-fan-12-months"

html = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
).text

print("Controllo eseguito:", datetime.now())
print(html[:500])
