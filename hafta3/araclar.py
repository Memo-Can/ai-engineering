"""Hafta 3 - ortak parcalar: ornek ilan verisi, arac fonksiyonlari ve arac sozlugu (schema).

Veri tamamen uydurmadir (egitim amacli); sirketler ve maaslar gercek degildir.
"""

import json

MODEL = "claude-haiku-4-5-20251001"

ILANLAR = [
    {"id": 1, "sirket": "Acme Yazılım", "pozisyon": "Backend Geliştirici", "sehir": "İstanbul",
     "calisma_sekli": "hibrit", "teknolojiler": ["Python", "Django", "PostgreSQL"],
     "maas_min": 90000, "maas_max": 120000,
     "aciklama": "Ödeme sistemleri üzerinde çalışan 8 kişilik bir ekip."},
    {"id": 2, "sirket": "BulutKod Teknoloji", "pozisyon": "Frontend Geliştirici", "sehir": "Ankara",
     "calisma_sekli": "uzaktan", "teknolojiler": ["React", "TypeScript"],
     "maas_min": 70000, "maas_max": 95000,
     "aciklama": "Tasarım sistemi ve yönetim paneli geliştirme."},
    {"id": 3, "sirket": "Veri Atölyesi", "pozisyon": "Python Geliştirici", "sehir": "İzmir",
     "calisma_sekli": "ofis", "teknolojiler": ["Python", "FastAPI", "Redis"],
     "maas_min": 80000, "maas_max": 100000,
     "aciklama": "Veri hatları ve API geliştirme."},
    {"id": 4, "sirket": "Nova Bilişim", "pozisyon": "Full Stack Geliştirici", "sehir": "İstanbul",
     "calisma_sekli": "uzaktan", "teknolojiler": ["Django", "React", "Docker"],
     "maas_min": 100000, "maas_max": 140000,
     "aciklama": "SaaS ürününde uçtan uca geliştirme."},
    {"id": 5, "sirket": "Kuzey Dijital", "pozisyon": "DevOps Mühendisi", "sehir": "Bursa",
     "calisma_sekli": "hibrit", "teknolojiler": ["Docker", "Kubernetes", "Python"],
     "maas_min": 95000, "maas_max": 130000,
     "aciklama": "CI/CD ve bulut altyapısı."},
]


def _bul(teknoloji: str) -> list[dict]:
    t = teknoloji.strip().lower()
    return [i for i in ILANLAR if any(t == x.lower() for x in i["teknolojiler"])]


def ilan_ara(teknoloji: str) -> str:
    """Bir teknolojiyi isteyen ilanlarin ozet listesini JSON olarak dondurur."""
    sonuc = [{"id": i["id"], "sirket": i["sirket"], "pozisyon": i["pozisyon"], "sehir": i["sehir"]}
             for i in _bul(teknoloji)]
    return json.dumps(sonuc, ensure_ascii=False)


def ortalama_maas(teknoloji: str) -> str:
    """Bir teknolojiyi isteyen ilanlarin ortalama (min+max)/2 maasini dondurur."""
    ilanlar = _bul(teknoloji)
    if not ilanlar:
        raise ValueError(f"'{teknoloji}' icin ilan bulunamadi")
    ort = sum((i["maas_min"] + i["maas_max"]) / 2 for i in ilanlar) / len(ilanlar)
    return json.dumps({"teknoloji": teknoloji, "ilan_sayisi": len(ilanlar), "ortalama_maas_tl": round(ort)})


def ilan_detay(ilan_id: int) -> str:
    """Bir ilanin tum alanlarini dondurur."""
    for i in ILANLAR:
        if i["id"] == ilan_id:
            return json.dumps(i, ensure_ascii=False)
    raise ValueError(f"{ilan_id} numarali ilan yok")


FONKSIYONLAR = {"ilan_ara": ilan_ara, "ortalama_maas": ortalama_maas, "ilan_detay": ilan_detay}

ARACLAR = [
    {
        "name": "ilan_ara",
        "description": "Verilen teknolojiyi (ornegin Python, Django) isteyen is ilanlarini listeler. "
                       "Sadece ozet doner: id, sirket, pozisyon, sehir.",
        "input_schema": {
            "type": "object",
            "properties": {"teknoloji": {"type": "string", "description": "Teknoloji adi, tek kelime"}},
            "required": ["teknoloji"],
        },
    },
    {
        "name": "ortalama_maas",
        "description": "Verilen teknolojiyi isteyen ilanlarin ortalama maasini (TL, net) hesaplar.",
        "input_schema": {
            "type": "object",
            "properties": {"teknoloji": {"type": "string", "description": "Teknoloji adi, tek kelime"}},
            "required": ["teknoloji"],
        },
    },
    {
        "name": "ilan_detay",
        "description": "Bir ilanin tum bilgilerini (maas araligi, calisma sekli, aciklama dahil) getirir.",
        "input_schema": {
            "type": "object",
            "properties": {"ilan_id": {"type": "integer", "description": "ilan_ara'dan gelen id"}},
            "required": ["ilan_id"],
        },
    },
]


def arac_calistir(ad: str, girdi: dict) -> dict:
    """Modelin istedigi araci calistirir; hata olursa is_error=True ile geri bildirir."""
    try:
        return {"content": FONKSIYONLAR[ad](**girdi), "is_error": False}
    except Exception as e:  # noqa: BLE001 - hatayi modele metin olarak iletiyoruz
        return {"content": f"Arac hatasi: {e}", "is_error": True}
