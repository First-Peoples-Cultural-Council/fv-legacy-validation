import re


class LetterMapper:

    def __init__(self):
        self.letters = {"Ṉ": "Ṉ", "č": "č", "ą̄": "ą̄", "š": "š", "į̄": "į̄", "Ḵ": "Ḵ", "Ṯ": "Ṯ", "é": "é", "í": "í", "ó": "ó", "ú": "ú",
                        "á": "á", "į": "į", "ḵ": ["ḵ", "ḵ"], "ĺ": ["ĺ", "ĺ"], "ḱ": "ḱ", "ǵ": "ǵ", "ẃ": "ẃ", "ś": "ś", "ń": "ń", "ṣ": "ṣ",
                        "ų̄": "ų̄", "ḵ̓": "ḵ̓", "ọʼ": "ọʼ", "ị": "ị", "ḷ": "ḷ", "ý": "ý", "ḻ": "ḻ", "a": "​a", "ḥ":  "ḥ", "ḵ̱̓": "ḵ̱̓", "ṓ": "ṓ",
                        "̀n": "̀n", "â": "â", "ǧ": "ǧ", "ä": "ä", "à": "à", "ē": "ē", "ë": "ë", "ą": "ą", "Ë": "Ë", "ò": "ò", "ẅ": "ẅ",
                        "̀ ": "̀ ", "ǫ": "ǫ", "ě": "ě", "Ǹ": "Ǹ", "ǔ": "ǔ", "Ä": "Ä", "ù": "ù", "ų": "ų", "l̓": "Ì", "ǰ": "ǰ",
                        "̀d": "̀d",  "Ḻ̵": "Ḻ̵", "Í": ["Í", "Í"], "Ú": "Ú", "É": "É", "ṕ": "ṕ", "ć": "ć", "̣́ĺ": "̣́ĺ", "ṯ": "ṯ", "Ḥ": "Ḥ",
                        "Č": "Č", "ṉ": "ṉ", "ḵ̕": "ḵ̕", "ō": "ō", "ḿ": "ḿ", "ü": "ü", "ǜ": "ǜ", "ę": "ę", "è": "è", "ˈẅ": "ˈẅ",
                        "ǟ": "ǟ", "ì": "ì", "Á": "Á", "ā": "ā", "Ń": "Ń", "ū": "ū", "À": "À", "ǹ": "ǹ", "ǒ": "ǒ", "ǭ":"ǭ",
                        "̀b": "̀b", "Ì": "Ì", "Ą": "Ą", "ǎ": "ǎ", "ô": "ô", "ạ": "ạ", "Ǫ": "Ǫ", "'": ["’", '"', "ʼ"], "’": "'","ǭ̀":"ǭ̀",
                         "ï": "ï", "Ę": "Ę", "̨": "̨̲", "ọ́ʕ": "ọ́ʕ", "ǐ": "ǐ", "ʼ": "'", "ī": "ī", "û": "û", "î": "î", "ī̀": "ī̀",
                        "ẕ": "ẕ", "Ḏẕ": "Ḏẕ", "ḏẕ": "ḏẕ", "ḡ°": "ḡ°", "ḡ": "ḡ", "ų́": "ų́", "Ǫ́": "Ǫ́", "į́": "į́", "Į́": "Į́",
                        "ą́": "ą́", "Ą́": "Ą́", "Ų́": "Ų́", "Ų": "Ų", "Ę́": "Ę́", "Į": "Į", "ę́": "ę́", "ł": "ł", "ä̀ ": "ä̀"}

    def compare(self, legacy_word, nuxeo_word):
        matches = re.findall("", legacy_word)
        for k, v in self.letters.items():
            if isinstance(v, list):
                for let in v:
                    legacy_word = re.sub(let, k, legacy_word)
                    nuxeo_word = re.sub(let, k, nuxeo_word)
            else:
                legacy_word = re.sub(v, k, legacy_word)
                nuxeo_word = re.sub(v, k, nuxeo_word)
        return legacy_word == nuxeo_word

        # for letter in nuxeo_word:
        #     if letter in self.letters:
        #         if isinstance(self.letters[letter], list):
        #             for item in self.letters[letter]:
        #                 legacy_word = legacy_word.replace(item, letter)
        #                 nuxeo_word = nuxeo_word.replace(item, letter)
        #         else:
        #             legacy_word = legacy_word.replace(self.letters[letter], letter)
        #             nuxeo_word = nuxeo_word.replace(self.letters[letter], letter)
        # if legacy_word == nuxeo_word:
        #     return True
        # return False

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
