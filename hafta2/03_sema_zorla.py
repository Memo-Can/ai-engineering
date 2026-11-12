"""Hafta 2 - Script 3: semayi API'ye vermek.

Yontem A: client.messages.parse(output_format=Ilan)  -> SDK semayi API'ye verir, sonucu pydantic nesnesine cevirir
Yontem B: tool use + tool_choice                      -> modeli "ilan_kaydet" aracini cagirmaya zorlar,
                                                         aracin girdisi (input) bizim semamiz olur
"""

from anthropic import Anthropic
from dotenv import load_dotenv
from ilan_modeli import ILAN_2, MODEL, Ilan

load_dotenv()
client = Anthropic()

SYSTEM = "Sana verilen is ilanindan alanlari cikar."


def yontem_a(metin: str) -> Ilan:
    r = client.messages.parse(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": metin}],
        output_format=Ilan,
    )
    return r.parsed_output  # dogrulanmis Ilan nesnesi


def yontem_b(metin: str) -> Ilan:
    r = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": metin}],
        tools=[
            {
                "name": "ilan_kaydet",
                "description": "Is ilanindan cikarilan alanlari kaydeder.",
                "input_schema": Ilan.model_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": "ilan_kaydet"},
    )
    blok = next(b for b in r.content if b.type == "tool_use")
    return Ilan.model_validate(blok.input)  # yine de dogrula


for ad, fonksiyon in [("A) messages.parse", yontem_a), ("B) tool use", yontem_b)]:
    print(f"=== {ad} ===")
    try:
        print(fonksiyon(ILAN_2).model_dump_json(indent=2))
    except Exception as e:  # noqa: BLE001 - egitim amacli, hatayi oldugu gibi gormek istiyoruz
        print(f"HATA ({type(e).__name__}): {str(e)[:300]}")
    print()
