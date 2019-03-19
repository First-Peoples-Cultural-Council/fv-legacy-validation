from src.LetterMapper import LetterMapper
from src.Item import Item


class MediaFile(Item):

    def __init__(self, dialect, file_id, filename, description, user, contributor, recorder, type_id, shared, status):
        if filename is None:
            super().__init__(dialect, file_id, filename, user)
        else:
            super().__init__(dialect, file_id, filename[filename.rindex('/')+1:], user)
        self.description = description
        self.contributor = contributor
        self.recorder = recorder
        self.type = type_id
        self.shared = shared
        self.status = status

    def validate(self):
        types = {1: self.dialect.nuxeo_imgs, 2: self.dialect.nuxeo_videos, 3: self.dialect.nuxeo_audio}
        self.doc = types[self.type].get(self.id)
        if super().validate():
            self.file_validate()
            self.recorder_validate()
            self.validate_text(self.description, "dc:description")
            self.validate_int(self.shared, "fvm:shared")
            self.contributor_validate(self.contributor, "fvm:source")
            self.status_validate()

    def file_validate(self):
        if not self.exists("https://preprod.firstvoices.com/nuxeo/nxfile/default/"+str(self.doc.uid)+"/file:content/"+self.title):
            print(self.title)
            print(self.doc.uid)
            print("file not found ?? " + self.doc.uid)

    def recorder_validate(self):
        self.contributor_validate(self.recorder, "fvm:recorder")


class UnEnteredMediaFile(MediaFile):

    def __init__(self, dialect, filename, description, contributor, recorder, type_id, status):
        super().__init__(dialect, None, filename, description, None, contributor, recorder, type_id, 0, status)

    def validate(self):
        types = {1: self.dialect.nuxeo_imgs, 2: self.dialect.nuxeo_videos, 3: self.dialect.nuxeo_audio}
        for doc in types[self.type].values():
            if doc.title == self.title or LetterMapper().compare(self.title, doc.title):
                self.doc = doc
                break

        if Item.validate(self):
            self.file_validate()
            self.recorder_validate()
            self.validate_int(self.shared, "fvm:shared")
            self.validate_text(self.description, "dc:description")
            self.contributor_validate(self.contributor, "fvm:source")
            self.status_validate()


class GalleryMediaFile(MediaFile):

    def __init__(self, dialect, file_id, filename, description, photographer, contributor, recorder, status, order, year, caption, gallery, change):
        super().__init__(dialect, file_id, filename, description, None, contributor, recorder, 1, None, status)  # shared ?
        self.change = change
        self.photographer = photographer  ## none of these are nuxeo properties
        self.order = order
        self.year = year
        self.caption = caption
        self.gallery = gallery
