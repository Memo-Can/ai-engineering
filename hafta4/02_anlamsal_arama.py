"""Hafta 4 - Script 2: anlamsal arama ile anahtar kelime aramasini karsilastirma.

Iki asama vardir:
  INDEKSLEME (bir kez): her ilanin embedding'i hesaplanip saklanir.
  SORGU (her aramada)  : sorunun embedding'i hesaplanir, tum ilanlarla kosinus benzerligi olculur, en yakin k ilan doner.
"""

import re
import time

import numpy as np
from ortak import ILANLAR, embed_et, kosinus

K = 3  # kac sonuc gosterilecek


def kucult(metin: str) -> str:
    """Turkceye uygun kucuk harfe cevirme (I -> i, I -> i dotless sorununu onler)."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def anahtar_kelime_ara(sorgu: str, k: int = K):
    """Basit kelime eslestirme: sorgudaki 4+ harfli kelimelerden kac tanesi ilan metninde AYNEN geciyor."""
    kelimeler = {k_ for k_ in re.findall(r"\w+", kucult(sorgu)) if len(k_) >= 4}
    sonuc = []
    for ilan in ILANLAR:
        metin_kelimeleri = set(re.findall(r"\w+", kucult(ilan["pozisyon"] + " " + ilan["metin"])))
        puan = len(kelimeler & metin_kelimeleri)
        if puan > 0:
            sonuc.append((puan, ilan))
    sonuc.sort(key=lambda x: -x[0])
    return sonuc[:k]


# --- INDEKSLEME: bir kez yapilir ---
baslangic = time.time()
METINLER = [f"{i['pozisyon']}. {i['metin']}" for i in ILANLAR]
INDEKS = embed_et(METINLER)  # (12, 384)
print(f"Indeks hazir: {INDEKS.shape[0]} ilan, {INDEKS.shape[1]} boyut, {time.time() - baslangic:.2f} sn (model yukleme dahil)\n")


def anlamsal_ara(sorgu: str, k: int = K):
    """Sorgunun embedding'ini hesapla, tum ilanlarla benzerligi olc, en yakin k ilani dondur."""
    q = embed_et([sorgu])[0]
    puanlar = [(kosinus(q, v), ilan) for v, ilan in zip(INDEKS, ILANLAR)]
    puanlar.sort(key=lambda x: -x[0])
    return puanlar[:k]


SORGULAR = [
    "Python web uygulamaları yazıyorsun",
    "evden çalışabileceğim ön yüz işi",
    "yazılımları yayına alma ve sunucu yönetimi",
    "telefon uygulaması yapmak",
    "aşçı arıyoruz",
]

for sorgu in SORGULAR:
    print(f"SORGU: {sorgu!r}")
    print("  Anahtar kelime aramasi:")
    kw = anahtar_kelime_ara(sorgu)
    if not kw:
        print("    (eslesme yok)")
    for puan, ilan in kw:
        print(f"    {puan} ortak kelime | #{ilan['id']:>2} {ilan['pozisyon']} ({ilan['sirket']})")
    print("  Anlamsal arama:")
    for puan, ilan in anlamsal_ara(sorgu):
        print(f"    benzerlik {puan:5.2f} | #{ilan['id']:>2} {ilan['pozisyon']} ({ilan['sirket']})")
    print()
