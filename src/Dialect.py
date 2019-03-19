from nuxeo.client import Nuxeo
from src.BookEntry import BookEntry
from src.Category import Category, PhraseBook
from src.Gallery import Gallery
from src.Letter import Letter
from src.MediaFile import MediaFile, GalleryMediaFile
from src.Portal import Portal
from src.authorization import Authorize
from src.Item import Item
from src.Word import Word
from src.Phrase import Phrase
from src.Book import Book
from src.NuxeoData import Data
from src.Link import Link
from nuxeo.exceptions import HTTPError


class Dialect(Item):

    def __init__(self, id, name, admin_info, contact_info, descriptions, country, dominant_lang, dominant_lang_fr,
                 public, region, status, url, grammar_rules, pronunciation, art_status, photo_status, lang_group, lang_fam, change):
        super().__init__(self, id, name, change=change)
        self.admin = admin_info  ##
        self.contact = contact_info
        self.description = descriptions
        countries = {1: "CA", 2: "US", 3: "AU"}
        self.country = countries[country]
        self.dominant_lang = dominant_lang
        self.dominant_lang_fr = dominant_lang_fr
        self.public = public
        self.region = region
        self.status = status
        self.url = url
        self.art_status = art_status  ##
        self.photo_status = photo_status  ##
        self.language_group = Data.legacy_lang_grp[lang_group]
        self.language_family = Data.legacy_lang_fam[lang_fam]
        self.portal = None
        self.legacy_words = []
        self.nuxeo_words = {}
        self.legacy_letters = []
        self.nuxeo_letters = {}
        self.legacy_phrases = []
        self.nuxeo_phrases = {}
        self.legacy_phrase_books = []
        self.nuxeo_phrase_books = {}
        self.legacy_books = []
        self.nuxeo_books = {}
        self.legacy_book_entries = []
        self.nuxeo_book_entries = {}
        self.nuxeo_contributors = {}
        self.legacy_categories = []
        self.nuxeo_categories = {}
        self.dialect_media = []
        self.legacy_media = {}
        self.nuxeo_imgs = {}
        self.nuxeo_videos = {}
        self.nuxeo_audio = {}
        self.art_gallery = []
        self.photo_gallery = []
        self.legacy_links = []
        self.legacy_links.append(Link(self, grammar_rules[3], grammar_rules[0], grammar_rules[1], grammar_rules[2], grammar_rules[4], grammar_rules[5], "grammar"))
        self.legacy_links.append(Link(self, pronunciation[0], pronunciation[1], pronunciation[2], pronunciation[4], pronunciation[3], pronunciation[5], "pronunciation"))
        self.nuxeo_links = []

    def validate(self):
        self.dialect_validate()
        for word in self.legacy_words:
            word.validate()
        for phrase in self.legacy_phrases:
            phrase.validate()
        for pb in self.legacy_phrase_books:
            pb.validate()
        for file in self.legacy_media.values():
            file.validate()
        for book in self.legacy_books:
            book.validate()
        for entry in self.legacy_book_entries:
            entry.validate()
        for link in self.legacy_links:
            link.validate()
        for cat in self.legacy_categories:
            cat.validate()
        self.portal.validate()

    def dialect_validate(self):
        self.status_validate()
        self.description_validate()
        self.contact_validate()
        self.validate_text(self.url, "fvdialect:short_url")
        self.validate_text(self.dominant_lang.lower(), "fvdialect:dominant_language")
        self.validate_text(self.country, "fvdialect:country")
        self.validate_text(self.region, "fvdialect:region")
        self.validate_uid(self.language_family, "fva:language", Data.nuxeo_lang_fam)
        self.validate_uid(self.language_group, "fva:family", Data.nuxeo_lang_grp)
        if self.public:
            if self.doc.state != "New" and self.doc.state != "Published":
                print("~~~ should not be state "+str(self.id))
        else:
            if self.doc.state != "New" and self.doc.state != "Enabled":
                print("~~~ should not be state "+str(self.id))

    def description_validate(self):
        while self.description.count(None) != 0:
            self.description.remove(None)
        description = " ".join(self.description)
        self.validate_text(description, "dc:description")

    def contact_validate(self):
        while self.contact.count(None) != 0:
            self.contact.remove(None)
        self.validate_text(" ".join(self.contact), "fvdialect:contact_information")

    def get_attributes(self):
        got_doc = False
        while not got_doc:
            try:
                nuxeo_dialect = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVDialect "
                                                                 "WHERE fvl:import_id = "+str(self.id)+" "
                                                                 "AND ecm:path STARTSWITH '/FV/Workspaces/Data'"})
                got_doc = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        entries = nuxeo_dialect.get("entries")
        for item in entries:
            self.doc = item

        if self.doc is None:
            print("dialect no doc: " + str(self.id))
            return False
        self.get_words()
        self.get_alphabet()
        self.get_phrases()
        self.get_phrase_books()
        self.get_categories()
        self.get_books()
        self.get_contributors()
        self.get_media()
        self.get_galleries()

    def get_words(self):
        word_rows = self.legacy.execute("SELECT ID, WORD_VALUE, DOMINANT_LANGUAGE_WORD_VALUE, PART_OF_SPEECH_ID, "
                                        "CATEGORY_ID, ABORIGINAL_LANGUAGE_SENTENCE, DOMINANT_LANGUAGE_SENTENCE, "
                                        "ASSIGNED_USR_ID, CONTRIBUTER, CULTURAL_NOTE, PHONETIC_INFO, REFERENCE, "
                                        "IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID, AVAILABLE_IN_CHILDRENS_ARCHIVE"
                                        ", STATUS_ID, DOMINANT_LANGUAGE_DEFINITION, CHANGE_DTTM "
                                        "FROM FIRSTVOX.WORD_ENTRY WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in word_rows:
            word = Word(self, r[0], r[1].strip(), r[2], Data.legacy_pos[r[3]], Data.legacy_categories[r[4]], r[5], r[6],
                        r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18])
            self.legacy_words.append(word)
            i = 12
            if r[i] is not None:
                self.dialect_media.append(r[i])
                if r == 14: break

        got_words = False
        while not got_words:
            try:
                queried_words = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVWord WHERE "
                                                                 "fva:dialect = '"+self.doc.uid+"' "
                                                                 "AND ecm:path STARTSWITH '/FV/Workspaces/Data'"})
                got_words = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))
        for w in queried_words.get("entries"):
            self.nuxeo_words[w.get("fvl:import_id")] = w

    def get_alphabet(self):
        rows = self.legacy.execute("SELECT ID, CHAR_DATA, UPPER_CASE_CHAR_DATA, EXTENDED, ALPH_ORDER, "
                                   "SAMPLE_WORD, SOUND_MEDIA_FILENAME, SOUND_DESCRIPTION, "
                                   "SOUND_CONTRIBUTER, SOUND_RECORDER, SOUND_STATUS_ID, CHANGE_DTTM "
                                   "FROM FIRSTVOX.ORTHOGRAPHY WHERE DICTIONARY_ID = '"+str(self.id)+"'")

        for r in rows:
            self.legacy_letters.append(Letter(self, r[0], r[1], r[2], r[3], r[4], r[5], [r[6], r[7], r[8], r[9], r[10]], r[11]))

        got_letters = False
        while not got_letters:
            try:
                queried_letters = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVCharacter WHERE "
                                                                   "fva:dialect = '"+self.doc.uid+"' AND ecm:path "
                                                                   "STARTSWITH '/FV/Workspaces/Data' "})
                got_letters = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))
        for letter in queried_letters.get("entries"):
            self.nuxeo_letters[letter.get("fvl:import_id")] = letter

    def get_phrases(self):

        phrase_rows = self.legacy.execute("SELECT ID, PHRASE, DOMINANT_LANGUAGE_PHRASE, CATEGORY_ID, ASSIGNED_USR_ID, "
                                          "CONTRIBUTER, CULTURAL_NOTE, REFERENCE, IMAGE_ENTRY_ID, SOUND_ENTRY_ID, "
                                          "VIDEO_ENTRY_ID, AVAILABLE_IN_CHILDRENS_ARCHIVE, STATUS_ID, CHANGE_DTTM "
                                          "FROM FIRSTVOX.PHRASE_ENTRY WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in phrase_rows:
            phrase = Phrase(self, r[0], r[1].strip(), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13])
            self.legacy_phrases.append(phrase)

        got_phrases = False
        while not got_phrases:
            try:
                queried_phrases = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVPhrase WHERE "
                                                                   "fva:dialect = '"+self.doc.uid+"' "
                                                                   "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})
                got_phrases = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        for phrase in queried_phrases.get("entries"):
            self.nuxeo_phrases[phrase.get("fvl:import_id")] = phrase

    def get_phrase_books(self):
        phrase_rows = self.legacy.execute("SELECT ID, DESCR, IMAGE_FILENAME, CHANGE_DTTM "
                                          "FROM FIRSTVOX.PHRASE_CATEGORY WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in phrase_rows:
            p = PhraseBook(self, r[0], r[1].strip(), r[2], r[3])
            self.legacy_phrase_books.append(p)

        for book in Data.categories:
            if book.path.startswith(self.doc.path+"/Phrase Books") and book.get("fva:dialect") == self.doc.uid:
                self.nuxeo_phrase_books[book.get("fvl:import_id")] = book

    def get_categories(self):
        if Data.dialect_categories.get(self.id) is not None:
            for book in Data.dialect_categories.get(self.id):
                self.legacy_categories.append(Category(self, book[0], book[1], book[3], book[4], book[5], book[6], book[7]))

        for book in Data.categories:
            if book.path.startswith(self.doc.path+"/Categories") and book.get("fva:dialect") == self.doc.uid:
                self.nuxeo_categories[book.get("fvl:import_id")] = book

    def get_books(self):
        rows = self.legacy.execute("SELECT ID, ABORIGINAL_LANGUAGE_TITLE, DOMINANT_LANGUAGE_TITLE, ASSIGNED_USR_ID, "
                                   "CONTRIBUTER, CULTURAL_NOTE, IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID, "
                                   "AVAILABLE_IN_CHILDRENS_ARCHIVE, STATUS_ID,  ABORIGINAL_LANGUAGE_INTRO, "
                                   "DOMINANT_LANGUAGE_INTRO, AUTHOR, AUTHOR_REFERENCE, CONTRIBUTER_REFERENCE, "
                                   "DOMINANT_LANGUAGE_TRANSLATION, SSTYPE_ID, CHANGE_DTTM "
                                   "FROM FIRSTVOX.SENTRY_BOOK WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in rows:
            book = Book(self, r[0], r[1], r[2], r[3], r[4], r[5], "", r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18])
            self.legacy_books.append(book)

        got_books = False
        while not got_books:
            try:
                queried_books = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVBook WHERE "
                                                                 "fva:dialect = '"+self.doc.uid+"' "
                                                                 "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})

                got_books = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        for book in queried_books.get("entries"):
            self.nuxeo_books[book.get("fvl:import_id")] = book

        rows = self.legacy.execute("SELECT ID, ABORIGINAL_LANGUAGE_TEXT, DOMINANT_LANGUAGE_TEXT, ASSIGNED_USR_ID, "
                                   "DOMINANT_LANGUAGE_TRANSLATION, SENTRY_BOOK_ID, CULTURAL_NOTE, "
                                   "IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID, CHANGE_DTTM "
                                   "FROM FIRSTVOX.SENTRY WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in rows:
            entry = BookEntry(self, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10])
            self.legacy_book_entries.append(entry)

        got_entries = False
        while not got_entries:
            try:
                queried_entries = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVBookEntry WHERE "
                                                                   "fva:dialect = '"+self.doc.uid+"' "
                                                                   "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})

                got_entries = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        for entry in queried_entries.get("entries"):
            self.nuxeo_book_entries[entry.get("fvl:import_id")] = entry

    def get_contributors(self):

        got_contributors = False
        while not got_contributors:
            try:
                queried_sources = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVContributor WHERE "
                                                                   "fva:dialect = '"+self.doc.uid+"' "
                                                                   "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})

                got_contributors = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        self.nuxeo_contributors = queried_sources.get("entries")

    def get_media(self):
        i = 0
        j = min(len(self.dialect_media), 1000)
        while j <= len(self.dialect_media) and j != 0:
            rows = self.legacy.execute("SELECT ID, FILENAME, DESCR, ASSIGNED_USR_ID, CONTRIBUTER, RECORDER, "
                                       "MEDIA_TYPE_ID, IS_SHARED, STATUS_ID "
                                       "FROM FIRSTVOX.ENTRY_MEDIA WHERE ID IN "+str(tuple(self.dialect_media[i:j]))+"")

            for r in rows:
                file = MediaFile(self, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
                self.legacy_media[r[0]] = file
            i += 1000
            j += 1000
            if j > len(self.dialect_media) > i:
                j = len(self.dialect_media)

        got_entries = False
        while not got_entries:
            try:
                queried_imgs = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVPicture WHERE "
                                                                "fva:dialect = '"+self.doc.uid+"' "
                                                                "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})

                got_entries = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        for img in queried_imgs.get("entries"):
            self.nuxeo_imgs[img.get("fvl:import_id")] = img

        got_entries = False
        while not got_entries:
            try:
                queried_audio = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVAudio WHERE "
                                                                 "fva:dialect = '"+self.doc.uid+"' "
                                                                 "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})

                got_entries = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        for audio in queried_audio.get("entries"):
            self.nuxeo_audio[audio.get("fvl:import_id")] = audio

        got_entries = False
        while not got_entries:
            try:
                queried_video = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVVideo WHERE "
                                                                 "fva:dialect = '"+self.doc.uid+"' "
                                                                 "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})

                got_entries = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        for video in queried_video.get("entries"):
            self.nuxeo_videos[video.get("fvl:import_id")] = video

    def get_galleries(self):
        rows = self.legacy.execute("SELECT ID, FILENAME, DESCR, PHOTOGRAPHER, CONTRIBUTER, RECORDER, "
                                   "STATUS_ID, ALPH_ORDER, YEAR, CAPTION, CHANGE_DTTM "
                                   "FROM FIRSTVOX.ART_GALLERY_ENTRY WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in rows:
            image = GalleryMediaFile(self, r[0], r[1].strip(), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], "art", r[10])
            self.art_gallery.append(image)

        Gallery(self, self.art_gallery, "srt")

        rows = self.legacy.execute("SELECT ID, FILENAME, DESCR, PHOTOGRAPHER, CONTRIBUTER, RECORDER, "
                                   "STATUS_ID, ALPH_ORDER, YEAR, CAPTION, CHANGE_DTTM "
                                   "FROM FIRSTVOX.PHOTO_ALBUM_ENTRY WHERE DICTIONARY_ID = '"+str(self.id)+"'")
        for r in rows:
            image = GalleryMediaFile(self, r[0], r[1].strip(), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], "photo", r[10])
            self.photo_gallery.append(image)

        Gallery(self, self.photo_gallery, "photo")

    def get_links(self):
        rows = self.legacy.execute("SELECT INSTRUCTIONS_MEDIA_FILENAME, INSTRUCTIONS_DESCRIPTION, "
                                   "INSTRUCTIONS_CONTRIBUTER, INSTRUCTIONS_RECORDER, INSTRUCTION_STATUS_ID, "
                                   "MAC_MEDIA_FILENAME, MAC_DESCRIPTION, MAC_CONTRIBUTER, MAC_RECORDER, MAC_STATUS_ID, "
                                   "PC_MEDIA_FILENAME, PC_DESCRIPTION, PC_CONTRIBUTER, PC_RECORDER, PC_STATUS_ID, "
                                   "FROM FIRSTVOX.KEYBOARD ID = '"+str(self.id)+"'")
        for r in rows:
            link = Link(self, r[0], r[0][r[0].rindex('/')+1:], r[1], r[2], r[3], r[4], "instructions")
            self.legacy_links.append(link)
            link = Link(self, r[5], r[5][r[5].rindex('/')+1:], r[6], r[7], r[8], r[9], "mac")
            self.legacy_links.append(link)
            link = Link(self, r[10], r[10][r[10].rindex('/')+1:], r[11], r[12], r[13], r[14], "pc")
            self.legacy_links.append(link)

        got_links = False
        while not got_links:
            try:
                queried_links = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVLink WHERE "
                                                                 "fva:dialect = '"+self.doc.uid+"' "
                                                                 "AND ecm:path STARTSWITH '/FV/Workspaces/Data' "})
                got_links = True
            except HTTPError:
                self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        self.nuxeo_links = queried_links.get("entries")

