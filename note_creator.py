from aqt import mw
from anki.notes import Note
from datetime import date, timedelta
from typing import Optional, List

class NoteCreator:
    def __init__(self, model_name: str, deck_name: str, allow_duplicates: bool,
                 import_tags: bool, adjust_ease: bool, include_WKI: bool, tags: List[str], days_filter: int):
        self.model_name = model_name
        self.deck_name = deck_name
        self.allow_duplicates = allow_duplicates
        self.import_tags = import_tags
        self.adjust_ease = adjust_ease
        self.include_WKI = include_WKI
        self.tags = tags
        self.days_filter = days_filter
        
    def create_cards(self, terms: List, selected_lang: str) -> int:
        """Creates Anki cards from LUTE terms"""
        try:
            deck_id = mw.col.decks.id_for_name(self.deck_name)
            counter = 0
            cutoff_date = str(date.today() - timedelta(days=self.days_filter))

            for term in terms:
                if not self._should_process_term(term, selected_lang, cutoff_date, self.include_WKI):
                    continue
                    
                note = self._create_note(term, self.adjust_ease)
                if not note:
                    continue
                    
                if self._can_add_note(term[0]):
                    counter = self._add_note_to_deck(note, term, deck_id, counter)
                    
            return counter
            
        except Exception as e:
            showInfo(f'Error creating cards: {str(e)}')
            return 0
            
    def _should_process_term(self, term, selected_lang: str, cutoff_date: str, include_WKI: bool) -> bool:
        if include_WKI:
            include_status = term[8] <= 5 or term[8] in [98, 99]
        else:
            include_status = term[8] <= 5
        return term[2] == selected_lang and cutoff_date < term[3] and include_status
        
    def _create_note(self, term, adjust_ease: bool) -> Optional[Note]:
        try:
            note = Note(model=mw.col.models.by_name(self.model_name), col=mw.col)
            zws = '\u200B'
            note.fields[0] = term[0].replace(zws, '')
            note.fields[1] = term[1].replace(zws, '')

            if adjust_ease == True:
                """ Assigning ease based on status in Lute giving default 250% to Status=3 and increasing/decreasing by 15% per level """
                """ capping it at 300% for Well known and Ignored (term[8] is status: 1,2,3,4,5,98,99) """
                note.ease = min(2500+(term[8]-3)*150, 3000)

            return note
        except Exception as e:
            print(f'Error creating note: {e}')
            return None
            
    def _can_add_note(self, term_front: str) -> bool:
        existing_notes = mw.col.find_notes(f'Front:"{term_front}"')
        return not existing_notes or self.allow_duplicates
        
    def _add_note_to_deck(self, note: Note, term, deck_id: int, 
        counter: int) -> int:
        try:
            tags = self._get_tags(term)
            note.tags = tags
            mw.col.add_note(note, deck_id)
            return counter + 1
        except Exception as e:
            print(f'Error adding note to deck: {e}')
            return counter
            
    def _get_tags(self, term) -> List[str]:
        tags = self.tags.copy()
        if term[4] and self.import_tags:
            tags.append(term[4])
        return tags