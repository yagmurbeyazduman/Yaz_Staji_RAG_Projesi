import sqlite3
import json
from foundry_local_sdk import Configuration, FoundryLocalManager
from belgeler import belgeler

def main():
    config = Configuration(app_name="yaz_staji_projesi")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embed_model.download(lambda p: print(f"\rIndirme: {p:.1f}%", end="", flush=True))
    print()
    embed_model.load()

    client = embed_model.get_embedding_client()

    baglanti = sqlite3.connect("belgeler.db")
    imlec = baglanti.cursor()

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS belgeler_tablosu (
            id INTEGER PRIMARY KEY,
            content TEXT,
            embedding TEXT
        )
    """)
    imlec.execute("DELETE FROM belgeler_tablosu")

    BATCH_BOYUTU = 10
    for i in range(0, len(belgeler), BATCH_BOYUTU):
        batch = belgeler[i:i + BATCH_BOYUTU]
        response = client.generate_embeddings(inputs=batch)
        for j, metin in enumerate(batch):
            vektor = response.data[j].embedding
            vektor_json = json.dumps(vektor)
            imlec.execute(
                "INSERT INTO belgeler_tablosu (content, embedding) VALUES (?, ?)",
                (metin, vektor_json)
            )
            print(f"Kaydedildi: {metin[:40]}...")
        baglanti.commit()

    baglanti.commit()
    baglanti.close()
    print("Tum belgeler veritabanina kaydedildi!")

    embed_model.unload()

if __name__ == "__main__":
    main()