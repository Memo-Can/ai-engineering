"""Hafta 3 - Script 1: tek arac, tek tur, elle adim adim.

Model fonksiyonu KENDISI calistirmaz. Bize "su araci su girdiyle cagir" der (tool_use),
biz calistirip sonucu geri veririz (tool_result), model sonra son cevabi yazar.
"""

from anthropic import Anthropic
from araclar import ARACLAR, MODEL, arac_calistir
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

SORU = "Django isteyen ilanlar hangileri?"
mesajlar = [{"role": "user", "content": SORU}]

# --- 1. istek: model araca ihtiyac duyar mi? ---
r1 = client.messages.create(model=MODEL, max_tokens=500, tools=ARACLAR, messages=mesajlar)
print("1. istek  stop_reason:", r1.stop_reason)
for blok in r1.content:
    if blok.type == "text":
        print("  [text]    ", blok.text)
    elif blok.type == "tool_use":
        print(f"  [tool_use] ad={blok.name} girdi={blok.input} id={blok.id}")

# --- biz araci calistiririz ---
arac_bloklari = [b for b in r1.content if b.type == "tool_use"]
sonuclar = []
for b in arac_bloklari:
    s = arac_calistir(b.name, b.input)
    print(f"  -> calisti: {s['content'][:100]}")
    sonuclar.append({"type": "tool_result", "tool_use_id": b.id, "content": s["content"], "is_error": s["is_error"]})

# --- 2. istek: konusma gecmisi + arac sonucu ---
mesajlar += [
    {"role": "assistant", "content": r1.content},
    {"role": "user", "content": sonuclar},
]
r2 = client.messages.create(model=MODEL, max_tokens=500, tools=ARACLAR, messages=mesajlar)
print("\n2. istek  stop_reason:", r2.stop_reason)
print(r2.content[0].text)

print(f"\nToplam token: girdi {r1.usage.input_tokens + r2.usage.input_tokens}, cikti {r1.usage.output_tokens + r2.usage.output_tokens}")
