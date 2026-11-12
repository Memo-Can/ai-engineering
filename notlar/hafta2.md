# AI Mühendisliği – Hafta 2: Structured Output (JSON)

Tarih: 2026-11-11

## 1. Amaç ve ön hazırlık

Bu hafta sonunda bir iş ilanı metnini alıp `şirket`, `pozisyon`, `teknolojiler` gibi alanları **doğrulanmış bir Python nesnesi** olarak döndüren bir script'in olacak. Hafta 1'de model cevabı serbest metindi; kodla işlemek için metni çözmek gerekirdi. Bu hafta modelden doğrudan makine okuyabilir veri almayı öğreniyoruz.

**Hafta sonu çıktısı:** `hafta2/` klasöründe 3 script (promptla JSON, pydantic ile doğrulama, şemayı zorlama) ve bu doküman.

**Ön hazırlık**

- [ ] Hafta 1 script'leri çalışıyor (`.env` içinde geçerli anahtar)
- [ ] Komutlar `ai-engineering` klasöründen `.venv/bin/python ...` ile çalıştırılır
- [ ] `pydantic` kurulu: `anthropic` paketi zaten getiriyor (bende 2.14.3); `requirements.txt`'e açıkça yazıldı

**Maliyet notu:** Bu haftanın script'leri küçük metinler kullandığı için yine Haiku ile birkaç sent tutar.

## 2. Temel kavramlar

Kodun bir sonraki adımı modelin cümlesini değil bir **değeri** bekler (örn. `sirket == "Acme"`). Serbest metinden bu değeri çıkarmak kırılgandır; bu yüzden modelden veriyi doğrudan JSON olarak isteriz ve gelen JSON'un beklenen biçimde olduğunu kodla doğrularız.

| Kavram | Ne demek | Neden önemli |
| --- | --- | --- |
| **JSON şema** | Alanların adlarını ve tiplerini tarif eden kural seti | Modele "tam olarak şu biçimde ver" demenin makine okunur yolu |
| **pydantic modeli** | Şemayı Python sınıfı olarak yazma ve gelen veriyi kontrol etme aracı | Tip hatası, eksik alan ve fazlalık çıktı anda yakalanır |
| **Doğrulama (validation)** | Gelen verinin şemaya uyduğunu kontrol etmek | Model yanlış biçimde cevap verirse kod bunu bilir |
| **Zorlama (constraining)** | Şemayı modelin üretim aşamasında uygulatmak | Doğrulama hatalarını azaltır ama tamamen ortadan kaldırdığını varsayma |

**Üç yöntem, artan güvenle**

| Yöntem | Nasıl | Zayıf noktası |
| --- | --- | --- |
| 1. Promptla iste | "Cevabı sadece JSON ver" yaz, `json.loads` ile oku | Model başa açıklama veya kod bloğu ekleyebilir, alan adı değiştirebilir |
| 2. Pydantic ile doğrula | Yöntem 1 + `Model.model_validate_json(...)`; hatalıysa yeniden dene | Hata yakalanır ama üretimi engellemez |
| 3. Şemayı API'ye ver | SDK'nın `messages.parse(..., output_format=Model)` çağrısı ya da tool use ile zorlanmış şema | Her model ve sürümde desteklenmeyebilir; uygulama 3'te Haiku ile denedik |

**Kural:** Üretimde yöntem 3'ü (varsa) kullan, yine de pydantic ile doğrula. Çünkü şema biçimi garanti edebilir ama **değerin doğruluğunu** (modelin yanlış şirket adı uydurması gibi) garanti etmez.

## 3. Uygulama 1: promptla JSON istemek

Prompta "cevabı sadece JSON ver" yazmak yetmedi: aynı istek 5 kez gönderildi ve **5 cevabın 5'inde de `json.loads` başarısız oldu**. Sebep: model JSON'u metin olarak değil, markdown kod bloğu içinde verdi (cevap ` ```json ` ile başlıyor). Dosya: `hafta2/01_promptla_json.py`.

Ortak parçalar `hafta2/ilan_modeli.py` içinde: pydantic modeli (`Ilan`) ve iki örnek ilan. `ILAN_2` kasıtlı olarak zor: şirket adı sonda, çalışma şekli ima ediliyor (günlük işler evden, ayda bir ofis), maaş yok, teknolojiler cümlenin içinde geçiyor.

```bash
.venv/bin/python hafta2/01_promptla_json.py
```

**Çıktı** (benim çalıştırmam; senin cevaplarının biçimi farklı olabilir):

```
#1 HATA json.loads basarisiz (Expecting value); cevabin ilk 60 karakteri: '```json\n{\n  "sirket": "BulutKod Teknoloji", ...
#2 ... #5 aynı hata

Sonuc: 0/5 cevap duz json.loads ile okundu
```

**Ders:** "Sadece JSON ver" talimatı **biçimi** garanti etmez. Cevabın içeriği doğru olabilir (şirket adı doğru çıktı) ama koda ulaşan metin geçerli JSON değil. Üretimde bu tek bir karakterle (`` ` ``) tüm akışı kırar. Yaması: kod bloğunu soyup tekrar parse etmek, ama bu çözüm kırılgandır; kalıcı çözüm 4. ve 5. bölümlerde.

