# note_creator.py
from typing import List, Optional
from anki.notes import Note
from aqt import mw
from aqt.utils import showInfo
from .logger import log_error, log_info


class NoteCreator:
    def __init__(self, model_name: str, deck_name: str, allow_duplicates: bool,
                 import_tags: bool, adjust_ease: bool, tags: List[str]):
        """ Initialization of passed values used for card creation """
        self.model_name = model_name
        self.deck_name = deck_name
        self.allow_duplicates = allow_duplicates
        self.import_tags = import_tags
        self.adjust_ease = adjust_ease
        self.tags = tags

    def create_cards(self, terms: List, selected_lang: str) -> int:
        """ Adds Anki cards from LUTE terms into deck with specified settings """
        log_info(f'[note_creator] Starting to create notes in deck: {self.deck_name}')
        try:
            # sets in which deck the cards should be created and initializes counter (created cards)
            deck_id = mw.col.decks.id_for_name(self.deck_name)
            counter = 0

            # checks if term should be allowed to be created and whether its ease should be adjusted
            for term in terms:
                if not self.should_process_term(term, selected_lang):
                    continue

                note = self.create_note(term, self.adjust_ease)
                if not note:
                    continue

                if self.can_add_note(term[0]):
                    counter = self.add_note_to_deck(note, term, deck_id, counter)

            log_info(f'[note_creator] Total {counter} cards added to deck {self.deck_name}')
            return counter

        except Exception as e:
            log_error(f'[note_creator] Error creating cards: {str(e)}')
            showInfo(f'Error creating cards: {str(e)}')
            return 0

    def should_process_term(self, term, selected_lang: str) -> bool:
        """ Returns true for terms meeting all set conditions that should be turned into notes """
        # term[2] is WoLgID (filter for selected language) - rest of filters moved to database.py
        return term[2] == selected_lang

    def create_note(self, term, adjust_ease: bool) -> Optional[Note]:
        """ Handles creation of notes from Lute terms """
        try:
            note = Note(model=mw.col.models.by_name(self.model_name), col=mw.col)
            zws = '\u200B'
            # term[0] is WoText and term[1] is WoTranslation (both) from table words
            # zws = '\u200B' is zero width space used for multi-word terms in Lute, removed for Anki
            note.fields[0] = term[0].replace(zws, '')
            note.fields[1] = term[1].replace(zws, '').replace('\r\n', '<br>')

            if adjust_ease:
                """ Assigning ease based on LUTE status using default 250% for Status=3, """
                """ increasing/decreasing the ease by 15% for each lower/higher level, """
                """ capping it at 300% for Well-Known, Ignored (term[8] is LUTE status) """
                note.ease = min(2500 + (term[8] - 3) * 150, 3000)

            return note
        except Exception as e:
            log_error(f'[note_creator] Error creating {term} note: {e}')
            return None

    def can_add_note(self, term_front: str) -> bool:
        # Checks whether identical note or note for the same term already exist
        existing_notes = mw.col.find_notes(f'Front:"{term_front}"')
        return not existing_notes or self.allow_duplicates

    def add_note_to_deck(self, note: Note, term, deck_id: int,
                         counter: int) -> int:
        # Adds tags to note and then adds it into deck
        try:
            tags = self.get_tags(term)
            if tags:
                note.tags = tags
            mw.col.add_note(note, deck_id)
            log_info(f'[note_creator] Note created for term: {term[0]}')
            return counter + 1
        except Exception as e:
            log_error(f'[note_creator] Error creating note for term {term[0]}: {str(e)}')
            return counter

    def get_tags(self, term) -> List[str]:
        # Copies tags from Lute and adds tags specified in GUI
        tags = self.tags.copy()
        if term[4] and self.import_tags:
            tags.append(term[4])
        return tags
