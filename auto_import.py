# auto_import.py
from aqt.utils import showInfo
from datetime import date, timedelta
from .database import LuteDatabase
from .note_creator import NoteCreator
from .logger import log_info, log_error

class AutoImporter:
    def __init__(self, config):
        self.config = config

    def run_import(self):
        try:
            db_path = self.config.get_config_param('lutedb_path')
            if db_path == 'Open file manager':
                log_error('[auto_import] Auto-import failed: LUTE database path is not set.')
                return

            log_info('[auto_import] Starting auto-import from LUTE database.')
            db = LuteDatabase(db_path)
            terms, languages = db.connect(
                self.config.get_config_param('parents_only'),
                self.config.get_config_param('empty_translation'),
                self.config.get_config_param('include_WKI'),
                date.today() - timedelta(days=self.config.get_config_param('last_days'))
            )

            if terms:
                # Adding new terms to Anki based on config.json settings
                selected_lang = self.config.get_config_param('selected_lang')
                selected_deck = self.config.get_config_param('selected_deck')
                creator = NoteCreator(
                    model_name=self.config.get_config_param('selected_model'),
                    deck_name=self.config.get_config_param('selected_deck'),
                    allow_duplicates=self.config.get_config_param('allow_duplicates'),
                    import_tags=self.config.get_config_param('import_tags'),
                    adjust_ease=self.config.get_config_param('adjust_ease'),
                    tags=self.config.get_config_param('tags')
                )
                cards_added = creator.create_cards(terms, selected_lang)
                log_info(f'[auto import] Total {cards_added} cards successfully added to deck {selected_deck}\n(ignored {len(terms)-cards_added} duplicates)')
                showInfo(f'Total {cards_added} cards successfully added to deck {selected_deck}\n(ignored {len(terms)-cards_added} duplicates)')
            else:
                log_info('[auto_import] Auto-import completed: No new terms found.')
        except Exception as e:
            log_error(f'[auto_import] Auto-import failed: {str(e)}')
            showInfo(f'Error when running auto_import {e}')
