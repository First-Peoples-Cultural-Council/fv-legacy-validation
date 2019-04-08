from src.authorization import Authorize
from src.Updater import Updater
from nuxeo.exceptions import HTTPError
from nuxeo.client import Nuxeo
import re


class Gallery:

    def __init__(self):
        self.legacy = Authorize.cursor
        self.nuxeo = Authorize.nuxeo
        self.dialects = {}
        dialects = None
        got_dialects = False
        while not got_dialects:
            try:
                dialects = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVDialect WHERE ecm:path STARTSWITH "
                                                                "'/FV/Workspaces/Data'"})
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

    def create_galleries(self, id, contributors=None):
        art_gallery, photo_gallery = self.get_galleries(id)
        doc = self.dialects[id]

        if not contributors:
            contributors = {}
            queried = None
            got_con = False
            while not got_con:
                try:
                    queried = self.nuxeo.documents.query(opts={'query': "SELECT * FROM FVContributor WHERE ecm:path "
                                                               "STARTSWITH '"+doc.path+"/Contributors'"})
                    got_con = True
                except HTTPError:
                    self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

            entries = queried.get("entries")
            for item in entries:
                contributors[item.get("dc:title")] = item.uid

        if art_gallery:
            related_pics = self.get_pictures(art_gallery, doc.path, contributors)
            print([doc.path+"/Portal/", "Art Gallery", "FVGallery", {'dc:title': "Art Gallery",
                                                                     "fv:related_pictures": related_pics}])
            art_gal = Updater().create_doc(doc.path+"/Portal/", "Art Gallery", "FVGallery", {'dc:title': "Art Gallery",
                                           "fv:related_pictures": related_pics})
        if photo_gallery:
            related_pics = self.get_pictures(photo_gallery, doc.path, contributors)
            print([doc.path+"/Portal/", "Photo Gallery", "FVGallery", {'dc:title': "Photo Gallery",
                                                                     "fv:related_pictures": related_pics}])
            photo_gal = Updater().create_doc(doc.path+"/Portal/", "Photo Gallery", "FVGallery", {'dc:title': "Photo Gallery",
                                             "fv:related_pictures": related_pics})

    def get_pictures(self, gallery, path, contributors):
        related_pics = []
        for pic in gallery:
            change = None
            if pic[10]:
                change = str(pic[10])[2:10]
            source = self.contributors(pic[4], contributors, path)
            recorder = self.contributors(pic[5], contributors, path)
            pic_title = ""
            if pic[1]:
                if pic[1].count("/"):
                    pic_title = pic[1][pic[1].index("/")+1:]
                else:
                    pic_title = pic[1][pic[1].index("\\")+1:]
            pic_properties = {'dc:title': pic_title, "fvm:source": source, "fvm:recorder": recorder, "dc:description": pic[2],
                              "fvl:import_id": pic[0], "fvl:change_date": change, "fvl:status_id": pic[6]}
            pic = Updater().create_doc(path+"/Resources/", pic_title, "FVPicture", pic_properties, pic[1])
            related_pics.append(pic.uid)
        return related_pics

    def contributors(self, contributors, contributors_list, path):
        match = "(?<!\d)([,/](?!( S[rR])|( Elder)|(.$)))|((( and )|( & ))(?!(Cultur)|(historian)|(mentor)|(Hand)|(Media)|(Elder)|(dictionary)|(Wildlife)|(Herring)|(Learn)|(Language)))"
        sources = []
        if contributors:
            if contributors.startswith("http") or contributors.startswith("www.") or contributors.count(".com"):
                cons = [contributors]
            else:
                cons = re.split(match, contributors, re.IGNORECASE)
                cons = [con for con in cons if con not in [",", "/", "", " and ", " & "] and con is not None]
            for name in cons:
                if name in contributors_list:
                    sources.append(contributors_list.get(name))
                else:
                    con = Updater().create_doc(path+"/Contributors/", name, "FVContributor", {'dc:title': name})
                    sources.append(con.uid)
        return sources
