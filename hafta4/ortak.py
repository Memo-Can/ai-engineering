"""Hafta 4 - ortak parcalar: ornek ilanlar, embedding modeli ve yardimci fonksiyonlar.

Veri tamamen uydurmadir (egitim amacli); sirketler gercek degildir.
"""

from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

EMBEDDING_MODELI = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# fastembed varsayilan olarak onbellegi /tmp'ye koyar; yeniden baslatinca silinir. Kalici klasor kullaniyoruz.
ONBELLEK = str(Path.home() / ".cache" / "fastembed")

ILANLAR = [
    {"id": 1, "sirket": "Acme Yazılım", "pozisyon": "Backend Geliştirici", "sehir": "İstanbul",
     "metin": "Ödeme sistemleri üzerinde çalışan 8 kişilik bir ekibe katılacak backend geliştirici arıyoruz. "
              "Python ve Django ile servisleri yazacak, PostgreSQL üzerinde veri modellerini tasarlayacaksın. "
              "Haftada üç gün ofiste çalışıyoruz."},
    {"id": 2, "sirket": "BulutKod Teknoloji", "pozisyon": "Frontend Geliştirici", "sehir": "Ankara",
     "metin": "Yönetim paneli ve tasarım sistemi geliştirecek, kullanıcı arayüzlerini React ve TypeScript ile "
              "yazacak bir arkadaş arıyoruz. Tamamen uzaktan çalışabilirsin."},
    {"id": 3, "sirket": "Veri Atölyesi", "pozisyon": "Python Geliştirici", "sehir": "İzmir",
     "metin": "Veri hatları ve API'ler yazacak, FastAPI ve Redis ile hızlı servisler geliştirecek birini "
              "arıyoruz. Ekibimiz ofiste çalışıyor."},
    {"id": 4, "sirket": "Nova Bilişim", "pozisyon": "Full Stack Geliştirici", "sehir": "İstanbul",
     "metin": "SaaS ürünümüzde uçtan uca çalışacak, sunucu tarafını Django ile, arayüzü React ile yazacak bir "
              "geliştirici arıyoruz. Uzaktan çalışma mümkün."},
    {"id": 5, "sirket": "Kuzey Dijital", "pozisyon": "DevOps Mühendisi", "sehir": "Bursa",
     "metin": "Yazılımların otomatik olarak test edilip yayına alınmasını sağlayacak, bulut altyapısını yönetecek "
              "bir mühendis arıyoruz. Docker ve Kubernetes tecrübesi artı."},
    {"id": 6, "sirket": "Mavi Mobil", "pozisyon": "Mobil Geliştirici", "sehir": "İstanbul",
     "metin": "Hem iOS hem Android için tek kod tabanıyla uygulama geliştirecek, Flutter bilen bir arkadaş "
              "arıyoruz."},
    {"id": 7, "sirket": "Analitik Lab", "pozisyon": "Veri Analisti", "sehir": "Ankara",
     "metin": "Satış verilerini inceleyecek, raporlar ve gösterge panelleri hazırlayacak, SQL ve Excel'e hâkim bir "
              "analist arıyoruz."},
    {"id": 8, "sirket": "Yapay Zeka Stüdyosu", "pozisyon": "AI Mühendisi", "sehir": "İstanbul",
     "metin": "Büyük dil modelleriyle müşteri destek asistanı geliştirecek, soru-cevap sistemini kuracak bir "
              "mühendis arıyoruz. Python bilgisi şart."},
    {"id": 9, "sirket": "SiberKalkan", "pozisyon": "Güvenlik Mühendisi", "sehir": "Ankara",
     "metin": "Uygulamalarımızdaki güvenlik açıklarını tespit edecek, sızma testleri yapacak ve ekibe güvenli kod "
              "yazma konusunda destek olacak birini arıyoruz."},
    {"id": 10, "sirket": "Oyun Fabrikası", "pozisyon": "Oyun Geliştirici", "sehir": "İzmir",
     "metin": "Mobil oyunlarımızın mekaniklerini kodlayacak, Unity ve C# ile çalışacak bir arkadaş arıyoruz."},
    {"id": 11, "sirket": "Lojistik Plus", "pozisyon": "Backend Geliştirici", "sehir": "Bursa",
     "metin": "Kargo takip sistemimizin sunucu tarafını geliştirecek, Java ve Spring tecrübesi olan bir arkadaş "
              "arıyoruz. Ofiste çalışıyoruz."},
    {"id": 12, "sirket": "Eğitim Köprüsü", "pozisyon": "Teknik İçerik Yazarı", "sehir": "Ankara",
     "metin": "Yazılım eğitimleri için içerik hazırlayacak, kodlamayı anlaşılır biçimde anlatmayı seven birini "
              "arıyoruz."},
]

_model = None


def model_getir() -> TextEmbedding:
    """Modeli bir kez yukler (ilk calistirmada indirir) ve tekrar kullanir."""
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODELI, cache_dir=ONBELLEK)
    return _model


def embed_et(metinler: list[str]) -> np.ndarray:
    """Metin listesini (n, 384) boyutlu bir matrise cevirir; her satir bir metnin vektoru."""
    return np.array(list(model_getir().embed(metinler)))


def kosinus(a: np.ndarray, b: np.ndarray) -> float:
    """Iki vektorun kosinus benzerligi: 1'e yakin = ayni yonde (anlamca yakin), 0'a yakin = ilgisiz."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def indeks_olustur() -> np.ndarray:
    """INDEKSLEME: her ilanin embedding'ini hesaplar. Sonuc (ilan sayisi, 384) matrisidir."""
    return embed_et([f"{i['pozisyon']}. {i['metin']}" for i in ILANLAR])


def anlamsal_ara(sorgu: str, indeks: np.ndarray, k: int = 3):
    """SORGU: sorunun embedding'ini hesaplar, tum ilanlarla benzerligi olcer, en yakin k ilani (puan, ilan) dondurur."""
    q = embed_et([sorgu])[0]
    puanlar = [(kosinus(q, v), ilan) for v, ilan in zip(indeks, ILANLAR)]
    puanlar.sort(key=lambda x: -x[0])
    return puanlar[:k]
