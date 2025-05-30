import os
from mnemonic import Mnemonic

def export_bip39_wordlists():
    supported_languages = [
        "english", "french", "italian", "spanish", "chinese_simplified",
        "chinese_traditional", "japanese", "korean", "czech", "portuguese", "russian"
    ]

    os.makedirs("output_lang_files", exist_ok=True)

    wordlists_by_lang = {}

    for lang in supported_languages:
        try:
            mnemo = Mnemonic(lang)
            wordlist = mnemo.wordlist

            # Save to file
            with open(f"output_lang_files/{lang}.txt", "w", encoding="utf-8") as f:
                for word in wordlist:
                    f.write(word + "\n")

            # Save to Python variable
            var_name = f"{lang.replace('-', '_')}_lst"
            globals()[var_name] = wordlist
            wordlists_by_lang[lang] = wordlist

            print(f"Saved: {lang}.txt and variable: {var_name}")

        except Exception as e:
            print(f"Error processing language {lang}: {e}")

    return wordlists_by_lang

# Run and get dictionary of wordlists
lang_wordlists = export_bip39_wordlists()

# Example usage:
# print(english_lst[:10])  # First 10 English words
# print(lang_wordlists["french"][:10])  # First 10 French words
