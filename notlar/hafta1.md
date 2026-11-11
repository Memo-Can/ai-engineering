# AI Mühendisliği – Hafta 1: LLM'e İlk Adım

Tarih: 2026-11-11

## 1. Amaç ve ön hazırlık

Bu hafta sonunda Python'dan bir LLM'i çağıran, system prompt ile davranışını yönlendiren ve sonucu ekrana yazan çalışan bir script'in olacak. Hedef, "model ne yapar, ben ona nasıl konuşurum" sorusunu sezgisel olarak oturtmak.

**Hafta sonu çıktısı:** `hafta1/` klasöründe 3 küçük script (ilk çağrı, system prompt denemesi, few-shot denemesi) ve bu doküman.

**Ön hazırlık**

- [ ] Python 3.10+ kurulu (`python3 --version`)
- [ ] Anthropic Console'da hesap ve API anahtarı (console.anthropic.com). API ücretlidir; deneme yükü için birkaç cent yeter
- [ ] Çalışma klasörü ve sanal ortam (bölüm 3'te)
- [ ] API anahtarı ortam değişkeni olarak ayarlı (`ANTHROPIC_API_KEY`)

**Güvenlik kuralı:** API anahtarını koda yazma, git'e koyma, sohbete veya dokümana yapıştırma. Yalnızca ortam değişkeni ya da `.gitignore`'a eklenmiş bir `.env` dosyasında tut.

## 2. Temel kavramlar

Bir LLM, verilen metnin devamını tahmin eden bir modeldir; API üzerinden ona bir konuşma geçmişi gönderirsin ve sıradaki cevabı alırsın. Aşağıdaki beş kavram bu haftanın tüm sözlüğüdür.

| Kavram | Ne demek | Neden önemli |
| --- | --- | --- |
| **Token** | Metnin parçaları; kabaca Türkçede bir kelime 2–4 token | Fiyat ve limit token ile ölçülür; Türkçe metin İngilizceden daha çok token harcar |
| **Context window** | Modelin tek istekte görebildiği toplam token (girdi + çıktı) | Sığmayan şey modele hiç ulaşmaz; uzun konuşmalarda eski mesajlar kesilmeli |
| **Mesaj rolleri** | `user` (sen), `assistant` (model), ayrıca ayrı bir `system` alanı | Model geçmişi hatırlamaz; her istekte tüm konuşmayı sen gönderirsin |
| **System prompt** | Modele kalıcı rol ve kural veren talimat | Davranışı yönlendirmenin en güçlü ve ucuz yolu |
| **max_tokens** | Cevabın üst sınırı | Zorunlu parametre; çok küçük verirsen cevap yarıda kesilir |
| **Temperature** | Cevabın ne kadar rastgele olacağını ayarlayan değer. Bu hafta kullandığımız SDK sürümünde (anthropic 2.8.0) `create()` içinde parametre olarak yok; verince `TypeError` alınır | Aynı prompt her çalıştırmada farklı cevap verebilir; bu yüzden tek denemeye güvenme, çıktıyı ölçmek (eval) gerekir |

**En çok yanılan nokta:** API durumsuzdur (stateless). "Model beni hatırlar" sezgisi yanlıştır; her çağrıda geçmişi `messages` listesi olarak yeniden gönderirsin.

## 3. İlk API çağrısı: kurulum ve kod

Tüm çalışmalar `~/projects/ai-engineering/` altında, quiz projesinden ayrı tutulur; her hafta kendi klasöründe (`hafta1/`, `hafta2/` ...).

**Adım 1: Ortam kurulumu** (bir kez)

```bash
mkdir -p ~/projects/ai-engineering/hafta1 && cd ~/projects/ai-engineering
python3 -m venv .venv
.venv/bin/pip install anthropic python-dotenv
printf '.venv/\n.env\n__pycache__/\n' > .gitignore
printf 'ANTHROPIC_API_KEY=\n' > .env.example
```

(Repoyu GitHub'dan klonladıysan bunun yerine: `.venv/bin/pip install -r requirements.txt`.)

**Adım 2: API anahtarı**

1. console.anthropic.com adresinde giriş yap, Billing bölümünden küçük bir bakiye yükle (5 USD bu hafta için fazlasıyla yeter).
2. API Keys bölümünden yeni anahtar oluştur; anahtar yalnızca bir kez gösterilir, hemen kopyala.
3. Anahtarı `.env` dosyasına yaz (`.env.example`'ı kopyalayıp doldur):

```bash
cp .env.example .env
# .env dosyasını açıp ANTHROPIC_API_KEY= satırının sonuna anahtarı yapıştır
```

`.env` dosyası `.gitignore` içinde olduğu için git'e girmez. Adı noktayla başladığı için gizli dosyadır: terminalde `ls -a`, dosya yöneticisinde `Ctrl+H` ile görünür.

**Adım 3: İlk script** (`hafta1/01_ilk_cagri.py`)

```python
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # .env varsa ANTHROPIC_API_KEY'i oradan okur

MODEL = "claude-haiku-4-5-20251001"  # en ucuz model; deneme için yeterli

client = Anthropic()  # anahtarı ortam değişkeninden kendisi alır

response = client.messages.create(
    model=MODEL,
    max_tokens=300,  # zorunlu: cevabın üst sınırı
    messages=[
        {"role": "user", "content": "Bir LLM'i 2 cümleyle, bir backend geliştiriciye anlat."},
    ],
)

print(response.content[0].text)
print("durma sebebi:", response.stop_reason)
print("girdi token :", response.usage.input_tokens)
print("çıktı token :", response.usage.output_tokens)
```

**Adım 4: Çalıştır**

```bash
.venv/bin/python hafta1/01_ilk_cagri.py
```

**Nasıl okunur:** `response.content` bir listedir (metin blokları), bu yüzden `content[0].text` alınır. `stop_reason` `end_turn` ise model doğal olarak bitirmiştir, `max_tokens` ise cevap kesilmiştir. `usage` size tam olarak kaç token harcadığını (yani parayı) gösterir.

**Çalıştırma sonucu** (benim çalıştırmam; senin cevap metnin farklı olacak, çünkü model her seferinde farklı cümle kurar):

```
durma sebebi: end_turn
girdi token : 31
çıktı token : 284
```

Dikkat: prompt "2 cümleyle" dediği halde model başlıklı, 284 token'lık bir cevap yazdı. Talimatlar her zaman birebir uygulanmaz; bunu 4. bölümde system prompt ile düzelteceğiz.

## 4. Prompt yazma: system prompt ve örnek verme

Aynı soruyu üç farklı system prompt ile sorunca çıktı uzunluğu 400 token'dan 92 token'a düştü ve biçim tamamen değişti; model aynı, sadece talimat farklı. Script: `hafta1/02_system_prompt.py`, soru: "Veritabanında index nedir?"

| System prompt | Çıktı (token) | Ne oldu |
| --- | --- | --- |
| Yok | 400 | Başlıklı, tablolu uzun cevap; `max_tokens` sınırına çarpıp yarıda kesildi |
| "En fazla 2 cümle, jargonsuz" | 92 | Kısa ve sade cevap |
| Tanım / Örnek / Dikkat kalıbı | 168 | Kalıba birebir uydu, ayrıştırması kolay |

**Few-shot (örnekle öğretme).** Script: `hafta1/03_few_shot.py`. Görev: quiz sorusunu "kolay / orta / zor" diye etiketlemek. Örnek vermeyince model doğru etiketi buldu ama biçimi tutturmadı; 3 örnek (user/assistant çifti) ekleyince biçim de oturdu:

| Yöntem | Cevap |
| --- | --- |
| Örnek yok | `Kolay` (büyük harfle başladı) |
| 3 örnekle | `kolay` (istediğimiz biçim) |

Örnekler içeriği olduğu kadar **biçimi** de öğretir. Bu fark çok küçük görünür, ama sonucu kodla işleyecek olduğunda (örn. `== "kolay"` karşılaştırması) önemlidir.

**Pratik kurallar**

- Rol ve kalıcı kurallar `system` alanına, o anki soru `user` mesajına yazılır.
- Sayıyla ve biçimle konuş: "kısa yaz" yerine "en fazla 2 cümle", "liste ver" yerine tam şablonu göster.
- Bir biçim istiyorsan tarif etmek yerine 2–3 örnek göster.
- Sonucu tek denemeyle değerlendirme; model her çalıştırmada biraz farklı cevap verir (hafta 9'da bunu ölçmeyi öğreneceksin).

## 5. Hafta sonu çıktısı

`~/projects/ai-engineering/hafta1/` altında üç çalışan script var; her biri bir kavramı gösteriyor.

| Script | Ne gösteriyor | Akılda kalacak sonuç |
| --- | --- | --- |
| `01_ilk_cagri.py` | `messages.create` çağrısı, `stop_reason`, token sayımı | Girdi 31, çıktı 284 token; talimat birebir uygulanmayabilir |
| `02_system_prompt.py` | Aynı soruya 3 farklı system prompt | Çıktı 400 → 92 token; kalıp verince biçim oturdu |
| `03_few_shot.py` | Örnekle biçim öğretme | Örnek yokken `Kolay`, örnekle `kolay` |

Hepsini sırayla çalıştırmak için (`ai-engineering` klasöründen):

```bash
.venv/bin/python hafta1/01_ilk_cagri.py
.venv/bin/python hafta1/02_system_prompt.py
.venv/bin/python hafta1/03_few_shot.py
```

**Kendi denemen (öneri, 15 dk):** `02_system_prompt.py` içindeki `SORU` değişkenini ve system metinlerini kendi konunla değiştirip çıktı uzunluğu ve biçimi nasıl değişiyor gözle. Hafta 1'in asıl kazanımı bu sezgidir.

## 6. Sık hatalar ve hızlı başvuru

| Belirti | Neden | Çözüm |
| --- | --- | --- |
| `.env` dosyası görünmüyor | Adı noktayla başlayan dosyalar gizlidir | Terminalde `ls -a`, dosya yöneticisinde `Ctrl+H` |
| `cp .env.example .env` çalışmadı gibi | Komut yanlış klasörde çalıştırılmış olabilir | Önce `cd ~/projects/ai-engineering`, sonra `ls -a` ile kontrol et |
| `TypeError: ... unexpected keyword argument 'temperature'` | Yeni SDK sürümü (2.8.0) bu parametreyi kabul etmiyor | `create()` çağrısından satırı sil |
| Cevap yarıda kesiliyor | `max_tokens` çok düşük; `stop_reason` `max_tokens` olur | Değeri artır ya da prompt ile cevabı kısalt |
| Kimlik doğrulama hatası | Anahtar yok, yanlış ya da `.env` okunmuyor | `.env`'de `ANTHROPIC_API_KEY=` satırını kontrol et (boşluk ve tırnak olmadan), script'te `load_dotenv()` var mı bak |
| Her çalıştırmada farklı cevap | Model deterministik değildir | Normal; tek denemeye güvenme |

**Minimum çağrı kalıbı** (unutursan buradan kopyala):

```python
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

r = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,                      # zorunlu
    system="Rol ve kurallar buraya",     # isteğe bağlı
    messages=[{"role": "user", "content": "Soru buraya"}],
)
print(r.content[0].text)
print(r.stop_reason, r.usage.input_tokens, r.usage.output_tokens)
```

## 7. Kaynaklar ve sıradaki hafta

**Bu hafta için kaynaklar**

- [Anthropic API dokümanları](https://docs.claude.com): Messages API ve prompt engineering bölümleri
- [Anthropic Console](https://console.anthropic.com): API anahtarı, bakiye ve kullanım takibi
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook): çalışan kod örnekleri
- DeepLearning.AI kısa kursu "ChatGPT Prompt Engineering for Developers" (yaklaşık 1 saat, ücretsiz)
- Andrej Karpathy, "Intro to LLMs" (YouTube, yaklaşık 1 saat): modelin içinde ne olduğuna dair sezgi

Bu listedeki başlıkları plan hazırlarken bildiğim kadarıyla yazdım, bağlantıları özellikle açıp doğrulamadım; ilk baktığında adı ya da adresi değişmiş olabilir.

**Hafta 2: Structured output (JSON)**

Bu haftanın sonunda modelin cevabı metindi. Gelecek hafta modelden serbest metin yerine **doğrulanabilir JSON** almayı öğreneceğiz: bir iş ilanı metninden şirket, pozisyon, teknoloji listesi gibi alanları çıkarıp `pydantic` ile doğrulayacağız. Bu, ileride RAG ve agent'ların temelidir.
