from foundry_local_sdk import Configuration, FoundryLocalManager

def main():
    config = Configuration(app_name="yaz_staji_projesi")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    model = manager.catalog.get_model("qwen2.5-0.5b")
    model.download(lambda p: print(f"\rIndirme: {p:.1f}%", end="", flush=True))
    print()
    model.load()
    print("Model yuklendi, hazir!")
    client = model.get_chat_client()
    messages = [{"role": "user", "content": "Merhaba, kendini tanitir misin?"}]

    print("Asistan: ", end="", flush=True)
    for chunk in client.complete_streaming_chat(messages):
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()

    model.unload()
    
if __name__ == "__main__":
    main()