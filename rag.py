import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import json
import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager


def kosinus_benzerligi(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def cince_karakter_var_mi(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def en_ilgili_belgeyi_bul(soru_vektoru, top_k=3):
    baglanti = sqlite3.connect("belgeler.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT content, embedding FROM belgeler_tablosu")
    kayitlar = imlec.fetchall()
    baglanti.close()

    skorlu_kayitlar = []
    for content, embedding_json in kayitlar:
        belge_vektoru = json.loads(embedding_json)
        skor = kosinus_benzerligi(soru_vektoru, belge_vektoru)
        skorlu_kayitlar.append((skor, content))

    skorlu_kayitlar.sort(key=lambda x: x[0], reverse=True)
    en_iyiler = skorlu_kayitlar[:top_k]

    en_iyi_skor = en_iyiler[0][0]
    birlesik_metin = "\n---\n".join(content for _, content in en_iyiler)

    return birlesik_metin, en_iyi_skor


def main():
    config = Configuration(app_name="yaz_staji_projesi")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embed_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embed_model.download(lambda p: print(f"\rIndirme: {p:.1f}%", end="", flush=True))
    print()
    embed_model.load()
    embed_client = embed_model.get_embedding_client()

    chat_model = manager.catalog.get_model("qwen2.5-7b")
    chat_model.download(lambda p: print(f"\rIndirme: {p:.1f}%", end="", flush=True))
    print()
    chat_model.load()
    chat_client = chat_model.get_chat_client()
    chat_client.settings.temperature = 0.4
    chat_client.settings.max_tokens = 500
    chat_client.settings.frequency_penalty = 1.2
    chat_client.settings.top_p = 0.9

    print("Her iki model de hazir! Cikmak icin 'q' yaz.\n")

    while True:
        soru = input("Sorunuz: ")

        if soru.lower() == "q":
            print("Gorusmek uzere!")
            break

        soru_response = embed_client.generate_embeddings(inputs=[soru])
        soru_vektoru = soru_response.data[0].embedding

        ilgili_belge, benzerlik_skoru = en_ilgili_belgeyi_bul(soru_vektoru)
        #print(f"(Benzerlik skoru: {benzerlik_skoru:.3f})")

        ESIK_DEGER = 0.4

        if benzerlik_skoru < ESIK_DEGER:
            print("Cevap: Bu konuda belgede bilgi bulunmuyor.\n")
            continue

        #print(f"(Bulunan ilgili belge: {ilgili_belge[:60]}...)")

        system_mesaji = (
            "Sen yardimci bir asistansin. Sadece asagida verilen BAGLAM bilgisini kullanarak "
            "kullanicinin sorusunu cevapla. Eger cevap baglamda yoksa, 'Bu bilgiye sahip degilim' de.\n\n"
            f"BAGLAM: {ilgili_belge}"
        )

        messages = [
            {"role": "system", "content": system_mesaji},
            {"role": "user", "content": soru}
        ]

        tam_cevap = ""
        for chunk in chat_client.complete_streaming_chat(messages):
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                tam_cevap += content

        if cince_karakter_var_mi(tam_cevap):
            messages.append({"role": "assistant", "content": tam_cevap})
            messages.append({"role": "user", "content": "UYARI: Cevabinda Cince karakter vardi, bu kabul edilemez. Cevabi SADECE Turkce kelimelerle tekrar yaz."})
            tam_cevap = ""
            for chunk in chat_client.complete_streaming_chat(messages):
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    tam_cevap += content

        print(f"Cevap: {tam_cevap}\n")

    embed_model.unload()
    chat_model.unload()


if __name__ == "__main__":
    main()