"""Hafta 3 - Script 2: ilk agent. Model araca ihtiyac duydukca dongu doner.

Dongu: istek at -> stop_reason == "tool_use" ise araclari calistir, sonuclari ekle, tekrar istek at.
       stop_reason == "end_turn" ise model bitirmistir.
"""

from anthropic import Anthropic
from araclar import ARACLAR, MODEL, arac_calistir
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

SYSTEM = "Sen is ilani asistanisin. Cevap vermeden once gerekli bilgiyi araclardan al, tahmin etme. Turkce cevap ver."
SORU = "Django isteyen ilanlar arasinda en yuksek maas veren hangisi? Maas araligini ve calisma sekliyle birlikte soyle."
MAKS_TUR = 8  # sonsuz donguye karsi guvenlik siniri


def agent_calistir(soru: str) -> str:
    mesajlar = [{"role": "user", "content": soru}]
    girdi_tok = cikti_tok = 0
    for tur in range(1, MAKS_TUR + 1):
        r = client.messages.create(model=MODEL, max_tokens=800, system=SYSTEM, tools=ARACLAR, messages=mesajlar)
        girdi_tok += r.usage.input_tokens
        cikti_tok += r.usage.output_tokens

        if r.stop_reason != "tool_use":
            print(f"\n[tur {tur}] bitti (stop_reason={r.stop_reason}) | toplam token: girdi {girdi_tok}, cikti {cikti_tok}")
            return "".join(b.text for b in r.content if b.type == "text")

        sonuclar = []
        for b in r.content:
            if b.type == "tool_use":
                s = arac_calistir(b.name, b.input)
                print(f"[tur {tur}] arac: {b.name}({b.input}) -> {s['content'][:70]}")
                sonuclar.append(
                    {"type": "tool_result", "tool_use_id": b.id, "content": s["content"], "is_error": s["is_error"]}
                )
        mesajlar += [
            {"role": "assistant", "content": r.content},
            {"role": "user", "content": sonuclar},
        ]
    return f"Tur siniri ({MAKS_TUR}) asildi, cevap alinamadi."


print(agent_calistir(SORU))
