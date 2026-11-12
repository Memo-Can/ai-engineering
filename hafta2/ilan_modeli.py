"""Hafta 2 - ortak parcalar: pydantic modeli ve ornek ilanlar."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

MODEL = "claude-haiku-4-5-20251001"


class Ilan(BaseModel):
    """Bir is ilanindan cikarilacak alanlar."""

    sirket: str
    pozisyon: str
    lokasyon: Optional[str] = Field(default=None, description="Sehir; belirtilmemisse null")
    calisma_sekli: Literal["ofis", "hibrit", "uzaktan", "belirtilmemis"]
    teknolojiler: list[str] = Field(description="Ilanda gecen teknoloji ve araclar")
    deneyim_yili: Optional[int] = Field(default=None, description="Istenen minimum yil; yoksa null")
    maas_var_mi: bool = Field(description="Ilanda maas veya maas araligi acikca yaziyor mu")


ILAN_1 = """\
Acme Yazılım İstanbul'da backend geliştirici arıyor.
Hibrit çalışma modeli (haftada 3 gün ofis). En az 3 yıl deneyim istiyoruz.
Python, Django ve PostgreSQL bilgisi şart; Docker ve Redis bilmen artı.
Maaş: 90.000 - 120.000 TL net.
"""

# Zor ornek: sirket adi sondan belli, calisma sekli ima ediliyor, maas yok, teknolojiler cumle icinde
ILAN_2 = """\
Ekibimize katılacak bir yazılımcı arıyoruz. Günlük işlerin çoğunu evden yürütüyoruz, ayda bir
ortak ofiste buluşuyoruz. React ve TypeScript ile arayüz yazacak, gerekirse Node.js tarafına da
dokunacaksın. Önceki deneyimin 2 yıldan az olabilir, öğrenmeye açık olman yeterli.
Başvurular için: ik@bulutkod.example — BulutKod Teknoloji, Ankara.
"""
