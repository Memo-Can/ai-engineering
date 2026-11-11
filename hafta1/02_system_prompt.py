"""Hafta 1 - Script 2: system prompt davranisi nasil degistirir.

Ayni soruyu uc farkli system prompt ile sorariz; sadece "system" degisir.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
client = Anthropic()

SORU = "Veritabanında index nedir?"

SYSTEMS = {
    "yok": None,
    "kisa": "Sen bir backend mentorusun. En fazla 2 cumleyle, jargon kullanmadan cevap ver.",
    "kalip": (
        "Sen bir backend mentorusun. Cevabi tam su bicimde ver:\n"
        "Tanim: <tek cumle>\n"
        "Ornek: <tek cumle, gunluk hayattan>\n"
        "Dikkat: <tek cumle, yaygin hata>"
    ),
}

for ad, system in SYSTEMS.items():
    kwargs = {"system": system} if system else {}
    r = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": SORU}],
        **kwargs,
    )
    print(f"=== system: {ad} (cikti {r.usage.output_tokens} token) ===")
    print(r.content[0].text, "\n")
