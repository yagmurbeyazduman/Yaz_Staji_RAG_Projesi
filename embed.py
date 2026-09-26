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
    print("Embedding modeli hazir!")
    client = embed_model.get_embedding_client()
    response = client.generate_embeddings(inputs=belgeler)

    for i, metin in enumerate(belgeler):
        vektor = response.data[i].embedding
        print(f"Metin: {metin[:40]}...")
        print(f"Vektor uzunlugu: {len(vektor)}")
        print(f"Ilk 5 sayi: {vektor[:5]}")
        print("---")

    embed_model.unload()

if __name__ == "__main__":
    main()