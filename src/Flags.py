import re

class Exceptions:

    def __init__(self, dialect):
        self.dialect = dialect
        self.LetterErrors = []
        self.WordErrors = []
        self.PhraseErrors = []
        self.PhraseBookErrors = []
        self.AudioErrors = []
        self.VideoErrors = []
        self.ImgErrors = []
        self.SongErrors = []
        self.StoryErrors = []
        self.SongEntryErrors = []
        self.StoryEntryErrors = []
        self.LinkErrors = []
        self.CatErrors = []
        self.PortalErrors = []
        self.DialectErrors = []
        self.LetterQuality = []
        self.WordQuality = []
        self.PhraseQuality = []
        self.PhraseBookQuality = []
        self.AudioQuality = []
        self.VideoQuality = []
        self.ImgQuality = []
        self.SongQuality = []
        self.StoryQuality = []
        self.SongEntryQuality = []
        self.StoryEntryQuality = []
        self.LinkQuality = []
        self.CatQuality = []
        self.PortalQuality = []
        self.DialectQuality = []
        self.item = None
        self.item_update = False
        self.update = []
        self.update_names = ["fvl:change_date", "fvl:status_id", "fv:available_in_childrens_archive", "fvm:shared", "fvcharacter:extended", "fvl:assigned_usr_id"]
        self.types = {"<class 'src.Portal.Portal'>": [self.PortalErrors, self.PortalQuality], "<class 'src.Link.Link'>": [self.LinkErrors, self.LinkQuality],
                      "<class 'src.Dialect.Dialect'>": [self.DialectErrors, self.DialectQuality], "<class 'src.Word.Word'>": [self.WordErrors, self.WordQuality],
                      "<class 'src.Category.PhraseBook'>": [self.PhraseBookErrors, self.PhraseBookQuality], "<class 'src.Phrase.Phrase'>": [self.PhraseErrors, self.PhraseQuality],
                      "<class 'src.Letter.Letter'>": [self.LetterErrors, self.LetterQuality], "<class 'src.Category.Category'>": [self.CatErrors, self.CatQuality],
                      "<class 'src.Phrase.SamplePhrase'>": [self.PhraseErrors, self.PhraseQuality]}
        self.property_name = {"fvl:status_id": "Status", "fvl:change_date": "Legacy Change Date", "fvl:assigned_usr_id": "Assigned User", "dc:title": "Title",
                              "fv:source": "Contributor", "fv:definitions": "Definition", "fv:literal_translation": "Literal Translation", "fv:reference": "Reference",
                              "fv:cultural_note": "Cultural Note", "fv:related_pictures": "Related Pictures", "fv:related_videos": "Related Videos", "fv:related_audio": "Related Audio",
                              "fv:available_in_childrens_archive": "Available in Children's Archive", "fvbook:introduction": "Introduction",
                              "fvbook:introduction_literal_translation": "Introduction Literal Translation", "fvbook:title_literal_translation": "Title Literal Translation",
                              "fvbook:dominant_language_translation": "Translation", "fvbook:author": "Author", "fvbook:type": "Type of Book: Song or Story ",
                              "fvbookentry:dominant_language_text": "Text Translation", "fvcategory:image": "Category Image", "fvdialect:short_url": "Dialect Short URL",
                              "fvdialect:dominant_language": "Dialect Dominant Language", "fvdialect:country": "Dialect Country", "fvdialect:region": "Dialect Region",
                              "fva:language": "Language Group", "fva:family": "Language Family", "fvdialect:contact_information": "Dialect Contact Information",
                              "dc:description": "description", "fvcharacter:alphabet_order": "Letter Order", "fvcharacter:upper_case_character": "Upper Case",
                              "fvcharacter:related_words": "Related Words", "fvcharacter:extended": "Character Extended", "fvm:shared": "Shared",
                              "fvm:source": "Contributor", "fvm:recorder": "Recorder", "fv-phrase:phrase_books": "Phrase Book", "fv-portal:greeting": "Portal Greeting",
                              "fv-portal:about": "Portal About", 'fv-portal:featured_words': "First Words", "fv-portal:news": "News", "fv-portal:related_links": "Related Links",
                              "fv-portal:logo": "Logo", "fv-portal:featured_audio": "Featured Audio", "fv-portal:background_bottom_image": "Background Bottom Image",
                              "fv-portal:background_top_image": "Background Top Image", "fv-word:pronunciation": "Pronunciation", 'fv-word:part_of_speech': "Part of Speech",
                              'fv:word_categories': "Category", "fv-word:related_phrases": "Related Phrases", "fvbook:sort_map": "Sort Order", "file:content": "File Link"}

    def itemNotFound(self, item):  # related phrase, sample word?  wrong state??
        group = self.getGroup(item)[0]
        group.append(["Item not Found", item.title, item.id, "", "", "", "", ""])

    def fileMissing(self, item):
        group  = self.getGroup(item)[0]
        group.append(["File does not Exist", item.title, item.id, "File linked does not exist", "", "", "", ""])

    def dataMismatch(self, item, nuxeo_str, expected, actual):  # what to do when item is attached to another item?
        group = self.getGroup(item)[0]
        expected = self.remove_html(expected)
        actual = self.remove_html(actual)
        self.item_update = self.toUpdate(item.doc, item.title, item.id, nuxeo_str, expected, actual)
        if not self.unexpectedProperty(group, item.title, item.id, self.property_name[nuxeo_str], expected, actual, item.doc.uid) and \
            not self.propertyEmpty(group, item.title, item.id, self.property_name[nuxeo_str], expected, actual, item.doc.uid) and \
            not self.multipleContributors(group, item.title, item.id, self.property_name[nuxeo_str], expected, actual, item.doc.uid) \
            and not self.switched("Data Mismatch", group, item.title, item.id, self.property_name[nuxeo_str], expected, actual, item.doc.uid):
                group.append(["Data Mismatch", item.title, item.id, self.property_name[nuxeo_str], expected, actual, item.doc.uid, self.item_update])

    def wrongOrder(self, item, nuxeo_str, expected, actual):
        group = self.getGroup(item)[0]
        expected = self.remove_html(expected)
        actual = self.remove_html(actual)
        self.item_update = self.toUpdate(item.doc, item.title, item.id, nuxeo_str, expected, actual)
        group.append(["Wrong Order", item.title, item.id, self.property_name[nuxeo_str], expected, actual, item.doc.uid, self.item_update])

    def propertyEmpty(self, group, title, id, property_name, expected, actual, uid):
        if not actual and not self.switched("Unexpected Property", group, title, id, property_name, expected, None, uid):
            group.append(["Property Empty", title, id, property_name, expected, None, uid, self.item_update])
            return True
        return False

    def unexpectedProperty(self, group, title, id, property_name, expected, actual, uid):
        if not expected and not self.switched("Property Empty", group, title, id, property_name, None, actual, uid):
            group.append(["Unexpected Property", title, id, property_name, None, actual, uid, self.item_update])
            return True
        return False

    def multipleContributors(self, group, title, id, property_name, expected, actual, uid):
        if property_name in ("Contributor", "Recorder", "Author") and len(expected) > 1:
            group.append(["Multiple Contributors", title, id, property_name, expected, actual, uid, self.item_update])
            return True
        return False

    def switched(self, name, group, title, id, property_name, expected, actual, uid):
        if property_name == "Literal Translation" and [name, title, id, "Definition", actual, expected, uid, self.item_update] in group:
            group.append(["Switched Definition and Literal Translation", title, id, "Definition, Literal Translation", str(actual)+", "+str(expected), str(expected)+", "+str(actual), uid, self.item_update])
            group.remove([name, title, id, "Definition", actual, expected, uid, self.item_update])
            return True
        if property_name == "Definition" and [name, title, id, "Literal Translation", actual, expected, uid, self.item_update] in group:
            group.append(["Switched Definition and Literal Translation", title, id, "Definition, Literal Translation", str(expected)+", "+str(actual), str(actual)+", "+str(expected), uid, self.item_update])
            group.remove([name, title, id, "Literal Translation", actual, expected, uid, self.item_update])
            return True
        return False

    def getGroup(self, item):
        self.item = item
        if str(item.__class__) in ("<class 'src.MediaFile.MediaFile'>", "<class 'src.MediaFile.UnEnteredMediaFile'>"):
            group = self.getMediaType()
        elif str(item.__class__) == "<class 'src.Book.Book'>":
            group = self.getBookType()
        elif str(item.__class__) == "<class 'src.BookEntry.BookEntry'>":
            group = self.getEntryType()
        else:
            group = self.types[str(item.__class__)]
        return group

    def getMediaType(self):
        if self.item is None:
            print("media item not exist ??")
            print(self.item)
            return False
        types = {1: [self.ImgErrors, self.ImgQuality], 2: [self.VideoErrors, self.VideoQuality], 3: [self.AudioErrors, self.AudioQuality]}
        return types[self.item.type]

    def getBookType(self):
        if self.item is None:
            print("book item not exist ??")
            print(self.item)
            return False
        types = {1: [self.SongErrors, self.SongQuality], 2: [self.StoryErrors, self.StoryQuality]}
        return types[self.item.sstype]

    def getEntryType(self):
        if self.item is None:
            print("entry item not exist ??")
            print(self.item)
            return False
        types = {1: [self.SongEntryErrors, self.SongEntryQuality], 2: [self.StoryEntryErrors, self.StoryEntryQuality]}
        return types[self.item.book.sstype]

    def missingData(self, item, nuxeo_str):
        group = self.getGroup(item)[1]
        group.append([" has no "+self.property_name[nuxeo_str].lower(), item.title, self.property_name[nuxeo_str], item.id, item.doc.uid])

    def toUpdate(self, doc, title, item_id, nuxeo_str, expected, actual):
        if nuxeo_str in self.update_names:
            self.update.append([doc, title, self.property_name[nuxeo_str], item_id, doc.uid, nuxeo_str, expected, actual])
            return True
        return False

    def remove_html(self, text):
        if text:
            text = re.sub('<[^<]+?>', "", str(text))
        return text

