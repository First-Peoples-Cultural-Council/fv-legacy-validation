from src.Text import Text
from src.LetterMapper import LetterMapper


class Book(Text):

    def __init__(self, dialect, book_id, title, definition, user, contributor, cultural_note, reference, image_id,
                 audio_id, video_id, children_archive, status, intro, intro_def, author, author_ref, contributor_ref,
                 translation, sstype, change):
        Text.__init__(self, dialect, book_id, title, definition, user, contributor, cultural_note, reference, image_id,
                      audio_id, video_id, children_archive, status, translation, change)
        self.intro = intro
        self.intro_def = intro_def
        self.author = author
        self.author_ref = author_ref  ##
        self.contributor_ref = contributor_ref  ##
        self.sstype = sstype

    def validate(self):
        self.doc = self.dialect.nuxeo_books.get(self.id)
        if super().validate():
            self.validate_translation(self.intro, "fvbook:introduction")
            self.validate_translation(self.intro_def, "fvbook:introduction_literal_translation")
            self.author_validate()
            self.type_validate()
            self.entries_validate()

    def definition_validate(self):
        self.validate_translation(self.definition, "fvbook:title_literal_translation")

    def literal_translation_validate(self):
        self.validate_translation(self.literal_translation, "fvbook:dominant_language_translation")

    def reference_validate(self):
        pass  # all nuxeo refs are empty, maybe put in author / contributor ref??

    def author_validate(self):
        self.contributor_validate(self.author, "fvbook:author")

    def type_validate(self):
        if self.sstype == 1:
            self.validate_text("song", "fvbook:type")
        else:
            self.validate_text("story", "fvbook:type")

    def entries_validate(self):
        doc_children = self.doc.get_children()
        legacy_children = [entry for entry in self.dialect.legacy_book_entries if entry.book_id == self.id]
        matches = {}
        for entry in legacy_children:
            entry.validate()
            for child in doc_children:
                if entry.id == child.get("fvl:import_id"):
                    matches[entry] = child
            if matches[entry] is None:
                print("book entry missing from nuxeo")
                print(entry)
        for entry in doc_children:
            if entry not in matches.values():
                print("book entry not from legacy db")
                print(entry)

