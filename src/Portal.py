from src.Item import Item
from src.MediaFile import UnEnteredMediaFile
from src.LetterMapper import LetterMapper
import re


class Portal(Item):

    def __init__(self, dialect, portal_info, first_words, image, audio, show_alphabet, show_keyboard):  #  no import ids-all fvl properties are null
        super().__init__(dialect, dialect.id, "Portal")
        self.about = [portal_info[2], portal_info[0], portal_info[1]]
        self.greeting = portal_info[3]
        self.column_title = portal_info[4]
        self.column_text = portal_info[5]
        self.people_name = portal_info[6]
        self.related_links = portal_info[7]
        self.status = portal_info[8]
        self.theme = self.dialect.Data.legacy_themes.get(portal_info[9])
        self.first_words = first_words
        self.image = image
        self.audio = audio
        self.show_alphabet = show_alphabet
        self.show_keyboard = show_keyboard

    def validate(self):
        for child in self.nuxeo.documents.get_children(uid=self.dialect.doc.uid):
            if child.get('dc:title') == "Portal":
                self.doc = child
        if super().validate():
            self.about_validate()
            self.validate_text(self.greeting, "fv-portal:greeting")
            self.first_words_validate()
            self.column_validate()
            self.links_validate()
            self.status_validate()
            self.media_validate()

    def about_validate(self):
        while self.about.count(None) != 0:
            self.about.remove(None)

        #if self.people_name is not None:
        #    portal_about = '<p><strong>About The '+self.people_name+' people</strong></p><p>'+portal_about  # review, maybe add back??
        # self.validate_text(portal_about, "fv-portal:about")
        # portal_about = self.html_strip(portal_about).strip()
        if len(self.about) == 0 and self.doc.get("fv-portal:about") is None:
            return True
        if len(self.about) == 0 or self.doc.get("fv-portal:about") is None:
            return False
        portal_about = " ".join(self.about)
        self.validate_text(portal_about, "fv-portal:about")

    def first_words_validate(self):  # check order too
        doc_ids = []
        for word in self.first_words:
            if word is not None:
                for legacy_word in self.dialect.legacy_words:
                    if word == legacy_word.id:
                        doc_ids.append(legacy_word.doc.uid)
                        break

        self.validate_text(doc_ids, 'fv-portal:featured_words')

    def column_validate(self):
        column = [self.column_title, self.column_text]
        while column.count(None) != 0:
            column.remove(None)
        column = " ".join(column)
        self.validate_text(column, "fv-portal:news")

    def links_validate(self):
        self.validate_uid(self.related_links, "fv-portal:related_links", self.dialect.nuxeo_links)

    def media_validate(self):
        if self.image[0] == 'pixel.gif':
            self.image[0] = '/pixel.gif'
        self._media_validate(self.image[0], "fv-portal:logo", self.image[1], self.image[3], self.image[2], 1, self.image[4])
        self._media_validate(self.audio[0], "fv-portal:featured_audio", self.audio[1], self.audio[3], self.audio[2], 3, self.audio[4])
        if self.theme is None:
            self._media_validate(self.theme, "fv-portal:background_bottom_image", None, None, None, 1, 1)
            self._media_validate(self.theme, "fv-portal:background_top_image", None, None, None, 1, 1)
        else:
            self._media_validate(self.theme[2], "fv-portal:background_bottom_image", None, None, None, 1, 1)
            self._media_validate(self.theme[3], "fv-portal:background_top_image", None, None, None, 1, 1)
        # self._media_validate(self.theme[4], "fv-portal:logo_2", None, None, None, None, 1, 1) # PREVIEW_IMAGE_FILENAME in db, unsure where in nuxeo, no other spots than logo_2 which is all empty

    def _media_validate(self, filename, nuxeo_str, descr, contributor, recorder, type, status):
        types = {1: self.dialect.nuxeo_imgs, 2: self.dialect.nuxeo_videos, 3: self.dialect.nuxeo_audio}
        nuxeo_docs = types[type].values()
        if filename is None:
            self.validate_uid(filename, nuxeo_str, nuxeo_docs)
        else:
            self.validate_uid(filename[filename.rindex('/')+1:], nuxeo_str, nuxeo_docs)
            media = UnEnteredMediaFile(self.dialect, filename, descr, contributor, recorder, type, status)
            media.validate()
