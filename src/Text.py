from src.Item import Item
from src.LetterMapper import LetterMapper


class Text(Item):

    def __init__(self, dialect, item_id,  title, definition, user, contributor, cultural_note, reference, image_id,
                 audio_id, video_id, children_archive, status, literal_translation=None, change=None):
        Item.__init__(self, dialect, item_id, title, user, change)
        self.definition = definition
        self.cultural_note = cultural_note
        self.reference = reference
        self.image_id = image_id
        self.audio_id = audio_id
        self.video_id = video_id
        self.contributor = contributor
        self.status = status
        self.children_archive = children_archive
        self.literal_translation = literal_translation

    def validate(self):
        if super().validate():
            self.definition_validate()
            self.literal_translation_validate()
            self.cultural_note_validate()
            self.reference_validate()
            self.childrens_validate()
            self.contributor_validate(self.contributor, "fv:source")
            self.media_validate()
            self.status_validate()

    def definition_validate(self):
        self.validate_translation(self.definition, "fv:definitions")

    def literal_translation_validate(self):
        self.validate_translation(self.literal_translation, "fv:literal_translation")

    def reference_validate(self):
        self.validate_text(self.reference, "fv:reference")

    def cultural_note_validate(self):
        notes = self.doc.get("fv:cultural_note")
        if self.cultural_note is None and len(notes) == 0:
            return True
        else:
            if self.cultural_note is not None:
                note = self.cultural_note.split(",")
                self.validate_text(note, "fv:cultural_note")

    def media_validate(self):
        if self.image_id in self.dialect.legacy_media:
            self.validate_uid(self.dialect.legacy_media[self.image_id].title, "fv:related_pictures", self.dialect.nuxeo_imgs.values())
        else:
            self.validate_uid(None, "fv:related_pictures", self.dialect.nuxeo_imgs.values())
        if self.video_id in self.dialect.legacy_media:
            self.validate_uid(self.dialect.legacy_media[self.video_id].title, "fv:related_videos", self.dialect.nuxeo_videos.values())
        else:
            self.validate_uid(None, "fv:related_videos", self.dialect.nuxeo_videos.values())
        if self.audio_id in self.dialect.legacy_media:
            self.validate_uid(self.dialect.legacy_media[self.audio_id].title, "fv:related_audio", self.dialect.nuxeo_audio.values())
        else:
            self.validate_uid(None, "fv:related_audio", self.dialect.nuxeo_audio.values())

    def childrens_validate(self):
        self.validate_int(self.children_archive, "fv:available_in_childrens_archive")
