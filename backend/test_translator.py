from app.ai_models.translator import SmartTranslator

if __name__ == "__main__":
    print("Initializing SmartTranslator...")
    t = SmartTranslator()
    print("Initialized.")
    text = "hello"
    print(f"Translating: {text}")
    try:
        out = t.translate_english_to_french(text)
        print("Translation:", out)
    except Exception as e:
        print("Error during translation:", repr(e))
