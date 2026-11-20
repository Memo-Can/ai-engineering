"""Hafta 5 - Script 1: ayni el kitabini uc stratejiyle parcalamak ve parcalari token sayisiyla olcmek.

Model sadece ilk 128 token'i gorur. Bir parca bundan uzunsa SONU embedding'e hic girmez (Hafta 4, Tuzak 3).
Bu yuzden chunk boyutunu karakterle degil TOKENLA dusunmek gerekir.
"""

from ortak import EL_KITABI, MAKS_TOKEN, bolum_bazli, sabit_boyut, token_say


def ozet(ad: str, parcalar: list[str]) -> None:
    tokenlar = [token_say(p) for p in parcalar]
    kesilen = sum(t > MAKS_TOKEN for t in tokenlar)
    print(f"\n=== {ad} ===")
    print(f"parca sayisi: {len(parcalar)} | token min/ort/maks: {min(tokenlar)}/{sum(tokenlar) // len(tokenlar)}/{max(tokenlar)} "
          f"| {MAKS_TOKEN} token'i asan (sonu kesilen) parca: {kesilen}")
    for i, (p, t) in enumerate(zip(parcalar[:3], tokenlar[:3])):
        isaret = "  <-- KESILIYOR" if t > MAKS_TOKEN else ""
        print(f"  [{i}] ({t} token){isaret}\n      {p[:110]!r}...  ...{p[-60:]!r}")


print(f"Belge: {len(EL_KITABI)} karakter, {token_say(EL_KITABI)} token (model en fazla {MAKS_TOKEN} gorur)")

ozet("D) sabit boyut: 1000 karakter (cok buyuk parca)", sabit_boyut(EL_KITABI, 1000, 0))
ozet("A) sabit boyut: 500 karakter, ortusme yok", sabit_boyut(EL_KITABI, 500, 0))
ozet("B) sabit boyut: 500 karakter, 100 karakter ortusme", sabit_boyut(EL_KITABI, 500, 100))
ozet("C) bolum bazli: baslik + cumle sinirlari, en fazla 450 karakter", bolum_bazli(EL_KITABI, 450))

# Sabit boyutun cumleyi ortasindan kestigini gosterelim.
print("\n--- A stratejisinde parcalarin birlesim noktalari ---")
a = sabit_boyut(EL_KITABI, 500, 0)
for i in range(3):
    print(f"  parca {i} biter: ...{a[i][-45:]!r}")
    print(f"  parca {i + 1} baslar: {a[i + 1][:45]!r}...")
