"""Hafta 4 - Script 3: mini RAG (Retrieval-Augmented Generation).

RAG iki yariydir:
  1) BUL   : soruya en yakin ilanlari anlamsal aramayla bul (Retrieval)
  2) URET  : bulunan ilanlari modele ver, SADECE bunlara dayanarak kaynakli cevap yazdir (Generation)
"""

from anthropic import Anthropic
from dotenv import load_dotenv
from ortak import anlamsal_ara, indeks_olustur

load_dotenv()
client = Anthropic()
MODEL = "claude-haiku-4-5-20251001"

SYSTEM = (
    "Sen bir is ilani asistanisin. Sadece <ilanlar> icindeki bilgilere dayanarak cevap ver. "
    "Her bilginin yanina kaynak olarak [ilan N] yaz. "
    "Cevap ilanlarda yoksa 'Verilen ilanlarda bu bilgi yok.' de ve tahmin etme. Turkce cevap ver."
)

INDEKS = indeks_olustur()  # bir kez


def rag_cevap(soru: str, k: int = 3) -> None:
    # 1) BUL
    bulunanlar = anlamsal_ara(soru, INDEKS, k)
    print(f"SORU: {soru}")
    print("  Bulunan ilanlar:", ", ".join(f"#{i['id']} ({p:.2f})" for p, i in bulunanlar))

    # 2) URET: bulunanlari baglam olarak modele ver
    baglam = "\n".join(
        f"[ilan {i['id']}] {i['pozisyon']} - {i['sirket']} ({i['sehir']}): {i['metin']}" for _, i in bulunanlar
    )
    r = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"<ilanlar>\n{baglam}\n</ilanlar>\n\nSoru: {soru}"}],
    )
    cevap = "".join(b.text for b in r.content if b.type == "text")
    print(f"  CEVAP: {cevap}")
    print(f"  (girdi {r.usage.input_tokens}, cikti {r.usage.output_tokens} token)\n")


for soru in [
    "Uzaktan çalışabileceğim bir Django işi var mı?",
    "Flutter bilen biri için iş var mı, hangi şehirde?",
    "Aşçı pozisyonu var mı?",
    "En yüksek maaşı hangi ilan veriyor?",
]:
    rag_cevap(soru)
