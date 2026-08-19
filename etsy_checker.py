import requests
import os
import json
from bs4 import BeautifulSoup

SHOP_URL = "https://www.etsy.com/ca/shop/SadhuDah"
WEBHOOK = os.environ["DISCORD_WEBHOOK"]
STATE_FILE = "seen.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(SHOP_URL, headers=headers).text
soup = BeautifulSoup(html, "html.parser")

listings = []

for link in soup.find_all("a", href=True):
    href = link["href"]

    if "/listing/" in href:
        title = link.get_text(strip=True)

        if title:
            listings.append({
                "title": title,
                "url": href.split("?")[0]
            })

# Remove duplicates
unique = {}
for item in listings:
    unique[item["url"]] = item

listings = list(unique.values())

try:
    with open(STATE_FILE) as f:
        seen = set(json.load(f))
except FileNotFoundError:
    seen = set()

new = [item for item in listings if item["url"] not in seen]

for item in reversed(new):
    payload = {
        "username": "SadhuDah Etsy",
        "embeds": [{
            "title": item["title"],
            "url": item["url"],
            "description": "🛍️ New listing from SadhuDah",
            "footer": {
                "text": "SadhuDah Etsy Shop"
            }
        }]
    }

    requests.post(WEBHOOK, json=payload)

with open(STATE_FILE, "w") as f:
    json.dump([item["url"] for item in listings], f)
