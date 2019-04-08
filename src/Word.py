import re
from src.Text import Text
from src.Phrase import SamplePhrase


class Word(Text):

    def __init__(self, dialect, word_id, title, definition, pos, category, phrase, phrase_def, user, contributor,
                 cultural_note, pronunciation, reference, image_id, audio_id, video_id, children_archive, status, literal_translation, change):
        Text.__init__(self, dialect, word_id, title, definition, user, contributor, cultural_note, reference, image_id,
                      audio_id, video_id, children_archive, status, literal_translation, change)
        self.category = category
        self.pos = pos
        self.pronunciation = pronunciation
        self.phrase = phrase
        self.phrase_def = phrase_def

    def validate(self):
        self.doc = self.dialect.nuxeo_words.get(self.id)
        if super().validate():
            self.pos_validate()
            self.phrase_validate()
            self.category_validate()
            self.validate_text(self.pronunciation, "fv-word:pronunciation")

    def pos_validate(self):
        if self.doc.get('fv-word:part_of_speech') is None:
            return False
        pos = re.sub('[/()\- ]+', "_", self.doc.get('fv-word:part_of_speech')).strip("_")
        if self.pos == pos:
            return True
        self.dialect.flags.dataMismatch(self, 'fv-word:part_of_speech', self.pos, pos)
        print(self.pos)
        print(self.doc.get('fv-word:part_of_speech'))
        print(self.id)
        print("~~~")
        return False

    def category_validate(self):
        self.validate_uid(self.category, 'fv:word_categories', self.dialect.Data.categories)

    def phrase_validate(self):
        related_phrases = self.doc.get("fv-word:related_phrases")
        if not self.phrase and not related_phrases:
            return True
        if not self.phrase:
            self.dialect.flags.dataMismatch(self, "fv-word:related_phrases", self.phrase, related_phrases)
            return False
        phrase = None
        for p in self.dialect.legacy_phrases:
            if p.title.strip() == self.phrase.strip() and p.definition.strip() == self.phrase_def.strip():
                phrase = p
                print("sample phrase found in phrases")
                break
        if not related_phrases:
            self.dialect.flags.dataMismatch(self, "fv-word:related_phrases", self.phrase, related_phrases)
            if not phrase:
                phrase = SamplePhrase(self.dialect, related_phrases[0], self.phrase, self.phrase_def, self.user, self.contributor, self.children_archive, self.status)
                self.dialect.flags.itemNotFound(phrase)
                return False
        if not phrase:
            phrase = SamplePhrase(self.dialect, related_phrases[0], self.phrase, self.phrase_def, self.user, self.contributor, self.children_archive, self.status)
            phrase.validate()
        self.validate_text(phrase.title, "fv-word:related_phrases")



