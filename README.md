# AI Mühendisliği – Çalışma Defteri

12 haftalık AI mühendisliği eğitim planının notları ve kodları. Her hafta bir `notlar/haftaN.md`
(ne öğrendim, neden öyle) ve bir `haftaN/` klasörü (çalışan script'ler) içerir.

| Hafta | Konu | Not | Kod |
| --- | --- | --- | --- |
| 1 | LLM'e ilk adım: API, system prompt, few-shot | [notlar/hafta1.md](notlar/hafta1.md) | [hafta1/](hafta1/) |
| 2 | Structured output: JSON şema, pydantic, tool use | [notlar/hafta2.md](notlar/hafta2.md) | [hafta2/](hafta2/) |
| 3 | Tool use ve ilk agent: araç döngüsü, hata, prompt injection | [notlar/hafta3.md](notlar/hafta3.md) | [hafta3/](hafta3/) |
| 4 | Embedding ve anlamsal arama: kosinüs benzerliği, mini RAG | [notlar/hafta4.md](notlar/hafta4.md) | [hafta4/](hafta4/) |
| 5 | Chunking ve pgvector: parçalama stratejileri, PostgreSQL ile vektör arama, HNSW | [notlar/hafta5.md](notlar/hafta5.md) | [hafta5/](hafta5/) |

## Kurulum

Python 3.10+ gerekir.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasını açıp `ANTHROPIC_API_KEY=` satırının sonuna kendi anahtarını yaz
(console.anthropic.com → API Keys). `.env` git'e girmez; anahtarı kodun içine veya repoya koyma.

## Hafta 5 için PostgreSQL (Docker)

Hafta 5 vektörleri PostgreSQL + pgvector'da saklar. Docker kurulu ve `docker ps` hata vermiyorsa:

```bash
docker run -d --name pgvector-egitim \
  -e POSTGRES_PASSWORD=egitim -e POSTGRES_DB=egitim \
  -p 127.0.0.1:5433:5432 \
  -v pgvector-egitim-veri:/var/lib/postgresql/data \
  pgvector/pgvector:pg16
```

Parola yalnızca bu yerel konteyner içindir; port yalnız `127.0.0.1`'e açılır. Ayrıntılar `notlar/hafta5.md` bölüm 6.

## Çalıştırma

```bash
.venv/bin/python hafta1/01_ilk_cagri.py
```

API çağrıları Anthropic Console bakiyesinden ücretlendirilir; hafta 1 denemeleri birkaç sent tutar.
