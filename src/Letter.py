from src.Item import Item
from src.MediaFile import UnEnteredMediaFile
from src.LetterMapper import LetterMapper


class Letter(Item):

    def __init__(self, dialect, letter_id, char, upper_char, extended, order, sample_word, audio, change):
        super().__init__(dialect, letter_id, char, change=change)
        self.upper = upper_char
        self.extended = extended
        self.order = order
        self.sample_word = sample_word
        self.audio = audio

    def validate(self):
        self.doc = self.dialect.nuxeo_letters.get(self.id)
        if super().validate():
            self.validate_int(self.order, "fvcharacter:alphabet_order")
            self.validate_text(self.upper, "fvcharacter:upper_case_character")
            self.sample_validate()
            self.extended_validate()
            self.audio_validate()

    def sample_validate(self):
        if self.sample_word and self.sample_word not in self.dialect.word_titles:
            match = False
            for word in self.dialect.word_titles:
                if LetterMapper().compare(self.sample_word, word):
                    match = True
                    break
            if not match:
                self.dialect.unentered_words += 1
        self.validate_uid(self.sample_word, "fvcharacter:related_words", self.dialect.nuxeo_words.values())

    def audio_validate(self):
        if not self.audio[0]:
            self.validate_uid(self.audio[0], "fv:related_audio", self.dialect.nuxeo_audio.values())
        else:
            if self.audio[0].count('/'):
                self.validate_uid(self.audio[0][self.audio[0].rindex('/')+1:], "fv:related_audio", self.dialect.nuxeo_audio.values())
                for f in self.dialect.legacy_media.values():
                    if f.filename == self.audio[0]:
                        print("~~~ unentered media found in media")
                        return
            else:
                self.validate_uid(self.audio[0][self.audio[0].rindex('\\')+1:], "fv:related_audio", self.dialect.nuxeo_audio.values())
                for f in self.dialect.legacy_media.values():
                    if f.filename == self.audio[0]:
                        print("~~~ unentered media found in media")
                        return
            audio = UnEnteredMediaFile(self.dialect, self.audio[0], self.audio[1], self.audio[2], self.audio[3], 3, self.audio[4])
            audio.validate()

    def extended_validate(self):
        if self.extended == 'Y':
            self.validate_int("True", "fvcharacter:extended")
        elif self.extended == 'N':
            self.validate_int("False", "fvcharacter:extended")

    def quality_check(self):
        if not self.doc.get("dc:title"):
            self.dialect.flags.missingData(self, "dc:title")
