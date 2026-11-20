"""Hafta 5 - ortak parcalar: ornek el kitabi, chunking fonksiyonlari ve embedding yardimcilari.

Metin tamamen uydurmadir (egitim amacli); sirket gercek degildir.
Embedding kismi Hafta 4'tekiyle ayni modeli kullanir (kopyasi burada, boylece hafta5 tek basina calisir).
"""

import re
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

EMBEDDING_MODELI = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ONBELLEK = str(Path.home() / ".cache" / "fastembed")
MAKS_TOKEN = 128  # modelin gorebildigi azami token; fazlasi sagdan kesilir (Hafta 4, Tuzak 3)

# ---------------------------------------------------------------------------
# Ornek belge: kurgusal bir sirketin calisan el kitabi. Cevaplar belgenin farkli yerlerine dagitilmistir.
# ---------------------------------------------------------------------------
EL_KITABI = """# Kuzey Yazılım Çalışan El Kitabı

## Hoş geldin
Kuzey Yazılım, küçük ve hızlı ilerleyen bir ürün şirketidir. Bu el kitabı ilk haftanda ihtiyaç duyacağın kuralları ve alışkanlıkları toplar. Kitabı baştan sona okumak zorunda değilsin; ihtiyaç duyduğunda ilgili bölüme bakman yeterli. Bir bölüm eksik ya da belirsizse ekip liderine ya da insan kaynaklarına yazabilirsin.

## İzin politikası
Her çalışan ilk yıl 14 iş günü ücretli yıllık izin kullanır. Beşinci yılın sonunda bu süre 20 iş gününe çıkar. İzin talepleri en az iki hafta önceden takım takvimine girilir ve ekip lideri onaylar. Kullanılmayan izinlerin en fazla beş günü ertesi yıla devredilebilir. Hastalık izni için rapor gerekir; üç güne kadar raporsuz mazeret izni için doğrudan ekip liderine bilgi verilir.

## Uzaktan çalışma
Ekipler haftada en fazla iki gün uzaktan çalışabilir; kalan günlerde ofise gelmek beklenir. Uzaktan çalıştığın günlerde ekip sohbetinde görünür olman ve toplantılara kamerayla katılman beklenir. Evden çalışmayı seçen herkese aylık 600 TL internet ve elektrik desteği ödenir. Bu destek bordroda ayrı bir kalem olarak görünür ve fatura istemez. Başka bir şehirden tamamen uzaktan çalışmak isteyenler insan kaynaklarıyla ayrı bir görüşme yapar.

## Ekipman
Her yeni çalışana bir dizüstü bilgisayar, ikinci bir ekran ve kulaklık verilir. Dizüstü bilgisayarlar 3 yılda bir yenilenir; arızalı cihazlar için bilgi işlem ekibine talep açılır. Şirket cihazına izinsiz yazılım kurulmaz. Cihazın kaybolması ya da çalınması durumunda aynı gün güvenlik ekibine haber verilir ki uzaktan silinebilsin.

## Kod geliştirme süreci
Ana dala doğrudan kod gönderilmez. Her değişiklik bir çekme isteğiyle açılır ve en az iki kişi tarafından incelenir; inceleyenlerden biri değişikliğin yapıldığı modülün sahibi olmalıdır. Testleri geçmeyen değişiklik birleştirilemez. Küçük ve sık değişiklik göndermeyi tercih ediyoruz; bin satırı aşan bir çekme isteği genellikle bölünmesi gerektiğinin işaretidir. Sürüm yayını her salı ve perşembe öğleden sonra yapılır.

## Nöbet ve olay yönetimi
Canlı sistemde bir sorun olduğunda ilk bakan kişi nöbetçi mühendistir. Nöbet haftalık ve dönüşümlüdür; sırası ekip takviminde görünür. Nöbet haftasında gece 23.00 ile sabah 07.00 arasında gelen kritik uyarılara 15 dakika içinde yanıt vermek gerekir. Nöbet tutan çalışana hafta başına sabit bir nöbet primi ödenir ve nöbetin ertesi günü öğlene kadar izinli sayılır. Her olay sonrasında suçlayıcı olmayan bir olay değerlendirme belgesi yazılır.

## Yan haklar ve gelişim
Her çalışanın yıllık 15.000 TL eğitim bütçesi vardır; kitap, kurs, konferans bileti ve sertifika sınavları bu bütçeden karşılanır. Bütçe devretmez. Öğle yemeği ofiste ücretsizdir. Özel sağlık sigortası ilk günden başlar ve eş ile çocukları kapsar. Yılda iki kez performans görüşmesi yapılır; maaş değişiklikleri yalnızca ocak ve temmuz aylarında bordroya yansır.

## İşten ayrılma
İşten ayrılmak isteyen çalışan yazılı bildirim verir. İhbar süresi ilk iki yıl için 4 hafta, sonrası için 8 haftadır. Bu sürede bilgi aktarımı için bir devir planı hazırlanır. Son iş gününde şirket cihazları teslim edilir, hesap erişimleri kapatılır ve kullanılmayan izin günleri maaşla birlikte ödenir. Ayrılan çalışanlarla bir çıkış görüşmesi yapılır; amacımız deneyimini öğrenip şirketi geliştirmektir.
"""

