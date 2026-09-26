import sqlite3
import json
import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

def kosinus_benzerligi(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def main():
    config = Configuration(app_name="yaz_staji_projesi")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embed_model.download(lambda p: print(f"\rIndirme: {p:.1f}%", end="", flush=True))
    print()
    embed_model.load()

    client = embed_model.get_embedding_client()

    soru = "SQLite nedir?"
    print(f"Soru: {soru}")

    soru_response = client.generate_embeddings(inputs=[soru])
    soru_vektoru = soru_response.data[0].embedding
    baglanti = sqlite3.connect("belgeler.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT content, embedding FROM belgeler_tablosu")
    kayitlar = imlec.fetchall()
    baglanti.close()

    en_iyi_skor = -1
    en_iyi_metin = None

    for content, embedding_json in kayitlar:
        belge_vektoru = json.loads(embedding_json)
        skor = kosinus_benzerligi(soru_vektoru, belge_vektoru)
        print(f"Benzerlik: {skor:.4f} -> {content[:50]}...")

        if skor > en_iyi_skor:
            en_iyi_skor = skor
            en_iyi_metin = content

    print()
    print(f"EN ILGILI BELGE: {en_iyi_metin}")

    embed_model.unload()

if __name__ == "__main__":
    main()