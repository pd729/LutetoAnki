import sqlite3
from typing import List, Tuple
from aqt.utils import showInfo

class LuteDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def connect(self) -> Tuple[List, List]:
        """Connect to LUTE database and retrieve terms and languages"""
        if not self.db_path.endswith('lute.db'):
            showInfo("Please select a lute.db file")
            return [], []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get terms
            cursor.execute('''
                SELECT WoText, WoTranslation, WoLgID, WoCreated, TgText, 
                       WoStatusChanged, WoTextLC, WoID, WoStatus, WoRomanization, 
                       WoTokenCount, WiSource, TgComment
                FROM words AS w 
                LEFT JOIN wordimages AS wi ON w.WoID=wi.WiWoID 
                LEFT JOIN wordtags AS wt ON wi.WiWoID=wt.WtWoID 
                LEFT JOIN tags AS t ON wt.WtTgID=t.TgID
                WHERE WoTranslation <> "" AND WoTranslation IS NOT NULL
            ''')
            terms = cursor.fetchall()
            
            # Get languages
            used_lg_ids = list(set(term[2] for term in terms))
            cursor.execute('SELECT * FROM languages')
            all_languages = cursor.fetchall()
            languages = [[lang[0], lang[1]] for lang in all_languages 
                        if lang[0] in used_lg_ids]
            
            conn.close()
            return terms, languages
            
        except Exception as e:
            showInfo(f'Database connection error: {str(e)}')
            return [], []