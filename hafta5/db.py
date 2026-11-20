"""Hafta 5 - veritabani baglantisi. Yerel Docker konteynerine (pgvector/pgvector:pg16) baglanir.

Konteyner (bir kez):
  docker run -d --name pgvector-egitim -e POSTGRES_PASSWORD=egitim -e POSTGRES_DB=egitim \
    -p 127.0.0.1:5433:5432 -v pgvector-egitim-veri:/var/lib/postgresql/data pgvector/pgvector:pg16

Parola yalnizca bu yerel egitim konteyneri icindir; port sadece 127.0.0.1'e acilir.
"""

import os

import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:egitim@127.0.0.1:5433/egitim")


def baglan() -> psycopg.Connection:
    """Baglanti acar, vector eklentisini etkinlestirir ve numpy dizilerini vector tipine cevirmeyi ogretir."""
    con = psycopg.connect(DATABASE_URL, autocommit=True)
    con.execute("CREATE EXTENSION IF NOT EXISTS vector")  # eklenti zaten varsa bir sey yapmaz
    register_vector(con)
    return con
