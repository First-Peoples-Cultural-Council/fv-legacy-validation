from src.authorization import Authorize
from nuxeo.client import Nuxeo
from nuxeo.models import Document


class Updater:

    def __init__(self):
        self.nuxeo = Authorize.nuxeo

    def update_property(self, doc, nuxeo_str, value):
        doc.properties[nuxeo_str] = value
        doc.save()

    def create_doc(self, path, name, type, properties):
        new_doc = Document(
            name=name,
            type=type,
            properties=properties) # a dict of propertyname: value
        ws = self.nuxeo.documents.create(new_doc, parent_path=path)
        ws.save()
        return ws