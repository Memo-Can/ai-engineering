"""Hafta 5 - Script 5: pgvector ile RAG. Hafta 4'teki mini RAG'in ayni fikri, bu sefer:
  - belge parcalanmis (bolum bazli chunking),
  - parcalar PostgreSQL'de duruyor (03_pgvector_yaz_ara.py bir kez calistirilmis olmali),
  - retrieval bir SQL sorgusu.
"""

from anthropic import Anthropic
from db import baglan
from dotenv import load_dotenv
from ortak import embed_et

load_dotenv()
client = Anthropic()
MODEL = "claude-haiku-4-5-20251001"
FIYAT_GIRDI, FIYAT_CIKTI = 1.00, 5.00  # $ / milyon token (Haiku 4.5)

SYSTEM = (
    "Sen bir sirket ici el kitabi asistanisin. Sadece <parcalar> icindeki bilgilere dayanarak cevap ver. "
    "Her bilginin yanina kaynak olarak [bolum adi] yaz. "
    "Cevap parcalarda yoksa 'El kitabinda bu bilgi yok.' de ve tahmin etme. Turkce, kisa cevap ver."
)

con = baglan()
if con.execute("SELECT to_regclass('parcalar')").fetchone()[0] is None:
    raise SystemExit("parcalar tablosu yok: once 03_pgvector_yaz_ara.py calistir")

toplam_girdi = toplam_cikti = 0


def sor(soru: str, k: int = 3) -> None:
    global toplam_girdi, toplam_cikti
    q = embed_et([soru])[0]
    satirlar = con.execute(
        "SELECT bolum, metin, 1 - (embedding <=> %s) AS benzerlik FROM parcalar ORDER BY embedding <=> %s LIMIT %s",
        (q, q, k),
    ).fetchall()
    print(f"SORU: {soru}")
    print("  Bulunan parcalar:", ", ".join(f"{b} ({s:.2f})" for b, _, s in satirlar))

    baglam = "\n".join(f"[{b}] {m.split(': ', 1)[1]}" for b, m, _ in satirlar)
    r = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"<parcalar>\n{baglam}\n</parcalar>\n\nSoru: {soru}"}],
    )
    cevap = "".join(b.text for b in r.content if b.type == "text")
    print(f"  CEVAP: {cevap}")
    print(f"  (girdi {r.usage.input_tokens}, cikti {r.usage.output_tokens} token)\n")
    toplam_girdi += r.usage.input_tokens
    toplam_cikti += r.usage.output_tokens


for soru in [
    "Yıllık iznim kaç gün, kullanmadığım günleri devredebilir miyim?",
    "Gece sistem çökerse kim bakıyor, bunun karşılığında ne alıyor?",
    "Eşim ve çocuklarım sağlık sigortası kapsamında mı?",
    "Şirkete köpeğimi getirebilir miyim?",
]:
    sor(soru)

maliyet = toplam_girdi / 1e6 * FIYAT_GIRDI + toplam_cikti / 1e6 * FIYAT_CIKTI
print(f"TOPLAM: {toplam_girdi} girdi + {toplam_cikti} cikti token ~ ${maliyet:.4f}")
