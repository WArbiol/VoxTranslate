def translate_text(text, target_code, tokenizer, translator):
    input_text = f">>{target_code}<< {text}"
    tokens = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    translated_tokens = translator.generate(**tokens, max_length=512)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return translated_text.upper()