from src.Item import Item
from src.MediaFile import UnEnteredMediaFile


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

    def sample_validate(self):
        self.validate_uid(self.sample_word, "fvcharacter:related_words", self.dialect.nuxeo_words.values())

    def audio_validate(self):
        if self.audio[0] is None:
            self.validate_uid(self.audio[0], "fv:related_audio", self.dialect.nuxeo_audio.values())
        else:
            self.validate_uid(self.audio[0][self.audio[0].rindex('/')+1:], "fv:related_audio", self.dialect.nuxeo_audio.values())
            audio = UnEnteredMediaFile(self.dialect, self.audio[0], self.audio[1], self.audio[2], self.audio[3], 3, self.audio[4])
            audio.validate()

    def extended_validate(self):
        if self.extended == 'Y':
            self.validate_int("True", "fvcharacter:extended")
        elif self.extended == 'N':
            self.validate_int("False", "fvcharacter:extended")
