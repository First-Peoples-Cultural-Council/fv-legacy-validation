from src.authorization import Authorize
from nuxeo.client import Nuxeo
from nuxeo.models import Document, FileBlob


class Updater:

    def __init__(self):
        self.nuxeo = Authorize.nuxeo

    def update_property(self, doc, nuxeo_str, value):
        doc.properties[nuxeo_str] = value
        doc.save()

    def create_doc(self, path, name, type, properties, file_path=""):
        new_doc = Document(
            name=name,
            type=type,
            properties=properties) # a dict of propertyname: value
        ws = self.nuxeo.documents.create(new_doc, parent_path=path)
        if file_path:
            blob = FileBlob(file_path)
            batch = self.nuxeo.uploads.batch()
            batch.upload(blob)
            uploaded = self.nuxeo.uploads.upload(batch, blob)
            operation = self.nuxeo.operations.new('Blob.AttachOnDocument')
            operation.params = {'document': path+"/"+name}
            operation.input_obj = uploaded
            operation.execute()
        ws.save()
        return ws
