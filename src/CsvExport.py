import unicodecsv as csv
from src.authorization import Authorize


class Exporter:

    def __init__(self):
        self.legacy = Authorize.cursor
        self.categories = {}
        self.pos = {}

        rows = self.legacy.execute("select ID, CODE from FIRSTVOX.WORD_CATEGORY")
        for r in rows:
            self.categories[r[0]] = r[1].strip("-")

        rows = self.legacy.execute("select ID, CODE from FIRSTVOX.PART_OF_SPEECH")
        for r in rows:
            self.pos[r[0]] = r[1].lower().capitalize()

    def export(self, dialect, title, headers, table, where=None):
        print(title)

        rows = self.legacy.execute("select "+headers+" from "+table+" where DICTIONARY_ID = '"+str(dialect)+"' "+(where or ""))

        with open(title, mode='wb') as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow(headers.split(","))
            if table == "FIRSTVOX.WORD_ENTRY":
                self.write_words(csvWriter, rows)
                return
            if table == "FIRSTVOX.ORTHOGRAPHY":
                self.write_file(csvWriter, rows, 5)
                return
            if table == "FIRSTVOX.PHRASE_CATEGORY":
                self.write_file(csvWriter, rows, 2)
                return
            to_csv = []
            for row in rows:
                to_csv.append(row)

            csvWriter.writerows(to_csv)

    def write_words(self, csvWriter, rows):
        for row in rows:
            row = list(row)
            row[3] = self.pos.get(row[3])
            row[4] = self.categories.get(row[4])
            csvWriter.writerow(row)

    def write_file(self, csvWriter, rows, index):
        for row in rows:
            row = list(row)
            if row[index]:
                if row[index].count('/'):
                    row[index] = row[index][row[index].rindex('/')+1:]
                else:
                    row[index] = row[index][row[index].rindex('\\')+1:]
            csvWriter.writerow(row)

    def main(self):
        tables = {"Words": ["ID, WORD_VALUE, DOMINANT_LANGUAGE_WORD_VALUE, PART_OF_SPEECH_ID, CATEGORY_ID, "
                            "ABORIGINAL_LANGUAGE_SENTENCE, DOMINANT_LANGUAGE_SENTENCE, CONTRIBUTER, CULTURAL_NOTE, "
                            "PHONETIC_INFO, REFERENCE, " # IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID,
                            "DOMINANT_LANGUAGE_DEFINITION", "FIRSTVOX.WORD_ENTRY", None],
                  "Phrases": ["ID, PHRASE, DOMINANT_LANGUAGE_PHRASE, CATEGORY_ID, CONTRIBUTER, CULTURAL_NOTE, REFERENCE"
                              , "FIRSTVOX.PHRASE_ENTRY", None],  # " IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID"
                  # "Media": ["ID, FILENAME, DESCR, CONTRIBUTER, RECORDER, MEDIA_TYPE_ID, IS_SHARED", "FIRSTVOX.ENTRY_MEDIA", None],
                  # "": ["ID, NAME, ADMIN_EMAIL_ADDRESS, ADMIN_FIRST_NAME, ADMIN_LAST_NAME, "
                  #      "ADMIN_PHONE_NUMBER, CONTACT_INFORMATION"
                  #      ", CONTACT_INFORMATION2, CONTACT_INFORMATION3, CONTACT_INFORMATION4, COUNTRY_ID, DESCR, "
                  #      "DESCR2, DESCR3, DESCR4, DOMINANT_LANGUAGE, DOMINANT_LANGUAGE_FR, FIRST_WORD_ONE_ID, "
                  #      "FIRST_WORD_TWO_ID, FIRST_WORD_THREE_ID, FIRST_WORD_FOUR_ID, FIRST_WORD_FIVE_ID, "
                  #      "GRAMMAR_RULES_NAME, GRAMMAR_RULES_DESCRIPTION, GRAMMAR_RULES_CONTRIBUTER, "
                  #      "GRAMMAR_RULES_MEDIA_FILENAME, GRAMMAR_RULES_RECORDER, IMAGE_MEDIA_FILENAME, IMAGE_DESCRIPTION, "
                  #      "IMAGE_RECORDER, IMAGE_CONTRIBUTER, LANG_GRP_ID, LANGUAGE_FAMILY_ID, PORTAL_ABOUT_MORE, "
                  #      "PORTAL_ABOUT_MORE_2, PORTAL_ABOUT_TEXT, PORTAL_GREETING, PORTAL_COLUMN_TITLE, PORTAL_COLUMN_TEXT, "
                  #      "PORTAL_PEOPLE_NAME, PORTAL_RELATED_LINKS, PRONUNCIATION_GUIDE_FILENAME, PRONUNCIATION_NAME, "
                  #      "PRONUNCIATION_GUIDE_DESCR, PRONUNCIATION_GUIDE_RECORDER, PRONUNCIATION_GUIDE_CONTRIB, "
                  #      "PUBLIC_ACCESS, REGION, SOUND_MEDIA_FILENAME, SOUND_DESCRIPTION, SOUND_CONTRIBUTER, "
                  #      "SOUND_RECORDER, FRIENDLY_URL_SEGMENT", "FIRSTVOX.DICTIONARY", None],
                  "Alphabet": ["ID, CHAR_DATA, UPPER_CASE_CHAR_DATA, ALPH_ORDER, SAMPLE_WORD, SOUND_MEDIA_FILENAME, "
                               "SOUND_DESCRIPTION, SOUND_CONTRIBUTER, SOUND_RECORDER", "FIRSTVOX.ORTHOGRAPHY", "order by ALPH_ORDER"],
                  "PhraseBooks": ["ID, DESCR, IMAGE_FILENAME", "FIRSTVOX.PHRASE_CATEGORY", None],
                  "Songs": ["ID, ABORIGINAL_LANGUAGE_TITLE, DOMINANT_LANGUAGE_TITLE, CONTRIBUTER, CULTURAL_NOTE, "
                            "ABORIGINAL_LANGUAGE_INTRO, "  # IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID, 
                            "DOMINANT_LANGUAGE_INTRO, AUTHOR, AUTHOR_REFERENCE, CONTRIBUTER_REFERENCE, "
                            "DOMINANT_LANGUAGE_TRANSLATION","FIRSTVOX.SENTRY_BOOK", "and SSTYPE_ID = 1"],
                  "Stories": ["ID, ABORIGINAL_LANGUAGE_TITLE, DOMINANT_LANGUAGE_TITLE, CONTRIBUTER, "
                              "CULTURAL_NOTE, "  # IMAGE_ENTRY_ID, SOUND_ENTRY_ID, VIDEO_ENTRY_ID, 
                              "ABORIGINAL_LANGUAGE_INTRO, DOMINANT_LANGUAGE_INTRO, AUTHOR, AUTHOR_REFERENCE, "
                              "CONTRIBUTER_REFERENCE, DOMINANT_LANGUAGE_TRANSLATION","FIRSTVOX.SENTRY_BOOK", "and SSTYPE_ID = 2"]}
          ### book entries, private categories
        dialects = {}
        entries = self.legacy.execute("SELECT ID, NAME FROM FIRSTVOX.DICTIONARY")

        for r in entries:
            dialects[r[0]] = r[1].replace(" ", "").replace("/", "")

        for dialect in dialects:
            for type in tables:
                self.export(dialect, dialects.get(dialect)+type+".csv" ,tables.get(type)[0], tables.get(type)[1], tables.get(type)[2])

Exporter().main()