## 4. Uygulama 2: pydantic ile doğrulama

Pydantic modeli (`Ilan`), şemayı Python sınıfı olarak tanımlar: hangi alanlar var, tipleri ne, hangi değerler geçerli. `Ilan.model_validate_json(metin)` gelen metni hem JSON olarak okur hem şemaya göre kontrol eder. Script: `hafta2/02_pydantic_dogrulama.py`.

```python
class Ilan(BaseModel):
    sirket: str
    pozisyon: str
    lokasyon: Optional[str] = None
    calisma_sekli: Literal["ofis", "hibrit", "uzaktan", "belirtilmemis"]
    teknolojiler: list[str]
    deneyim_yili: Optional[int] = None
    maas_var_mi: bool
```

**A) Bozuk JSON'u pydantic nasıl yakalar** (model çağrısı yok, ücretsiz; elle yazdığım bozuk bir örnek):

```
alan='calisma_sekli'  sorun: Input should be 'ofis', 'hibrit', 'uzaktan' or 'belirtilmemis'
alan='teknolojiler'   sorun: Input should be a valid array
alan='maas_var_mi'    sorun: Input should be a valid boolean, unable to interpret input
```

Hata mesajı hangi alanın neden geçersiz olduğunu tek tek söyler; bu mesajı modele geri verip düzeltmesini isteyebilirsin (script'teki `ilan_cikar` fonksiyonu bunu yapar).

**B) Gerçek model, iki ilan.** Kod bloğunu soyma yaması (`kod_blogunu_soy`) sayesinde ikisi de ilk denemede geçti:

| Alan | ILAN_1 (özet) | ILAN_2 (zor örnek) |
| --- | --- | --- |
| sirket | Acme Yazılım | BulutKod Teknoloji |
| lokasyon | İstanbul | Ankara |
| calisma_sekli | hibrit | hibrit |
| teknolojiler | Python, Django, PostgreSQL, Docker, Redis | React, TypeScript, Node.js |
| deneyim_yili | 3 | null |
| maas_var_mi | true | false |

**Ne öğrendik**

- Doğrulama **biçimi** garanti eder: geçerli alan, doğru tip, izinli değer. Bu akışı sağlamlaştırır.
- Doğrulama **değerin doğruluğunu** garanti etmez. ILAN_2'de "günlük işler evden, ayda bir ofis" yazıyor; model bunu `hibrit` diye etiketledi, `uzaktan` de savunulabilirdi. Pydantic ikisini de kabul eder. Bu tür belirsizlikleri **ölçmek** için hafta 9'daki eval'e ihtiyacın olacak.
- Bu çalıştırmada yeniden deneme döngüsü hiç tetiklenmedi (iki ilan da ilk denemede geçti), yani o yolu gerçek modelle sınamadım; yalnızca kodu yazılı.

## 5. Uygulama 3: şemayı API'ye vermek

Bu yöntemlerde "JSON ver" diye rica etmek yerine şemayı API'nin kendisine veririz. İki yol denedik (`hafta2/03_sema_zorla.py`); ikisi de Haiku 4.5 ile **çalıştı**:

| Yöntem | Kod |
| --- | --- |
| A) Yapılandırılmış çıktı | `client.messages.parse(..., output_format=Ilan)` → sonuç `r.parsed_output` (hazır `Ilan` nesnesi) |
| B) Tool use | `tools=[{"name": "ilan_kaydet", "input_schema": Ilan.model_json_schema()}]` + `tool_choice={"type": "tool", "name": "ilan_kaydet"}`; sonuç `tool_use` bloğunun `.input` alanı |

Her ikisinde de kod bloğu, açıklama cümlesi veya `json.loads` hatası yok; doğrudan şemaya uyan veri geliyor. Hafta 3'te göreceğimiz tool use'un ilk tanışması da bu.

**ILAN_2 için çıktı** (her iki yöntemde de aynı; kısaltıldı):

```
sirket: BulutKod Teknoloji   lokasyon: Ankara   calisma_sekli: hibrit
teknolojiler: React, TypeScript, Node.js
deneyim_yili: 2   maas_var_mi: false
```

**Dikkat çeken fark:** Yöntem 2'nin (4. bölüm) aynı ilan için `deneyim_yili` değerini `null` döndürdüğünü görmüştük; burada `2` geldi. İlanın metni "önceki deneyimin 2 yıldan az olabilir" diyor, yani gereken minimum deneyim yok; `2` büyük ihtimalle yanlış okuma. Şema biçimi doğruladı (`int` geçerli), ama değer hatalı olabilir ve aynı prompt farklı çalıştırmalarda farklı sonuç verebilir.

**Pratik karar**

- Üretimde A veya B ile şemayı API'ye ver, sonucu yine pydantic'le doğrula.
- Alan açıklamalarını (`Field(description=...)`) netleştir: "yoksa null", "ilanda açıkça yazıyorsa" gibi cümleler şemaya girer ve modele rehberlik eder.
- Değer doğruluğu için elle etiketlenmiş örneklerle test et (hafta 9, eval).

