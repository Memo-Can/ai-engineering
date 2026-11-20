"""Hafta 5 - Script 4: metadata filtresi (Hafta 4'teki sehir sorununun cozumu) ve HNSW indeksi.

Bolum A: ayni ilanlar, bu sefer sehir ayri bir SUTUNDA; arama WHERE ile daraltilir, anlam vektore birakilir.
Bolum B: HNSW indeksi. 12 satirda indekse gerek yok; ne ise yaradigini gormek icin 20.000 SENTETIK vektorle
         olcuyoruz (anlamsiz, yalniz hiz/plan/geri-getirme olcumu icin). Iki veri turu: tamamen rastgele ve KUMELI.
"""

import importlib.util
import time
from pathlib import Path

import numpy as np
from db import baglan
from ortak import embed_et

# Hafta 4'un ortak.py'sini farkli bir adla yukle (ayni dosya adi hafta5'te de var).
_spec = importlib.util.spec_from_file_location("ortak_h4", Path(__file__).resolve().parent.parent / "hafta4" / "ortak.py")
h4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h4)

con = baglan()

# ---------------------------------------------------------------------------
# BOLUM A: metadata filtresi
# ---------------------------------------------------------------------------
CALISMA = {1: "hibrit", 2: "uzaktan", 3: "ofis", 4: "uzaktan", 11: "ofis"}  # ilan metinlerinden; digerleri belirtilmemis

con.execute("DROP TABLE IF EXISTS ilanlar")
con.execute(
    """
    CREATE TABLE ilanlar (
        id serial PRIMARY KEY, sirket text, pozisyon text, sehir text, calisma text,
        metin text, embedding vector(384) NOT NULL
    )
    """
)
vek = embed_et([f"{i['pozisyon']}. {i['metin']}" for i in h4.ILANLAR])  # Hafta 4'tekiyle ayni metin: sehir YOK
for i, v in zip(h4.ILANLAR, vek):
    con.execute(
        "INSERT INTO ilanlar (id, sirket, pozisyon, sehir, calisma, metin, embedding) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (i["id"], i["sirket"], i["pozisyon"], i["sehir"], CALISMA.get(i["id"], "belirtilmemis"), i["metin"], v),
    )


def ara(soru: str, filtre_sql: str = "", parametre: tuple = (), k: int = 4) -> None:
    q = embed_et([soru])[0]
    sql = f"""SELECT id, pozisyon, sehir, calisma, 1 - (embedding <=> %s) AS benzerlik
              FROM ilanlar {filtre_sql} ORDER BY embedding <=> %s LIMIT {k}"""
    for id_, poz, sehir, calisma, b in con.execute(sql, (q, *parametre, q)).fetchall():
        print(f"    {b:.2f}  #{id_:>2} {poz} ({sehir}, {calisma})")


print("=== A) METADATA FILTRESI ===")
soru = "İzmir'de ofiste çalışılan bir iş var mı?"
print(f"\nSORU: {soru}\n  filtresiz (Hafta 4'teki gibi, yalniz anlam):")
ara(soru)
print("  WHERE sehir = 'İzmir':")
ara(soru, "WHERE sehir = %s", ("İzmir",))

soru = "Python bilen biri için uzaktan çalışılabilen bir iş"
print(f"\nSORU: {soru}\n  filtresiz:")
ara(soru, k=3)
print("  WHERE calisma = 'uzaktan':")
ara(soru, "WHERE calisma = %s", ("uzaktan",), k=3)

# ---------------------------------------------------------------------------
# BOLUM B: HNSW indeksi
# ---------------------------------------------------------------------------
print("\n\n=== B) HNSW INDEKSI (20.000 sentetik vektor, 384 boyut) ===")
N, D, SORGU = 20000, 384, 50
rng = np.random.default_rng(42)


def normla(x: np.ndarray) -> np.ndarray:
    return (x / np.linalg.norm(x, axis=1, keepdims=True)).astype(np.float32)


def boyut(tablo: str) -> str:
    return con.execute("SELECT pg_size_pretty(pg_total_relation_size(%s::regclass))", (tablo,)).fetchone()[0]


def plan_dugumu(sql: str, param) -> str:
    """EXPLAIN ciktisindaki ilk 'Scan' iceren satir: Seq Scan mi, Index Scan mi?"""
    satirlar = [r[0].strip() for r in con.execute("EXPLAIN " + sql, (param,)).fetchall()]
    return next((s.split("  (")[0] for s in satirlar if "Scan" in s), "?")


def deney(ad: str, veri: np.ndarray, sorgular: np.ndarray) -> None:
    print(f"\n--- {ad} ---")
    con.execute("DROP TABLE IF EXISTS sentetik")
    con.execute("CREATE TABLE sentetik (id int PRIMARY KEY, embedding vector(384))")
    with con.cursor() as cur, cur.copy("COPY sentetik (id, embedding) FROM STDIN WITH (FORMAT BINARY)") as cp:
        cp.set_types(["int4", "vector"])
        for i, v in enumerate(veri):
            cp.write_row((i, v))
    sql = "SELECT id FROM sentetik ORDER BY embedding <=> %s LIMIT 10"

    def olc() -> tuple[float, list[set]]:
        sonuclar, t0 = [], time.perf_counter()
        for q in sorgular:
            sonuclar.append({r[0] for r in con.execute(sql, (q,)).fetchall()})
        return (time.perf_counter() - t0) / len(sorgular) * 1000, sonuclar

    tam_ms, tam = olc()
    print(f"indeksiz : {tam_ms:5.1f} ms/sorgu | dogruluk %100 (referans) | plan: {plan_dugumu(sql, sorgular[0])} | tablo {boyut('sentetik')}")
    t0 = time.perf_counter()
    con.execute("CREATE INDEX sentetik_hnsw ON sentetik USING hnsw (embedding vector_cosine_ops)")
    ins = time.perf_counter() - t0
    for ef in (40, 100, 400):
        con.execute(f"SET hnsw.ef_search = {ef}")
        ms, sonuc = olc()
        geri = np.mean([len(a & b) / 10 for a, b in zip(sonuc, tam)])
        print(f"HNSW ef={ef:<4}: {ms:5.1f} ms/sorgu | geri getirme (recall@10) %{100 * geri:3.0f} | plan: {plan_dugumu(sql, sorgular[0])}")
    print(f"(indeks {ins:.1f} sn'de kuruldu, tablo+indeks {boyut('sentetik')})")


# 1) Tamamen rastgele: 384 boyutta her nokta hemen hemen herkese ayni uzaklikta; yapi yok.
deney("RASTGELE vektorler (yapisiz)", normla(rng.standard_normal((N, D))), normla(rng.standard_normal((SORGU, D))))

# 2) Kumeli: 200 merkez, her nokta bir merkez + kucuk gurultu; gercek metinlerde konu kumeleri vardir.
merkez = normla(rng.standard_normal((200, D)))
kume = lambda n: normla(merkez[rng.integers(0, 200, n)] + 0.35 * rng.standard_normal((n, D)) / np.sqrt(D) * 4)
deney("KUMELI vektorler (200 konu kumesi)", kume(N), kume(SORGU))

# Kucuk tabloda planlayici indeksi kullanir mi? 12 satirlik ilanlar tablosuna da indeks koyup bakalim.
con.execute("CREATE INDEX ilanlar_hnsw ON ilanlar USING hnsw (embedding vector_cosine_ops)")
print("\n12 satirlik ilanlar tablosu (HNSW indeksi VAR) plan:",
      plan_dugumu("SELECT id FROM ilanlar ORDER BY embedding <=> %s LIMIT 4", embed_et(["x"])[0]))
