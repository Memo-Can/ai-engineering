"""Hafta 2 - Script 2: promptla JSON + pydantic dogrulama + hata olursa yeniden deneme.

Once pydantic'in hatayi nasil yakaladigini sabit (uydurma) bir ornekle gosteririz,
sonra gercek model cevabiyla deneriz.
"""

import re

from anthropic import Anthropic
from dotenv import load_dotenv
from ilan_modeli import ILAN_1, ILAN_2, MODEL, Ilan
from pydantic import ValidationError

load_dotenv()
client = Anthropic()

SYSTEM = (
    "Sana verilen is ilanindan alanlari cikar. Cevabi sadece JSON olarak ver, baska metin yazma. "
    "Alanlar: sirket (str), pozisyon (str), lokasyon (str veya null), "
    "calisma_sekli (ofis | hibrit | uzaktan | belirtilmemis), teknolojiler (str listesi), "
    "deneyim_yili (tam sayi veya null), maas_var_mi (true/false)."
)


def kod_blogunu_soy(metin: str) -> str:
    """```json ... ``` sarmalini kaldirir (modelin sik yaptigi sey)."""
    m = re.search(r"```(?:json)?\s*(.*?)```", metin, re.DOTALL)
    return (m.group(1) if m else metin).strip()


# --- Bolum A: pydantic hatayi nasil yakalar (model cagrisi yok, ucretsiz) ---
KOTU = '{"sirket": "X", "pozisyon": "Dev", "calisma_sekli": "evden", "teknolojiler": "Python", "maas_var_mi": "belki"}'
print("=== A) Bozuk bir JSON'u pydantic nasil reddeder ===")
try:
    Ilan.model_validate_json(KOTU)
except ValidationError as e:
    for hata in e.errors():
        print(f"  alan={hata['loc'][0]!r:<16} sorun: {hata['msg']}")


# --- Bolum B: gercek model, hata olursa hatayi modele geri verip yeniden dene ---
def ilan_cikar(metin: str, en_fazla_deneme: int = 3) -> Ilan:
    mesajlar = [{"role": "user", "content": metin}]
    for deneme in range(1, en_fazla_deneme + 1):
        r = client.messages.create(model=MODEL, max_tokens=500, system=SYSTEM, messages=mesajlar)
        ham = r.content[0].text
        try:
            ilan = Ilan.model_validate_json(kod_blogunu_soy(ham))
            print(f"  deneme {deneme}: basarili")
            return ilan
        except ValidationError as e:
            print(f"  deneme {deneme}: dogrulama hatasi ({e.error_count()} alan), modele geri bildirim veriliyor")
            mesajlar += [
                {"role": "assistant", "content": ham},
                {"role": "user", "content": f"JSON su hatalari verdi, duzelt ve sadece JSON don:\n{e}"},
            ]
    raise RuntimeError("Model gecerli JSON uretemedi")


for ad, ilan_metni in [("ILAN_1", ILAN_1), ("ILAN_2", ILAN_2)]:
    print(f"\n=== B) {ad} ===")
    print(ilan_cikar(ilan_metni).model_dump_json(indent=2))
