from aqt import mw
from aqt.qt import *
from .config import Config
from .gui import ImporterGui

def initialize_config():
    """Ensure config file exists with all necessary keys"""
    config = Config()
    default_config = {
            'lutedb_path': 'Open file manager',
            'parents_only': False,
            'empty_translation': False,
            'allow_duplicates': False,
            'import_tags': True,
            'selected_deck': "Default",
            'adjust_ease': False,
            'include_WKI': False
            }
    current_config = config.get_config()
    
    # Update with any missing default values
    if any(key not in current_config for key in default_config):
        config.update_config(default_config)

def show_importer():
    # Displaying the addon GUI
    config = Config()
    mw.myWidget = ImporterGui(config)
    mw.myWidget.widget.show()

# Initialize config when addon loads
initialize_config()

# Create menu item
action = QAction('LUTE to Anki importer', mw)
qconnect(action.triggered, show_importer)
mw.form.menuTools.addAction(action)