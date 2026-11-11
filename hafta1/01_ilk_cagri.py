"""Hafta 1 - Script 1: modele ilk istek.

Calistirma (ai-engineering klasorunden):
    .venv/bin/python hafta1/01_ilk_cagri.py
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # .env varsa ANTHROPIC_API_KEY'i oradan okur

MODEL = "claude-haiku-4-5-20251001"  # en ucuz model; deneme icin yeterli

client = Anthropic()  # anahtari ortam degiskeninden kendisi alir

response = client.messages.create(
    model=MODEL,
    max_tokens=300,  # zorunlu: cevabin ust siniri
    messages=[
        {"role": "user", "content": "Bir LLM'i 2 cumleyle, bir backend gelistiriciye anlat."},
    ],
)

print("--- Cevap ---")
print(response.content[0].text)

print("\n--- Meta ---")
print("durma sebebi:", response.stop_reason)  # end_turn = dogal bitti, max_tokens = kesildi
print("girdi token :", response.usage.input_tokens)
print("cikti token :", response.usage.output_tokens)
