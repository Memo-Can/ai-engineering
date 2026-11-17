# AI Mühendisliği – Çalışma Defteri

12 haftalık AI mühendisliği eğitim planının notları ve kodları. Her hafta bir `notlar/haftaN.md`
(ne öğrendim, neden öyle) ve bir `haftaN/` klasörü (çalışan script'ler) içerir.

| Hafta | Konu | Not | Kod |
| --- | --- | --- | --- |
| 1 | LLM'e ilk adım: API, system prompt, few-shot | [notlar/hafta1.md](notlar/hafta1.md) | [hafta1/](hafta1/) |
| 2 | Structured output: JSON şema, pydantic, tool use | [notlar/hafta2.md](notlar/hafta2.md) | [hafta2/](hafta2/) |
| 3 | Tool use ve ilk agent: araç döngüsü, hata, prompt injection | [notlar/hafta3.md](notlar/hafta3.md) | [hafta3/](hafta3/) |
| 4 | Embedding ve anlamsal arama: kosinüs benzerliği, mini RAG | [notlar/hafta4.md](notlar/hafta4.md) | [hafta4/](hafta4/) |

## Kurulum

Python 3.10+ gerekir.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasını açıp `ANTHROPIC_API_KEY=` satırının sonuna kendi anahtarını yaz
(console.anthropic.com → API Keys). `.env` git'e girmez; anahtarı kodun içine veya repoya koyma.

## Çalıştırma

```bash
.venv/bin/python hafta1/01_ilk_cagri.py
```

API çağrıları Anthropic Console bakiyesinden ücretlendirilir; hafta 1 denemeleri birkaç sent tutar.
