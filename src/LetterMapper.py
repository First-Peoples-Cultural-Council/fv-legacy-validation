

class LetterMapper:

    def __init__(self):
        self.letters = {"Ṉ": "Ṉ", "č": "č", "š": "š", "Ḵ": "Ḵ", "Ṯ": "Ṯ", "é": "é", "í": "í", "ó": "ó", "ú": "ú",
                        "á": "á", "ḵ": ["ḵ", "ḵ"], "ĺ": ["ĺ", "ĺ"], "ḱ": "ḱ", "ǵ": "ǵ", "ẃ": "ẃ", "ś": "ś", "ń": "ń", "ṣ": "ṣ",
                        "ị": "ị", "ḷ": "ḷ", "ý": "ý", "ḻ": "ḻ", "a": "​a", "ọ": "ọ́", "ḥ":  "ḥ", "ḵ̱̓": "ḵ̱̓", "ṓ": "ṓ",  # how to handle ḵ̱̓ , ḵ̱̓ ??
                        "ǧ": "ǧ", "ä": "ä", "à": "à", "į": "į", "ē": "ē", "ë": "ë", "ą": "ą", "Ë": "Ë", "ò": "ò",
                        "ǫ": "ǫ", "ě": "ě", "Ǹ": "Ǹ", "ǔ": "ǔ", "Ä": "Ä", "ù": "ù", "ų": "ų", "l̓": "Ì", "ǰ": "ǰ",
                        "Ḻ̵": "Ḻ̵", "Í": ["Í", "Í"], "Ú": "Ú", "É": "É", "ṕ": "ṕ", "ć": "ć", "̣́ĺ": "̣́ĺ", "ṯ": "ṯ", "Ḥ": "Ḥ",
                        "Č": "Č", "ṉ": "ṉ", "ḵ̕": "ḵ̕", "ō": "ō", "ḿ": "ḿ", "ü": "ü", "ǜ": "ǜ", "ę": "ę", "è": "è",
                        "ǟ": "ǟ", "ì": "ì", "Á": "Á", "ā": "ā", "Ń": "Ń", "ū": "ū", "À": "À", "ǹ": "ǹ", "ǒ": "ǒ",
                        "Ì": "Ì", "Ą": "Ą", "ǎ": "ǎ", "ô": "ô", "ạ": "ạ", "ą̄": "ą̄", "Ǫ": "Ǫ", "'": "’", "’": "'",
                        "\"": "'"}

    def compare(self, legacy_word, nuxeo_word):
        for letter in nuxeo_word:
            if letter in self.letters:
                if isinstance(self.letters[letter], list):
                    for item in self.letters[letter]:
                        legacy_word = legacy_word.replace(item, letter)
                        nuxeo_word = nuxeo_word.replace(item, letter)
                else:
                    legacy_word = legacy_word.replace(self.letters[letter], letter)
        if legacy_word == nuxeo_word:
            return True
        return False

    # def __init__(self):
    #     self.letters = {"Ṉ": "Ṉ", "č": "č", "š": "š", "Ḵ": "Ḵ", "Ṯ": "Ṯ", "é": "é", "í": "í", "ó": "ó", "ú": "ú",
    #                     "á": "á", "ḵ": "ḵ", "ĺ": "ĺ", "ĺ": "ĺ", "ḱ": "ḱ", "ǵ": "ǵ", "ẃ": "ẃ", "ś": "ś", "ń": "ń", "ṣ": "ṣ",
    #                     "ị": "ị", "ḷ": "ḷ", "ý": "ý", "ḻ": "ḻ", "​a": "a", "ọ́": "ọ", "ḥ": "ḥ", "ḵ̱̓": "ḵ̱̓", "ṓ": "ṓ",
    #                     "ǧ": "ǧ", "ä": "ä", "à": "à", "į": "į", "ē": "ē", "ë": "ë", "ą": "ą", "Ë": "Ë", "ò": "ò",
    #                     "ǫ": "ǫ", "ě": "ě", "Ǹ": "Ǹ", "ǔ": "ǔ", "Ä": "Ä", "ù": "ù", "ų": "ų", "Ì": "l̓"}
    #
    # def compare(self, legacy_word, nuxeo_word):
    #     for letter in nuxeo_word:
    #         if letter in self.letters.values():
    #             legacy_word = legacy_word.replace(list(self.letters.keys())[list(self.letters.values()).index(letter)], letter)
    #     if legacy_word == nuxeo_word:
    #         return True
    #     return False
