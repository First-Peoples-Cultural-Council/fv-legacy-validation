from src.Text import Text


class Phrase(Text):

    def __init__(self, dialect, phrase_id, title, definition, phrase_book, user, contributor, cultural_note, reference, image_id,
                 audio_id, video_id, children_archive, status, change):
        Text.__init__(self, dialect, phrase_id, title, definition, user, contributor, cultural_note, reference, image_id,
                      audio_id, video_id, children_archive, status, change=change)
        self.category = phrase_book

    def validate(self):
        self.doc = self.dialect.nuxeo_phrases.get(self.id)
        if super().validate():
            self.category_validate()

    def category_validate(self):
        self.validate_uid(self.category, "fv-phrase:phrase_books", self.dialect.nuxeo_phrase_books.values())


class SamplePhrase(Text):

    def __init__(self, dialect, phrase_id, title, definition, user, contributor, children_archive, status):
        Text.__init__(self, dialect, phrase_id, title, definition, user, contributor, None, None, None,
                      None, None, children_archive, status)

    def validate(self):
        for p in self.dialect.nuxeo_phrases:
            if p.uid == self.id:
                self.doc = p
                break

        return super().validate()
