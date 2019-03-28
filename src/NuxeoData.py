from src.authorization import Authorize
from nuxeo.exceptions import HTTPError
from nuxeo.client import Nuxeo
import re


class Data:

    def __init__(self):
        nuxeo = Authorize.nuxeo
        legacy = Authorize.cursor
        self.dialect_categories = {}
        self.legacy_categories = {}
        self.legacy_pos = {}
        self.categories = []
        self.all_categories = {}
        self.shared_categories = {}
        self.private_categories = {}
        self.nuxeo_lang_fam = []
        self.legacy_lang_fam = {}
        self.nuxeo_lang_grp = []
        self.legacy_lang_grp = {}
        self.legacy_themes = {}

        rows = legacy.execute("select ID, NAME, BACKGROUND_BOTTOM_FILENAME, BACKGROUND_TOP_FILENAME, PREVIEW_IMAGE_FILENAME"
                              " from FIRSTVOX.THEME")
        for r in rows:
            self.legacy_themes[r[0]] = r

        rows = legacy.execute("select ID, CODE, DICTIONARY_ID, IS_PRIVATE, PARENT_CATEGORY, CODEFR, IMAGE_FILENAME, "
                              "CHANGE_DTTM from FIRSTVOX.WORD_CATEGORY")
        for r in rows:
            self.legacy_categories[r[0]] = re.sub('[/()\- ]+', "_", r[1]).lower().strip("_")
            if r[2] is not None:
                if self.dialect_categories.get(r[2]):
                    self.dialect_categories[r[2]] = self.dialect_categories.get(r[2]).append(r)
                else: self.dialect_categories[r[2]] = [r]

        rows = legacy.execute("select ID, CODE from FIRSTVOX.PART_OF_SPEECH")
        for r in rows:
            self.legacy_pos[r[0]] = re.sub('[/()\- ]+', "_", r[1]).lower().strip("_")

        get_categories = False
        while not get_categories:
            try:
                category = nuxeo.documents.query(opts={'query': "SELECT * FROM FVCategory WHERE ecm:path STARTSWITH"
                                                        " '/FV/Workspaces/SharedData/Shared Categories'"})
                get_categories = True
            except HTTPError:
                nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        entries = category.get("entries")
        for item in entries:
            self.categories.append(item)
            self.shared_categories[item.uid] = re.sub("[/()\- ]+", "_", item.get('dc:title')).lower()
            self.all_categories[item.uid] = re.sub("[/()\- ]+", "_", item.get('dc:title')).lower()

        get_categories = False
        while not get_categories:
            try:
                category = nuxeo.documents.query(opts={'query': "SELECT * FROM FVCategory WHERE ecm:path STARTSWITH"
                                                       " '/FV/Workspaces/Data' "})
                get_categories = True
            except HTTPError:
                nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        entries = category.get("entries")
        for item in entries:
            self.categories.append(item)
            self.private_categories[item.uid] = re.sub("[/()\- ]+", "_", item.get('dc:title')).lower()
            self.all_categories[item.uid] = re.sub("[/()\- ]+", "_", item.get('dc:title')).lower()

        rows = legacy.execute("select ID, NAME "
                              "from FIRSTVOX.DICTIONARY_FAMILY")
        for r in rows:
            self.legacy_lang_fam[r[0]] = r[1]

        get_lang_fam = False
        while not get_lang_fam:
            try:
                families = nuxeo.documents.query(opts={'query': "SELECT * FROM FVLanguage WHERE ecm:path STARTSWITH"
                                                                " '/FV/Workspaces/Data' "})
                get_lang_fam = True
            except HTTPError:
                nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        self.nuxeo_lang_fam = families.get("entries")

        rows = legacy.execute("select ID, DESCR "
                              "from FIRSTVOX.LANGUAGE_GROUP")
        for r in rows:
            self.legacy_lang_grp[r[0]] = r[1]

        get_lang_grp = False
        while not get_lang_grp:
            try:
                groups = nuxeo.documents.query(opts={'query': "SELECT * FROM FVLanguageFamily WHERE ecm:path STARTSWITH"
                                                                " '/FV/Workspaces/Data' "})
                get_lang_grp = True
            except HTTPError:
                nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

        self.nuxeo_lang_grp = groups.get("entries")
