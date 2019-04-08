# coding= utf-8
import os
from src.Portal import Portal
from src.Updater import Updater
from src.authorization import Authorize
from src.Dialect import Dialect
from src.NuxeoData import Data
from nuxeo.client import Nuxeo


class LegacyValidator:

    def __init__(self):
        self.nuxeo = Authorize.nuxeo
        self.cur = Authorize.cursor
        self.data = Data()

        # dialects = self.validate_dialects_test()
        # missing = [145, 401, 403, 185, 406]
        # for dialect in dialects:
        #     if dialect.id not in missing:
        #         dialect.get_attributes()
        #         dialect.validate()
        #         print(dialect.id)
        #     else:
        #         print("missing: "+str(dialect.id))

    def get_dialects_all(self):  # collects all dialects, then processes, longer to start but quicker to process?
        dialects = []
        entries = self.cur.execute("SELECT ID, NAME, ADMIN_EMAIL_ADDRESS, ADMIN_FIRST_NAME, ADMIN_LAST_NAME, "  # 0-4
                             "ADMIN_PHONE_NUMBER, CHANGE_DTTM, CONTACT_INFORMATION"  # 5-7      maybe just get rid of char grid text one, only 306 uses it, unsure where it maps to
                             ", CONTACT_INFORMATION2, CONTACT_INFORMATION3, CONTACT_INFORMATION4, COUNTRY_ID, DESCR, "  # 8-12
                             "DESCR2, DESCR3, DESCR4, DOMINANT_LANGUAGE, DOMINANT_LANGUAGE_FR, FIRST_WORD_ONE_ID, "  # 13-18
                             "FIRST_WORD_TWO_ID, FIRST_WORD_THREE_ID, FIRST_WORD_FOUR_ID, FIRST_WORD_FIVE_ID, "  # 19-22
                             "GRAMMAR_RULES_NAME, GRAMMAR_RULES_DESCRIPTION, GRAMMAR_RULES_CONTRIBUTER, "  # 23-25
                             "GRAMMAR_RULES_MEDIA_FILENAME, GRAMMAR_RULES_RECORDER, GRAMMAR_RULES_STATUS_ID, "  # 26-28
                             "IMAGE_MEDIA_FILENAME, IMAGE_DESCRIPTION, IMAGE_RECORDER, IMAGE_CONTRIBUTER, "  # 29-32
                             "IMAGE_STATUS_ID, LANG_GRP_ID, LANGUAGE_FAMILY_ID, PORTAL_ABOUT_MORE, PORTAL_ABOUT_MORE_2,"  # 33-37
                             " PORTAL_ABOUT_TEXT, PORTAL_ART_GALLERY_STATUS_ID, PORTAL_PHOTO_ALBUMN_STATUS_ID, "  # 38-40
                             "PORTAL_GREETING, PORTAL_COLUMN_TITLE, PORTAL_COLUMN_TEXT, PORTAL_PEOPLE_NAME, "  # 41-44
                             "PORTAL_RELATED_LINKS, PORTAL_STATUS_ID, PORTAL_THEME_ID, PRONUNCIATION_GUIDE_FILENAME, "  # 45-48
                             "PRONUNCIATION_NAME, PRONUNCIATION_GUIDE_DESCR, PRONUNCIATION_GUIDE_RECORDER, "  # 49-51
                             "PRONUNCIATION_GUIDE_CONTRIB, PRONUNCIATION_GUIDE_STATUS_ID, PUBLIC_ACCESS, REGION, "  # 52-55
                             "SHOW_ALPHABET_LIST, SHOW_KEYBOARD, SOUND_MEDIA_FILENAME, SOUND_DESCRIPTION, "  # 56-59
                             "SOUND_CONTRIBUTER, SOUND_RECORDER, SOUND_STATUS_ID, SPECIAL_CSS, STATUS_ID, "  # 60-64
                             "FRIENDLY_URL_SEGMENT FROM FIRSTVOX.DICTIONARY")

        for r in entries:
            admin_info = [r[2], r[3], r[4], r[5]]
            contact_info = [r[7], r[8], r[9], r[10]]
            descriptions = [r[12], r[13], r[14], r[15]]
            first_words = [r[18], r[19], r[20], r[21], r[22]]
            grammar_rules = [r[23], r[24], r[25], r[26], r[27], r[28]]
            image = [r[29], r[30], r[31], r[32], r[33]]
            portal_info = [r[36], r[37], r[38], r[41], r[42], r[43], r[44], r[45], r[46], r[47]]
            pronunciation = [r[48], r[49], r[50], r[51], r[52], r[53]]
            sound = [r[58], r[59], r[60], r[61], r[62]]
            dialect = Dialect(r[0], r[1], admin_info, contact_info, descriptions, r[11], r[16], r[17], r[54], r[55], r[64], r[65], grammar_rules, pronunciation, r[39], r[40], r[34], r[35], r[6], self.data)
            dialects.append(dialect)
            portal = Portal(dialect, portal_info, first_words, image, sound, r[56], r[57])
            dialect.portal = portal
        return dialects

    def validate_dialects(self):
        dialects = []
        entries = self.cur.execute("SELECT ID FROM FIRSTVOX.DICTIONARY ORDER BY ID DESC")
        validated = False
        for r in entries:
            dialects.append(r[0])
        for dialect_id in dialects:
            while not validated:
                try:
                    self.dialect(dialect_id)
                    print()
                    break
                except ConnectionError as connect:
                    print("CONNECTION RETRY")
                    print(connect)
                    self.nuxeo = Nuxeo(host=Authorize.nuxeoUrl, auth=(Authorize.nuxeoUser, Authorize.nuxeoPassword))

    def dialect(self, dialect_id):
        dialect = ""
        entries = self.cur.execute("SELECT ID, NAME, ADMIN_EMAIL_ADDRESS, ADMIN_FIRST_NAME, ADMIN_LAST_NAME, "  # 0-4
                                   "ADMIN_PHONE_NUMBER, CHANGE_DTTM, CONTACT_INFORMATION"  # 5-7  char grid text one, only 306 uses it, doesn't maps to anything
                                   ", CONTACT_INFORMATION2, CONTACT_INFORMATION3, CONTACT_INFORMATION4, COUNTRY_ID, DESCR, "  # 8-12
                                   "DESCR2, DESCR3, DESCR4, DOMINANT_LANGUAGE, DOMINANT_LANGUAGE_FR, FIRST_WORD_ONE_ID, "  # 13-18
                                   "FIRST_WORD_TWO_ID, FIRST_WORD_THREE_ID, FIRST_WORD_FOUR_ID, FIRST_WORD_FIVE_ID, "  # 19-22
                                   "GRAMMAR_RULES_NAME, GRAMMAR_RULES_DESCRIPTION, GRAMMAR_RULES_CONTRIBUTER, "  # 23-25
                                   "GRAMMAR_RULES_MEDIA_FILENAME, GRAMMAR_RULES_RECORDER, GRAMMAR_RULES_STATUS_ID, "  # 26-28
                                   "IMAGE_MEDIA_FILENAME, IMAGE_DESCRIPTION, IMAGE_RECORDER, IMAGE_CONTRIBUTER, "  # 29-32
                                   "IMAGE_STATUS_ID, LANG_GRP_ID, LANGUAGE_FAMILY_ID, PORTAL_ABOUT_MORE, PORTAL_ABOUT_MORE_2,"  # 33-37
                                   " PORTAL_ABOUT_TEXT, PORTAL_ART_GALLERY_STATUS_ID, PORTAL_PHOTO_ALBUMN_STATUS_ID, "  # 38-40
                                   "PORTAL_GREETING, PORTAL_COLUMN_TITLE, PORTAL_COLUMN_TEXT, PORTAL_PEOPLE_NAME, "  # 41-44
                                   "PORTAL_RELATED_LINKS, PORTAL_STATUS_ID, PORTAL_THEME_ID, PRONUNCIATION_GUIDE_FILENAME, "  # 45-48
                                   "PRONUNCIATION_NAME, PRONUNCIATION_GUIDE_DESCR, PRONUNCIATION_GUIDE_RECORDER, "  # 49-51
                                   "PRONUNCIATION_GUIDE_CONTRIB, PRONUNCIATION_GUIDE_STATUS_ID, PUBLIC_ACCESS, REGION, "  # 52-55
                                   "SHOW_ALPHABET_LIST, SHOW_KEYBOARD, SOUND_MEDIA_FILENAME, SOUND_DESCRIPTION, "  # 56-59
                                   "SOUND_CONTRIBUTER, SOUND_RECORDER, SOUND_STATUS_ID, SPECIAL_CSS, STATUS_ID, "  # 60-64
                                   "FRIENDLY_URL_SEGMENT FROM FIRSTVOX.DICTIONARY WHERE ID = "+str(dialect_id)+"")

        for r in entries:
            admin_info = [r[2], r[3], r[4], r[5]]
            contact_info = [r[7], r[8], r[9], r[10]]
            descriptions = [r[12], r[13], r[14], r[15]]
            first_words = [r[18], r[19], r[20], r[21], r[22]]
            grammar_rules = [r[23], r[24], r[25], r[26], r[27], r[28]]
            image = [r[29], r[30], r[31], r[32], r[33]]
            portal_info = [r[36], r[37], r[38], r[41], r[42], r[43], r[44], r[45], r[46], r[47]]
            pronunciation = [r[48], r[49], r[50], r[51], r[52], r[53]]
            sound = [r[58], r[59], r[60], r[61], r[62]]
            dialect = Dialect(r[0], r[1], admin_info, contact_info, descriptions, r[11], r[16], r[17], r[54], r[55], r[64], r[65], grammar_rules, pronunciation, r[39], r[40], r[34], r[35], r[6], self.data)
            portal = Portal(dialect, portal_info, first_words, image, sound, r[56], r[57])
            dialect.portal = portal
            missing = [145, 401, 403, 185, 406]  #  these don't exist in nuxeo
            if dialect.id not in missing:
                dialect.get_attributes()
                dialect.validate()
                dialect.report()
                # dialect.update_dialect()
                print(str(dialect.id)+" "+dialect.title+" is complete")
                # cont = input("Enter a string to continue"):
            else:
                print(str(dialect.id)+" "+dialect.title+" is MISSING")
        return dialect

    def upload_reports(self, path):  # uploads any already created reports, not ones with errors for us to fix
        entries = self.cur.execute("SELECT ID, NAME FROM FIRSTVOX.DICTIONARY")
        for r in entries:
            if self.data.nuxeo_dialects.get(r[0]):
                self._upload(r[1], path, self.data.nuxeo_dialects.get(r[0]).path)
            else:
                print(str(r[0])+" "+str(r[1]))

    def _upload(self, title, file_path, nuxeo_path):  # file_path = path to directory where reports are, nuxeo_path = parent path to put links
        title = title.replace(" ", "").replace("/", "")
        if os.path.isfile(file_path+'\\'+title+'.csv'):
            Updater().create_doc(nuxeo_path+"/Links", title+'.csv', "FVLink", {'dc:title': title}, file_path+'\\'+title+'.csv')
        if os.path.isfile(file_path+'\\'+title+'Errors.csv'):
            Updater().create_doc(nuxeo_path+"/Links", title+"Errors.csv", "FVLink", {'dc:title': title}, file_path+title+'\\'+'Errors.csv')


lv = LegacyValidator()
# lv.upload_reports(os.getcwd())
lv.validate_dialects()



