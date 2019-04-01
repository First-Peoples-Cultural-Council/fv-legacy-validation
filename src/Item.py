from src.authorization import Authorize
from src.LetterMapper import LetterMapper
import re
import requests
import calendar


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
            self.quality_check()
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
        if not legacy_name and not self.doc.get(nuxeo_str):
            return True
        if not legacy_name or not self.doc.get(nuxeo_str):
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
                        self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_name, self.doc.get(nuxeo_str))
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
            return False
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
        if len(definitions) == 0:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_def, None)
            return False
        if legacy_def is None:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_def, definitions[0]['translation'])
            return False
        if definitions[0]['translation'].count("<br />") != 0:
            legacy_def = legacy_def.replace("\r\n", "<br />")
        if legacy_def != definitions[0]['translation']:
            if not LetterMapper().compare(legacy_def, definitions[0]['translation']):
                self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_def, definitions[0]['translation'])
                print(legacy_def)
                print(definitions[0]['translation'])
                print("text defs don't match")
                print(str(self.__class__) + str(self.id))
                return False

    def validate_uid(self, legacy_name, nuxeo_str, nuxeo_docs):
        if not legacy_name and not self.doc.get(nuxeo_str):
            return True
        if not self.doc.get(nuxeo_str):
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
        if not legacy_contributor and len(self.doc.get(nuxeo_str)) == 0:
            return True
        if len(self.doc.get(nuxeo_str)) == 0:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_contributor, self.doc.get(nuxeo_str))
            return False
        sources = []
        for source in self.doc.get(nuxeo_str):
            for c in self.dialect.nuxeo_contributors:
                if c.uid == source:
                    sources.append(c.title.strip())
                    break
        if not legacy_contributor:
            self.dialect.flags.dataMismatch(self, nuxeo_str, legacy_contributor, sources)
            return False
        match = "(^[^(https:\/\/)|(www.)].*)((?<!\d)([,/](?!( S[rR])|( Elder)|(.$)))|(?:(( and )|( & ))(?!(Cultur)|(historian)|(mentor)|(Hand)|(Media)|(Elder)|(dictionary)|(Wildlife))))"
        contributors = re.split(match, legacy_contributor, re.IGNORECASE)
        contributors = [con for con in contributors if con not in [",", "/", "", " and ", " & "] and con is not None]
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
        if not self.change:
            self.validate_text(self.change, "fvl:change_date")
            return
        # match = re.search("^(\d\d)-(\w{3})-\d{2}(\d{2}).*", str(self.change))
        # if match:
        #     date = str(match.group(3))+"-"+str(list(calendar.month_abbr).index(match.group(2)))+"-"+str(match.group(1))
        #     print("hand made date !!!")
        #     print(match.groups())
        #     print(date)
        #     self.validate_text(date, "fvl:change_date")
        # else:
        self.validate_text(str(self.change)[2:10], "fvl:change_date")

    def quality_check(self):
        # if not self.title:
        #     self.dialect.flags.missingData(self, "dc:title")
        pass

    def exists(self, path):
        connect = requests.head(path)
        return connect.status_code in [200, 302]

    def html_strip(self, html_string):
        return re.sub('<[^<]+?>', '', html_string)
