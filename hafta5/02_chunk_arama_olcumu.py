"""Hafta 5 - Script 2: hangi chunking stratejisi cevabi daha iyi bulduruyor? (olcum)

Her strateji icin: parcalari embed et, 7 soruyu sor, en yakin parcaya bak.
Basari olcutu: en yakin 1 (ya da 3) parcanin METNINDE cevabin gectigi ifade var mi?
"""

from ortak import EL_KITABI, MAKS_TOKEN, SORULAR, bolum_bazli, embed_et, kosinus, model_getir, sabit_boyut

STRATEJILER = {
    "D) 1000 karakter": sabit_boyut(EL_KITABI, 1000, 0),
    "A) 500 karakter": sabit_boyut(EL_KITABI, 500, 0),
    "B) 500 + 100 ortusme": sabit_boyut(EL_KITABI, 500, 100),
    "C) bolum bazli": bolum_bazli(EL_KITABI, 450),
    "C') bolum bazli, basliksiz": bolum_bazli(EL_KITABI, 450, baslik_ekle=False),
}

sorular = [s for s, _ in SORULAR]
q_vek = embed_et(sorular)

print(f"{len(SORULAR)} soru | basari = en yakin parcanin metninde cevap ifadesi geciyor mu\n")
print(f"{'strateji':<26}{'parca':>6}{'top-1':>8}{'top-3':>8}")

ayrinti = {}
for ad, parcalar in STRATEJILER.items():
    p_vek = embed_et(parcalar)
    top1 = top3 = 0
    satirlar = []
    for (soru, cevap), q in zip(SORULAR, q_vek):
        sira = sorted(((kosinus(q, v), i) for i, v in enumerate(p_vek)), key=lambda x: -x[0])
        ilk3 = [i for _, i in sira[:3]]
        bulundu1 = cevap in parcalar[ilk3[0]]
        bulundu3 = any(cevap in parcalar[i] for i in ilk3)
        top1 += bulundu1
        top3 += bulundu3
        satirlar.append((soru, sira[0][0], bulundu1))
    ayrinti[ad] = satirlar
    print(f"{ad:<26}{len(parcalar):>6}{top1:>5}/{len(SORULAR)}{top3:>5}/{len(SORULAR)}")

print("\n--- C) bolum bazli: soru soru ---")
for soru, puan, ok in ayrinti["C) bolum bazli"]:
    print(f"  {'OK ' if ok else 'YOK'} {puan:.2f}  {soru}")

print("\n--- TEK VEKTOR neden yetmez: sorunun belgeyle ve en iyi parcayla benzerligi ---")
doc_vek = embed_et([EL_KITABI])[0]
c_parca = embed_et(bolum_bazli(EL_KITABI, 450))
for (soru, _), q in zip(SORULAR, q_vek):
    en_iyi = max(kosinus(q, v) for v in c_parca)
    print(f"  belge: {kosinus(q, doc_vek):5.2f} | en iyi parca: {en_iyi:5.2f}  {soru}")

# Belge vektoru gercekte belgenin yalnizca ilk 128 token'ini mi temsil ediyor? Ilk 128 token'in metniyle karsilastiralim.
tok = model_getir().model.tokenizer
tok.no_truncation()
ids = tok.encode(EL_KITABI).ids
ilk128 = tok.decode(ids[1:MAKS_TOKEN - 1])  # bastaki/sondaki ozel tokenlari atlayip 126 icerik token'i
tok.enable_truncation(max_length=MAKS_TOKEN)
bas = embed_et([ilk128])[0]
print(f"\nBelge {len(ids)} token; vektor yalnizca ilk {MAKS_TOKEN} tanesini (%{100 * MAKS_TOKEN / len(ids):.0f}) gordu.")
print(f"Belge vektoru ile 'sadece ilk {MAKS_TOKEN} token' vektoru arasindaki benzerlik: {kosinus(doc_vek, bas):.3f} (1.000 = geri kalan hic girmedi)")
