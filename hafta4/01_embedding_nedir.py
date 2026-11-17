"""Hafta 4 - Script 1: embedding uretmek ve benzerligi olcmek.

Cumleleri vektore ceviririz, sonra her cift icin kosinus benzerligini yazdiririz.
"""

import numpy as np
from ortak import embed_et, kosinus

CUMLELER = [
    "Python ile web sitesi geliştirmek",          # 0
    "Django kullanarak web uygulaması yazmak",    # 1  (0'a cok yakin anlam)
    "Bulut sunucularını yönetmek",                # 2  (ilgili ama farkli is)
    "Kedi mamasını rafa koydum",                  # 3  (tamamen ilgisiz)
    "Bugün hava çok güzel",                       # 4
    "The weather is very nice today",             # 5  (4'un Ingilizcesi: ayni anlam, baska dil)
]

vektorler = embed_et(CUMLELER)

print(f"Matris sekli: {vektorler.shape}  -> {vektorler.shape[0]} cumle, her biri {vektorler.shape[1]} sayi")
print(f"Ilk cumlenin ilk 5 sayisi: {np.round(vektorler[0][:5], 4)}")
print(f"Ilk cumlenin vektor uzunlugu (norm): {np.linalg.norm(vektorler[0]):.3f}\n")

print("Kosinus benzerligi (satir x sutun):")
print("      " + "".join(f"  [{i}] " for i in range(len(CUMLELER))))
for i, a in enumerate(vektorler):
    satir = "".join(f" {kosinus(a, b):5.2f}" for b in vektorler)
    print(f"  [{i}] {satir}")

print("\nSecilmis ciftler:")
for i, j in [(0, 1), (0, 2), (0, 3), (4, 5), (4, 3)]:
    print(f"  {kosinus(vektorler[i], vektorler[j]):5.2f}  |  {CUMLELER[i]!r}  <->  {CUMLELER[j]!r}")