## 6. Hafta sonu çıktısı

`~/projects/ai-engineering/hafta2/` altında ortak bir dosya ve üç script var. Aynı iş (ilandan alan çıkarma) üç güvenlik seviyesinde yapılıyor.

| Dosya | Ne gösteriyor | Akılda kalacak sonuç |
| --- | --- | --- |
| `ilan_modeli.py` | `Ilan` pydantic modeli, iki örnek ilan | Şema bir Python sınıfı olarak yazılır |
| `01_promptla_json.py` | "Sadece JSON ver" + `json.loads` | 5 denemenin 5'inde başarısız (kod bloğu yüzünden) |
| `02_pydantic_dogrulama.py` | pydantic ile doğrulama, hata geri bildirimi | Biçim hataları alan alan yakalandı; gerçek cevaplar ilk denemede geçti |
| `03_sema_zorla.py` | `messages.parse` ve tool use ile şema zorlama | İki yol da çalıştı; değer yine de yanlış olabilir (`deneyim_yili`) |

Sırayla çalıştırmak için (`ai-engineering` klasöründen):

```bash
.venv/bin/python hafta2/01_promptla_json.py
.venv/bin/python hafta2/02_pydantic_dogrulama.py
.venv/bin/python hafta2/03_sema_zorla.py
```

**Kendi denemen (öneri, 20 dk):**

1. Gerçek bir iş ilanını (LinkedIn, Kariyer.net) `ilan_modeli.py` içine `ILAN_3` olarak yapıştır ve `03_sema_zorla.py` ile çıkar.
2. Sonucu ilan metniyle karşılaştır: hangi alanı yanlış doldurdu?
3. `Ilan` modeline kendi istediğin bir alan ekle (ör. `sektor`, `yan_haklar` listesi) ve alan açıklaması (`Field(description=...)`) yazarak sonucun nasıl değiştiğine bak.

Bu çalışma, ileride kuracağın AI destekli iş ilanı tarama aracının (job-radar fikri) ilk parçasıdır.

## 7. Sık hatalar ve hızlı başvuru

| Belirti | Neden | Çözüm |
| --- | --- | --- |
| `json.JSONDecodeError: Expecting value` | Model JSON'u ` ```json ` kod bloğu içinde verdi (bizim çalıştırmada 5/5) | Yama: bloğu soy; kalıcı: şemayı API'ye ver (yöntem A veya B) |
| `pydantic.ValidationError` | Alan eksik, tip yanlış ya da `Literal` dışı değer | `e.errors()` ile hangi alan olduğunu oku; hatayı modele geri ver |
| `ANTHROPIC_API_KEY is set and takes precedence ...` (script çıktılarında görünen bilgi mesajı) | SDK, ortamda anahtar bulunduğunu ve başka kimlik bilgilerinden önce onu kullandığını bildiriyor | Bilgilendirme; anahtarın `.env`'den geldiğini gösterir, işlevi bozmaz |
| `messages.parse` hata verirse | Kullanılan model veya SDK sürümü yapılandırılmış çıktıyı desteklemiyor olabilir (benim Haiku 4.5 ile denememde çalıştı) | Yöntem B'ye (tool use) geç; çözüm yine pydantic ile doğrulamaktır |
| Değer yanlış ama biçim doğru | Şema yalnızca biçimi denetler | Alan açıklamasını netleştir, elle etiketli örneklerle test et |

**Minimum kalıp** (unutursan buradan kopyala):

```python
from pydantic import BaseModel
from anthropic import Anthropic

class Ilan(BaseModel):
    sirket: str
    teknolojiler: list[str]

client = Anthropic()
r = client.messages.parse(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[{"role": "user", "content": "Ilan metni buraya"}],
    output_format=Ilan,
)
ilan = r.parsed_output   # dogrulanmis Ilan nesnesi
```

## 8. Kaynaklar ve sıradaki hafta

**Bu hafta için kaynaklar**

- [Anthropic: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs): `messages.parse` ve JSON şema ile çıktı biçimi (bağlantı SDK'nın kendi doküman açıklamasından alındı)
- [Pydantic dokümanları](https://docs.pydantic.dev): `BaseModel`, `Field`, `Literal`, `model_validate_json`
- Anthropic Docs'ta tool use bölümü: yöntem B'nin ayrıntıları için

Bu bağlantıları sayfayı açıp doğrulamadım; ilk baktığında adres ya da başlık değişmiş olabilir. Kodlar ise bu oturumda gerçekten çalıştırıldı (anthropic 2.8.0, pydantic 2.14.3, Haiku 4.5).

**Hafta 3: Tool use ve ilk agent**

Bu hafta tool use'u yalnızca şema zorlamak için kullandık. Gelecek hafta asıl amacı için kullanacağız: modelin **senin yazdığın Python fonksiyonlarını çağırması** (hava durumu sorgula, quiz veritabanında soru ara gibi), aracın sonucunu modele geri verme ve bunu bir döngüde tekrarlama. Bu döngü, agent'ın temelidir.
