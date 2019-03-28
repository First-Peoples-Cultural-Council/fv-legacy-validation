from src.authorization import Authorize
from src.LetterMapper import LetterMapper
import re
import requests


class Item:

    def __init__(self, dialect, item_id, title, user=None, change=None):
        self.nuxeo = Authorize.nuxeo
        self.legacy = Authorize.cursor
        self.dialect = dialect
        self.id = item_id
        self.title = title
        self.user = user
        self.change = change
        self.status = None
        self.doc = None

    def check_last_modified(self):  # maybe check dc:contributors too before updating ?
        last = self.doc.get("dc:lastContributor")
        admin = ["dyona", "Administrator", "awadmin", "NuxeoAdmin", "coakenfold", "lalia_cann", "kyra@fpcc.ca",
                 "murray@fpcc.ca", "vtr_monk@mac.com"]
        if last in admin:
            return True
        return False

    def validate(self):
        if self.doc is not None:
            if self.check_last_modified():
                self.title_validate()
                self.user_validate()
                self.change_validate()
                return True
        else:
            self.dialect.flags.itemNotFound(self)
            print("++++")
            print(str(self.__class__) + str(self.id))
            return False

    def validate_text(self, legacy_name, nuxeo_str):
        if legacy_name is None and self.doc.get(nuxeo_str) is None:
            return True
        if legacy_name is None or self.doc.get(nuxeo_str) is None:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))
            return False
        if self.doc.get(nuxeo_str).count("<br />") != 0:
            legacy_name = legacy_name.replace("\r\n", "<br />")
        if not isinstance(legacy_name, str):
            for name in legacy_name:
                if name.strip() not in self.doc.get(nuxeo_str):
                    match = False
                    for nux in self.doc.get(nuxeo_str):
                        if LetterMapper().compare(name.strip(), nux.strip()):
                            match = True
                            break
                    if not match:
                        self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))  # update these names
                        print(name.strip())
                        print(self.doc.get(nuxeo_str))
                        print(str(self.__class__) + str(self.id))
                        return False
        elif legacy_name.strip() == self.doc.get(nuxeo_str).strip():
            return True
        elif not LetterMapper().compare(legacy_name.strip(), self.doc.get(nuxeo_str).strip()):
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))
            print(legacy_name.strip())
            print(self.doc.get(nuxeo_str).strip())
            print(str(self.__class__) + str(self.id))
            return False

    def validate_int(self, legacy_name, nuxeo_str):
        if legacy_name is None and self.doc.get(nuxeo_str) is None:
            return True
        if legacy_name is None or self.doc.get(nuxeo_str) is None:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))
        if legacy_name == self.doc.get(nuxeo_str):
            return True
        self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))
        print(legacy_name)
        print(self.doc.get(nuxeo_str))
        print(str(self.__class__) + str(self.id))
        return False

    def validate_translation(self, legacy_def, nuxeo_str):
        definitions = self.doc.get(nuxeo_str)
        if legacy_def is None and len(definitions) == 0:
            return True
        if legacy_def is None or len(definitions) == 0:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_def, self.doc.get(nuxeo_str))
            return False
        if legacy_def != definitions[0]['translation']:
            if not LetterMapper().compare(legacy_def, definitions[0]['translation']):
                self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_def, definitions[0]['translation'])
                print(legacy_def)
                print(definitions[0]['translation'])
                print("text defs don't match")
                print(str(self.__class__) + str(self.id))
                return False

    def validate_uid(self, legacy_name, nuxeo_str, nuxeo_docs):
        if legacy_name is None and self.doc.get(nuxeo_str) is None or legacy_name is None and len(self.doc.get(nuxeo_str)) == 0:
            return True
        if self.doc.get(nuxeo_str) is None or len(self.doc.get(nuxeo_str)) == 0:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))
            return False
        nuxeo_titles = []
        if not isinstance(self.doc.get(nuxeo_str), str):
            for uid in self.doc.get(nuxeo_str):
                for doc in nuxeo_docs:
                    if doc.uid == uid:
                        nuxeo_titles.append(doc.get("dc:title").strip())
                        break
        else:
            if legacy_name == 'B_E_Welcome.mp3':
                print('isss str')
                print(self.doc.get(nuxeo_str))
            uid = self.doc.get(nuxeo_str)
            for doc in nuxeo_docs:
                if doc.uid == uid:
                    nuxeo_titles.append(doc.get("dc:title").strip())
                    break
        if legacy_name is None:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, nuxeo_titles)
            return False
        if not isinstance(legacy_name, str):
            for name in legacy_name:
                if name not in nuxeo_titles:
                    self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, nuxeo_titles)
                    print(legacy_name)
                    print(nuxeo_titles)
                    print(str(self.__class__) + str(self.id))
                    return False
        else:
            if legacy_name not in nuxeo_titles:
                self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, nuxeo_titles)
                print(legacy_name)
                print(nuxeo_titles)
                print(str(self.__class__) + str(self.id))
                return False

    def title_validate(self):
        self.validate_text(self.title, "dc:title")

    def user_validate(self): # maybe expand or not depending on further user validation
        self.validate_int(self.user, "fvl:assigned_usr_id")

    def contributor_validate(self, legacy_contributor, nuxeo_str):  # remove old multiple ppl contributors
        if legacy_contributor is None and len(self.doc.get(nuxeo_str)) == 0:
            return True
        if legacy_contributor is None or len(self.doc.get(nuxeo_str)) == 0:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_contributor, self.doc.get(nuxeo_str))
            return False
        contributors = re.split("^[^(https:\/\/)](.*)(?<!\d)([,/](?!( S[rR])|( Elder)|(.$)))|(?:(( and )|( & ))(?!(Culture)|(historian)|(mentor)|(Hand)|(Media)|(Elder)))", legacy_contributor, re.IGNORECASE)
        contributors = [con for con in contributors if con in [",", "/", "", " and ", " & "]]
        sources = []
        for source in self.doc.get(nuxeo_str):
            for c in self.dialect.nuxeo_contributors:
                if c.uid == source:
                    sources.append(c.title.strip())
                    break
        for con in contributors:
            if con.strip() not in sources:
                match = False
                for s in sources:
                    if LetterMapper().compare(con.strip(), s.strip()):
                        match = True
                        break
                if not match:
                    self.dialect.flags.dataMismatch(self, nuxeo_str, contributors, sources)
                    print(contributors)
                    print(sources)
                    print(self.id)
                    return False

    def status_validate(self):  # what property shows whether public or not ?
        # status_code = {1: "Enabled", 2: "Disabled", 3: "Deleted", 4: "None", 0: "New"}
        self.validate_int(self.status, "fvl:status_id")
        # if status_code[self.status] != self.doc.state:
        #     print(status_code[self.status])
        #     print(self.doc.state)
        #     print("~~~ should not be state "+str(self.__class__)+str(self.id))

    def change_validate(self):
        self.validate_text(str(self.change)[2:10], "fvl:change_date")

    def exists(self, path):
        connect = requests.head(path)
        return connect.status_code in [200, 302]

    def html_strip(self, html_string):
        return re.sub('<[^<]+?>', '', html_string)
