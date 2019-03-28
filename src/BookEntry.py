from src.Text import Text


class BookEntry(Text):

    def __init__(self, dialect, entry_id, title, definition, user, translation, book_id, cultural_note, image_id,
                 audio_id, video_id, change, order):
        self.order = order
        for book in dialect.legacy_books:
            if book.id == book_id:
                self.book = book
                self.status = book.status
                self.children_archive = book.children_archive
        Text.__init__(self, dialect, entry_id, title, definition, user, None, cultural_note, None, image_id,
                      audio_id, video_id, self.children_archive, self.status, translation, change)

    def validate(self):
        self.doc = self.dialect.nuxeo_book_entries.get(self.id)
        if super().validate():
            self.order_validate()

    def definition_validate(self):
        if self.definition:
            self.validate_translation(self.definition, "fvbookentry:dominant_language_text")
        else:
            self.validate_translation(self.definition, "fvbookentry:dominant_language_text")

    def order_validate(self):
        self.validate_int(self.order, "fvbookentry:sort_map")
