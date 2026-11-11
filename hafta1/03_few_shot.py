"""Hafta 1 - Script 3: few-shot (ornek vererek ogretme).

Gorev: bir quiz sorusunu zorluk seviyesine gore etiketle (kolay/orta/zor).
Once ornek olmadan, sonra 3 ornekle deneriz.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
client = Anthropic()

SYSTEM = "Sana verilen quiz sorusunu etiketle. Sadece tek kelime yaz: kolay, orta veya zor."

YENI_SORU = "Hangi element periyodik tabloda 'Au' sembolüyle gösterilir?"

ORNEKLER = [
    {"role": "user", "content": "Türkiye'nin başkenti neresidir?"},
    {"role": "assistant", "content": "kolay"},
    {"role": "user", "content": "Osmanlı'da Tanzimat Fermanı hangi yıl ilan edilmiştir?"},
    {"role": "assistant", "content": "orta"},
    {"role": "user", "content": "Heisenberg belirsizlik ilkesi hangi büyüklük çiftleri için geçerlidir?"},
    {"role": "assistant", "content": "zor"},
]


def sor(mesajlar, baslik):
    r = client.messages.create(
        model=MODEL,
        max_tokens=20,
        system=SYSTEM,
        messages=mesajlar,
    )
    print(f"{baslik:>12}: {r.content[0].text.strip()}")


sor([{"role": "user", "content": YENI_SORU}], "ornek yok")
sor(ORNEKLER + [{"role": "user", "content": YENI_SORU}], "3 ornekle")
