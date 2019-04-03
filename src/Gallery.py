from src.authorization import Authorize
from src.Updater import Updater
from nuxeo.exceptions import HTTPError
import re


class Gallery:

    def __init__(self):
        self.legacy = Authorize.cursor
        nuxeo = Authorize.nuxeo
        self.dialects = {}
        dialects = None
        got_dialects = False
        while not got_dialects:
            try:
                dialects = nuxeo.documents.query(opts={'query': "SELECT * FROM FVDialect "
                                                                "WHERE ecm:path STARTSWITH '/FV/Workspaces/Data'"})
                got_dialects = True
            except HTTPError:
                pass

        entries = dialects.get("entries")
        for item in entries:
            self.dialects[item.get("fvl:import_id")] = item

    def get_galleries(self, id):
        rows = self.legacy.execute("SELECT ID, FILENAME, DESCR, PHOTOGRAPHER, CONTRIBUTER, RECORDER, "
                                   "STATUS_ID, ALPH_ORDER, YEAR, CAPTION, CHANGE_DTTM "
                                   "FROM FIRSTVOX.ART_GALLERY_ENTRY WHERE DICTIONARY_ID = '"+str(id)+"'")

        art_gallery = list(rows)

        rows = self.legacy.execute("SELECT ID, FILENAME, DESCR, PHOTOGRAPHER, CONTRIBUTER, RECORDER, "
                                   "STATUS_ID, ALPH_ORDER, YEAR, CAPTION, CHANGE_DTTM "
                                   "FROM FIRSTVOX.PHOTO_ALBUM_ENTRY WHERE DICTIONARY_ID = '"+str(id)+"'")

        photo_gallery = list(rows)
        return art_gallery, photo_gallery

    def create_galleries(self, id):  # create_doc( path, name, type, properties), properties must have dc:title
        art_gallery, photo_gallery = self.get_galleries(id)
        doc = self.dialects[id]
        if art_gallery:
            related_pics = self.get_pictures(art_gallery, doc.path)
            art_gal = Updater().create_doc(doc.path+"/Portal/", "Art Gallery", "FVGallery", {'dc:title': "Art Gallery",
                                                                                                "fv:related_pictures": related_pics})
        if photo_gallery:
            related_pics = self.get_pictures(photo_gallery, doc.path)
            photo_gal = Updater().create_doc(doc.path+"/Portal/", "Photo Gallery", "FVGallery", {'dc:title': "Photo Gallery",
                                                                                                    "fv:related_pictures": related_pics})
            # how to update state, create not published

    def get_pictures(self, gallery, path):
        match = "(^[^(https:\/\/)|(www.)].*)((?<!\d)([,/](?!( S[rR])|( Elder)|(.$)))|(?:(( and )|( & ))(?!(Cultur)|(historian)|(mentor)|(Hand)|(Media)|(Elder)|(dictionary)|(Wildlife)|(Language))))"
        updater = Updater()
        related_pics = []
        for pic in gallery:
            source = []
            recorder = []
            change = None
            if pic[10]:
                change = str(pic[10])[2:10]
            if pic[5]:
                recs = re.split(match, pic[5], re.IGNORECASE)
                recs = [con for con in recs if con not in [",", "/", "", " and ", " & "] and con is not None]
                for name in recs:
                    rec = updater.create_doc(path+"/Contributors/", name, "FVContributor", {'dc:title': name})
                    recorder.append(rec.uid)
            if pic[4]:
                cons = re.split(match, pic[4], re.IGNORECASE)
                cons = [con for con in cons if con not in [",", "/", "", " and ", " & "] and con is not None]
                for name in cons:
                    con = updater.create_doc(path+"/Contributors/", name, "FVContributor", {'dc:title': name})
                    source.append(con.uid)
            pic_title = ""
            if pic[1]:
                if pic[1].count("/"):
                    pic_title = pic[1][pic[1].index("/")+1:]
                else:
                    pic_title = pic[1][pic[1].index("\\")+1:]
            pic_properties = {'dc:title': pic_title, "fvm:source": source, "fvm:recorder": recorder, "dc:description": pic[2],
                              "fvl:import_id": pic[0], "fvl:change_date": change, "fvl:status_id": pic[6]}
            pic = updater.create_doc(path+"/Resources/", pic_title, "FVPicture", pic_properties, pic[1])
            related_pics.append(pic.uid)
        return related_pics
