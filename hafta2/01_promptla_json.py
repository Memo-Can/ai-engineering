"""Hafta 2 - Script 1: promptla JSON iste, json.loads ile oku.

Ayni istegi 5 kez gondeririz; kac seferde duz json.loads basarili olur bakariz.
"""

import json

from anthropic import Anthropic
from dotenv import load_dotenv
from ilan_modeli import ILAN_2, MODEL

load_dotenv()
client = Anthropic()

SYSTEM = (
    "Sana verilen is ilanindan alanlari cikar. "
    "Cevabi sadece JSON olarak ver. Alanlar: sirket, pozisyon, lokasyon, calisma_sekli, "
    "teknolojiler (liste), deneyim_yili, maas_var_mi."
)

DENEME = 5
basarili = 0
for i in range(1, DENEME + 1):
    r = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": ILAN_2}],
    )
    metin = r.content[0].text
    try:
        veri = json.loads(metin)
        basarili += 1
        print(f"#{i} OK   alanlar: {sorted(veri)}")
    except json.JSONDecodeError as e:
        print(f"#{i} HATA json.loads basarisiz ({e.msg}); cevabin ilk 60 karakteri: {metin[:60]!r}")

print(f"\nSonuc: {basarili}/{DENEME} cevap duz json.loads ile okundu")
