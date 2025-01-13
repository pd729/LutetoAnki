# auto_import.py
from datetime import date
from .database import LuteDatabase
from .note_creator import NoteCreator
from .logger import log_info, log_error

class AutoImporter:
    def __init__(self, config):
        self.config = config

    def run_import(self):
        try:
            # Check if auto-import is enabled in the config
            if not self.config.get_config_param('auto_import_on_startup'):
                log_info('[auto_import] Auto-import on startup is disabled.')
                return

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
                date.today()
            )

            if terms:
                # Adding new terms to Anki based on config.json settings
                creator = NoteCreator(
                    model_name=self.config.get_config_param('selected_model'),
                    deck_name=self.config.get_config_param('selected_deck'),
                    allow_duplicates=self.config.get_config_param('allow_duplicates'),
                    import_tags=self.config.get_config_param('import_tags'),
                    adjust_ease=self.config.get_config_param('adjust_ease'),
                    tags=[]
                )
                cards_added = creator.create_cards(terms, languages[0][0])
                log_info(f'[auto_import] Auto-import completed: {cards_added} cards added.')
            else:
                log_info('[auto_import] Auto-import completed: No new terms found.')
        except Exception as e:
            log_error(f'[auto_import] Auto-import failed: {str(e)}')