# __init__.py
from aqt import mw
from aqt.qt import *
from .config import Config
from .gui import ImporterGui
from .logger import log_info

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
            'adjust_ease': False,
            'include_WKI': False
            }
    current_config = config.get_config()
    
    # Update with any missing default values
    missing_keys = {k: v for k, v in default_config.items() if k not in current_config}
    if missing_keys:
        config.update_config(missing_keys)
        log_info(f'Configuration initialized with default values for {missing_keys}')


def show_importer():
    # Displaying the addon GUI
    config = Config()
    mw.myWidget = ImporterGui(config)
    log_info('Importer GUI launched.')
    mw.myWidget.widget.show()

# Initialize config when addon loads
initialize_config()

# Create menu item
action = QAction('LUTE to Anki importer', mw)
qconnect(action.triggered, show_importer)
mw.form.menuTools.addAction(action)