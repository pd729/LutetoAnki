# __init__.py
from aqt import mw
from aqt.qt import *
from aqt.gui_hooks import collection_did_load
from .config import Config
from .gui import ImporterGui
from .logger import log_info
from .auto_import import AutoImporter

def initialize_config():
    """ Ensure config file exists with all necessary keys """
    config = Config()
    default_config = {
            'lutedb_path': 'Open file manager',
            'parents_only': False,
            'empty_translation': False,
            'allow_duplicates': False,
            'import_tags': False,
            'selected_deck': 'Default',
            'selected_model': 'Basic',
            'adjust_ease': False,
            'include_WKI': False,
            'selected_lang': 0,
            'last_days': 0,
            'tags': [],
            'auto_import': False
            }
    current_config = config.get_config()
    
    # Update with any missing default values
    missing_keys = {k: v for k, v in default_config.items() if k not in current_config}
    if missing_keys:
        config.update_config(missing_keys)
        log_info(f'[init] Configuration initialized with default values for {missing_keys}')

def auto_import_on_startup():
    """Safely run automatic import only once after collection is loaded."""
    if mw.col is None:
        log_info('[init] Anki collection not loaded. Auto-import skipped.')
        return

    config = Config()
    if config.get_config_param('auto_import_on_startup'):
        importer = AutoImporter(config)
        importer.run_import()
        log_info('[init] Auto-import on startup executed.')

def show_importer():
    """Display the importer GUI."""
    config = Config()
    mw.myWidget = ImporterGui(config)
    log_info('[init] Importer GUI launched.')

    # Refresh Anki after closing the GUI
    def on_close(event):
        mw.reset()
        event.accept()

    mw.myWidget.widget.closeEvent = on_close
    mw.myWidget.widget.show()

def on_collection_loaded(_):
    """Initialize config and trigger auto-import safely after collection load."""
    initialize_config()

    # Add menu item to Tools
    action = QAction('LUTE to Anki importer', mw)
    qconnect(action.triggered, show_importer)
    mw.form.menuTools.addAction(action)

    # Run the auto-import exactly once after collection is ready
    auto_import_on_startup()

# Hook to run after Anki's collection is fully loaded
collection_did_load.append(on_collection_loaded)