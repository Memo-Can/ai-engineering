"""Hafta 5 - Script 3: parcalari pgvector tablosuna yazmak ve SQL ile anlamsal arama yapmak.

Hafta 4'te vektorler bir numpy matrisindeydi ve program kapaninca kayboluyordu.
Simdi ayni vektorler PostgreSQL'de, bir tablonun satirlarinda duruyor.
"""

import numpy as np
from db import baglan
from ortak import EL_KITABI, SORULAR, bolum_bazli, embed_et, kosinus

con = baglan()

# 1) TABLO: her satir bir parca. embedding sutunu vector(384): tam 384 sayi tutar, baska boyut hata verir.
con.execute("DROP TABLE IF EXISTS parcalar")
con.execute(
    """
    CREATE TABLE parcalar (
        id        serial PRIMARY KEY,
        bolum     text NOT NULL,
        metin     text NOT NULL,
        embedding vector(384) NOT NULL
    )
    """
)

# 2) INDEKSLEME: parcala, embed et, satir satir yaz.
parcalar = bolum_bazli(EL_KITABI, 450)
vektorler = embed_et(parcalar)
for metin, v in zip(parcalar, vektorler):
    bolum = metin.split(":", 1)[0]
    con.execute("INSERT INTO parcalar (bolum, metin, embedding) VALUES (%s, %s, %s)", (bolum, metin, v))

print(con.execute("SELECT count(*) FROM parcalar").fetchone()[0], "parca yazildi")
print("vektor boyutu:", con.execute("SELECT vector_dims(embedding) FROM parcalar LIMIT 1").fetchone()[0])
print("tablo boyutu :", con.execute("SELECT pg_size_pretty(pg_total_relation_size('parcalar'))").fetchone()[0])

# 3) SORGU: soruyu embed et, '<=>' kosinus MESAFESI (0 = ayni yon). Benzerlik = 1 - mesafe.
print("\n--- SQL ile arama: ORDER BY embedding <=> sorgu LIMIT 3 ---")
for soru, cevap in SORULAR[:3]:
    q = embed_et([soru])[0]
    satirlar = con.execute(
        "SELECT id, bolum, embedding <=> %s AS mesafe, metin FROM parcalar ORDER BY embedding <=> %s LIMIT 3", (q, q)
    ).fetchall()
    print(f"\nSORU: {soru}")
    for id_, bolum, mesafe, metin in satirlar:
        isaret = "<-- cevap burada" if cevap in metin else ""
        print(f"  #{id_} {bolum:<18} mesafe {mesafe:.3f} (benzerlik {1 - mesafe:.2f}) {isaret}")

# 4) DOGRULAMA: Hafta 4'teki numpy hesabiyla ayni siralama mi?
print("\n--- numpy ile ayni mi? (7 soru, en yakin 1 parca) ---")
ayni = 0
for soru, _ in SORULAR:
    q = embed_et([soru])[0]
    sql_id = con.execute("SELECT id FROM parcalar ORDER BY embedding <=> %s LIMIT 1", (q,)).fetchone()[0]
    np_id = 1 + int(np.argmax([kosinus(q, v) for v in vektorler]))  # serial id 1'den baslar
    ayni += sql_id == np_id
print(f"SQL ve numpy ayni parcayi buldu: {ayni}/{len(SORULAR)}")

# 5) Uc mesafe operatorunun ayni iki vektordeki degerleri.
a, b = vektorler[0], vektorler[1]
print("\n--- mesafe operatorleri (parca 1 ile parca 2) ---")
for ad, op in [("<=> kosinus mesafesi", "<=>"), ("<-> oklid (L2) mesafesi", "<->"), ("<#> negatif ic carpim", "<#>")]:
    print(f"  {ad:<26}", round(con.execute(f"SELECT %s::vector {op} %s::vector", (a, b)).fetchone()[0], 4))
print(f"  numpy kosinus benzerligi   {kosinus(a, b):.4f}  (1 - mesafe ile ayni olmali)")
