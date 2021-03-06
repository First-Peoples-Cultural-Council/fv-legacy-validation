from src.Item import Item


class Link(Item):

    def __init__(self, dialect, filename, name, description, contributor, recorder, status, type):
        super().__init__(dialect, None, name)
        self.filename = filename
        self.description = description
        self.contributor = contributor ##  these properties don't exist in nuxeo
        self.recorder = recorder ##
        self.status = status ##
        self.type = type

    def validate(self):
        for file in self.dialect.nuxeo_links:
            if self.title == file.title:
                self.doc = file

        if super().validate():
            self.validate_text(self.description, "dc:description")

    def file_validate(self):
        if not self.doc.get("fvlink:url"):
            if not self.exists("https://preprod.firstvoices.com/nuxeo/nxfile/default/"+str(self.doc.uid)+"/file:content/"+self.title):
                self.dialect.flags.fileMissing(self)
                print(self.title)
                print(self.doc.uid)
                print("link not found ?? " +self.doc.uid)
        else:
            if not self.exists(self.doc.get("fvlink:url")):
                self.dialect.flags.fileMissing(self)

    def quality_check(self):
        if not self.doc.get("dc:title"):
            self.dialect.flags.missingData(self, "dc:title")
        if not self.doc.get("dc:description"):
            self.dialect.flags.missingData(self, "dc:description")
        if not self.doc.get("fvlink:url") and not self.doc.get("file:content").get("data"):
            self.dialect.flags.missingData(self, "file:content")
