from src.Item import Item
from src.MediaFile import UnEnteredMediaFile


class PhraseBook(Item):

    def __init__(self, dialect, item_id, name, image, change):
        super().__init__(dialect, item_id, name, change=change)
        self.image = image

    def validate(self):
        self.doc = self.dialect.nuxeo_phrase_books.get(self.id)
        super().validate()

    def image_validate(self):
        if self.image is None:
            self.validate_uid(self.image, "fvcategory:image", self.dialect.nuxeo_imgs.values)
        else:
            if self.image.count('/'):
                self.validate_uid(self.image[self.image.rindex('/')+1:], "fvcategory:image", self.dialect.nuxeo_imgs.values())
                for f in self.dialect.legacy_media.values():
                    if f.filename == self.image:
                        print("~~~ unentered media found in media")
                        return
            else:
                self.validate_uid(self.image[self.image.rindex('\\')+1:], "fvcategory:image", self.dialect.nuxeo_imgs.values())
                for f in self.dialect.legacy_media.values():
                    if f.filename == self.image:
                        print("~~~ unentered media found in media")
                        return
            img = UnEnteredMediaFile(self.dialect, self.image, None, None, None, 1, None)
            img.validate()

    def quality_check(self):
        if not self.doc.get("dc:title"):
            self.dialect.flags.missingData(self, "dc:title")


class Category(PhraseBook):  # review validation

    def __init__(self, dialect, item_id, name, private, parent, namefr, image, change):
        super().__init__(dialect, item_id, name, image, change)
        self.private = private  # don't correspond to nuxeo
        self.parent = parent
        self.name_fr = namefr

    def validate(self):
        self.doc = self.dialect.nuxeo_categories.get(self.id)
        Item.validate(self)