# Her soru icin cevabin bulunmasi gereken ifade (belgede tam olarak gecen bir parca).
SORULAR = [
    ("Yıllık izin kaç gün?", "14 iş günü"),
    ("Evden çalışırsam internet masrafım karşılanıyor mu?", "600 TL"),
    ("Gece canlı sistemde hata çıkarsa kim bakıyor?", "nöbetçi mühendis"),
    ("İşten ayrılırken ihbar süresi ne kadar?", "4 hafta"),
    ("Kurs ve konferanslar için ne kadar bütçem var?", "15.000 TL"),
    ("Dizüstü bilgisayarım ne zaman yenilenir?", "3 yılda bir"),
    ("Kodumu birleştirmeden önce kaç kişi inceliyor?", "en az iki kişi"),
]

# ---------------------------------------------------------------------------
# Chunking stratejileri. Hepsi metni alir, parca (str) listesi dondurur.
# ---------------------------------------------------------------------------


def sabit_boyut(metin: str, boyut: int = 500, ortusme: int = 0) -> list[str]:
    """Metni karakter sayisina gore keser. ortusme > 0 ise komsu parcalar o kadar karakteri paylasir."""
    adim = boyut - ortusme
    return [metin[i : i + boyut].strip() for i in range(0, len(metin), adim) if metin[i : i + boyut].strip()]


def bolum_bazli(metin: str, azami_karakter: int = 450, baslik_ekle: bool = True) -> list[str]:
    """Markdown basliklarina gore boler; her parcanin basina bolum basligini yazar.

    Bolum azami_karakter'den uzunsa cumle sinirlarindan, kucuk parcalara boler. baslik_ekle=False ise baslik yazilmaz.
    """
    parcalar = []
    for bolum in re.split(r"\n(?=## )", metin):
        satirlar = bolum.strip().splitlines()
        baslik = satirlar[0].lstrip("# ").strip()
        govde = " ".join(satirlar[1:]).strip()
        if not govde:
            continue
        onek = f"{baslik}: " if baslik_ekle else ""
        cumleler = re.split(r"(?<=[.!?])\s+", govde)
        mevcut = ""
        for c in cumleler:
            if mevcut and len(mevcut) + len(c) + 1 > azami_karakter:
                parcalar.append(f"{onek}{mevcut}")
                mevcut = c
            else:
                mevcut = f"{mevcut} {c}".strip()
        if mevcut:
            parcalar.append(f"{onek}{mevcut}")
    return parcalar


# ---------------------------------------------------------------------------
# Embedding yardimcilari
# ---------------------------------------------------------------------------
_model = None


def model_getir() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODELI, cache_dir=ONBELLEK)
    return _model


def embed_et(metinler: list[str]) -> np.ndarray:
    """Metin listesini (n, 384) matrise cevirir; her satir bir metnin vektoru."""
    return np.array(list(model_getir().embed(metinler)))


def kosinus(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def token_say(metin: str) -> int:
    """Modelin kesmeden once gorecegi token sayisi (kesmeyi gecici olarak kapatir)."""
    tok = model_getir().model.tokenizer
    tok.no_truncation()
    n = len(tok.encode(metin).ids)
    tok.enable_truncation(max_length=MAKS_TOKEN)
    return n
