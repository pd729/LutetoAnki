import sqlite3
import json
from pathlib import Path
from typing import Optional, List
from anki.notes import Note
from datetime import date, timedelta
# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

###########################################
# Declaring, laoding and saving variables #
###########################################
def get_saved_path() -> str:
    """ loading saved path if it exists """
    try:
        # Get addon folder name (the number)
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        addon_id = os.path.basename(addon_dir)
        conf = mw.addonManager.getConfig(addon_id)
    except Exception as e:
            print(f'Debug - Loading .db path failed: {str(e)}')
    return conf.get('lutedb_path','Open file manager')  # Returns default if empty

""" global variables """
lutedb_path = get_saved_path()
sel_model = ''
sel_lang = ''
sel_deck = 'Default'
terms = []
tags = []
languages = []
checked_duplicates = False
checked_tags = True
last_days = 0

def save_path_to_config(path: str) -> bool:
    """ saving path for future """
    try:
        """ Get addon folder name (the number) """
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        addon_id = os.path.basename(addon_dir)
        
        """ Prepare new config """
        current_config = mw.addonManager.getConfig(addon_id)
        if current_config is None:
            current_config = {}
        
        """ Update the path """
        current_config['lutedb_path'] = path
        
        """ Try direct file writing as a fallback """
        config_path = os.path.join(addon_dir, 'config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=4)
            print(f'Debug - Wrote config directly to file: {config_path}')
        except Exception as e:
            print(f'Debug - Direct file write failed: {str(e)}')
        
        """ Verify the save """
        new_config = mw.addonManager.getConfig(addon_id)
        print(f"Debug - New config after save: {new_config}")
        
        return new_config and new_config.get('lutedb_path') == path
        
    except Exception as e:
        print(f'Debug - Main function error: {str(e)}')
        return False

#####################
# Create Anki cards #
#####################
def create_anki_cards() -> None:
    """Creates Anki cards from LUTE terms in the selected deck."""
    try:
        deck_id = mw.col.decks.id_for_name(sel_deck)
        counter = 0
        cutoff_date = str(date.today() - timedelta(days=last_days))
        
        for term in terms:
            if not _should_process_term(term, sel_lang, cutoff_date):
                continue
                
            note = _create_note(term)
            if not note:
                continue
                
            if _can_add_note(term[0], checked_duplicates):
                counter = _add_note_to_deck(note, term, deck_id, counter)
        
        showInfo(f'{counter} cards added to deck {sel_deck}')
        
    except Exception as e:
        showInfo(f'Error creating cards: {str(e)}')

def _should_process_term(term, selected_lang, cutoff_date) -> bool:
    """Determines if a term should be processed based on language and date."""
    return term[2] == selected_lang and cutoff_date < term[3]

def _create_note(term) -> Optional[Note]:
    """Creates an Anki note from a term, handling field assignment."""
    try:
        note = Note(model=mw.col.models.by_name(sel_model), col=mw.col)
        zws = '\u200B'
        note.fields[0] = term[0].replace(zws, '')
        note.fields[1] = term[1].replace(zws, '')
        return note
    except Exception as e:
        print(f'Error creating note: {e}')
        return None

def _can_add_note(term_front, allow_duplicates) -> bool:
    """Checks if a note can be added based on duplication rules."""
    existing_notes = mw.col.find_notes(f'Front:"{term_front}"')
    return not existing_notes or allow_duplicates

def _add_note_to_deck(note, term, deck_id, counter) -> int:
    """Adds a note to the deck with proper tagging."""
    try:
        tags = _get_tags(term)
        note.tags = [tags]
        mw.col.add_note(note, deck_id)
        return counter + 1
    except Exception as e:
        print(f'Error adding note to deck: {e}')
        return counter

def _get_tags(term) -> str:
    """Generates tag string based on term and global settings."""
    base_tags = ' '.join(tags)
    if term[4] and checked_tags:
        return ' '.join([base_tags, term[4]])
    return base_tags

################
# Creating GUI #
################
def GUIFunction() -> None:
    """ GUI menu function """
    mw.myWidget = widget = QWidget()
    widget.setWindowTitle('LUTE to Anki importer')
    col = mw.col

    def connect_to_lutedb() -> None:
        """ Connect to the SQLite database """
        if (lutedb_path.endswith('lute.db')):
            conn = sqlite3.connect(lutedb_path)
            cursor = conn.cursor()
            
            """ save path for the future """
            save_path_to_config(lutedb_path)

            """ as much information as I managed to put together, filtering out terms without translation (not everything used now) """
            cursor.execute('SELECT WoText, WoTranslation, WoLgID, WoCreated, TgText, WoStatusChanged, WoTextLC, WoID, WoStatus, WoRomanization, WoTokenCount, WiSource, TgComment \
                                        FROM words AS w LEFT JOIN wordimages AS wi ON w.WoID=wi.WiWoID LEFT JOIN wordtags AS wt ON wi.WiWoID=wt.WtWoID LEFT JOIN tags AS t ON wt.WtTgID=t.TgID   \
                                        WHERE WoTranslation <> '' AND WoTranslation IS NOT NULL')
            rows = cursor.fetchall()
            used_Lg_IDs = list(set([item[2] for item in rows])) # find unique LgIDs in the data loaded from lute.db
            global terms
            for item in rows:
                terms.append(item)

            """ load languages """
            cursor.execute('SELECT * FROM languages')
            langs = cursor.fetchall()
            global languages
            for item in langs:
                if (item[0] in used_Lg_IDs):
                    languages.append([item[0], item[1]]) # 0 lgID, 1 lgName
                    language_options.addItem(item[1]) # add the options to the widget

            showInfo(f'Connected and loaded {len(terms)} terms')
            connect_button.setText("Connected")
            connect_button.setEnabled(False)
        else: showInfo("Please select a lute.db file")

    def update_variables():
        """ update values of global variables when user selects different values """
        global sel_lang, sel_model, sel_deck, last_days, tags
        if (len(language_options.currentText())>0):
            sel_lang = languages[language_options.currentIndex()][0]

        """ checking that selected model's name exists (pointless?) """
        for model in mw.col.models.all():
            if model['name'] == model_options.currentText():
                sel_model = model['name']
                break
        sel_deck = deck_options.currentText()
        last_days = time_box.value()
        tags = tag_input_box.text().split(" ")

    def update_checks():
        """ keep track of (un)checked checkboxes """
        global checked_duplicates, checked_tags
        checked_duplicates = duplicate_check_box.isChecked()
        checked_tags = import_tags_check_box.isChecked()
        
    def find_file() -> None:
        """ open file browser to select the lute.db file and save path to it """
        f = QFileDialog()
        global lutedb_path
        lutedb_path = f.getOpenFileName()[0]
        path_button.setText(lutedb_path)

    """ create layout """
    import_layout = QFormLayout(widget)

    """ create options to choose model """
    model_options = QComboBox(widget)
    for model in col.models.all():
        modelName = model['name']
        model_options.addItem(modelName)
    model_options.currentIndexChanged.connect(update_variables)

    """ Create options to choose language """
    language_options = QComboBox(widget)
    language_options.currentIndexChanged.connect(update_variables)

    """ create button to select path to lute.db """
    path_button = QPushButton(widget)
    saved_path = get_saved_path()
    if saved_path:
        lutedb_path = saved_path
    path_button.setText(lutedb_path)
    path_button.clicked.connect(find_file)

    """ create button to connect to lute.db """
    connect_button = QPushButton(widget)
    connect_button.setText('Click to connect')
    connect_button.clicked.connect(connect_to_lutedb)

    """ create button to filter time """
    time_box = QSpinBox(widget)
    time_box.setRange(0,365)
    time_box.valueChanged.connect(update_variables)

    """ create input field for tags """
    tag_input_box = QLineEdit(widget)
    tag_input_box.editingFinished.connect(update_variables)

    """ create options to choose deck """
    decks = mw.col.decks.all_names_and_ids()
    decks = [deck.name for deck in decks]
    deck_options = QComboBox(widget)
    for deck in decks:
        deck_options.addItem(deck)
    deck_options.currentIndexChanged.connect(update_variables)

    """ create settings options """
    duplicate_check_box = QCheckBox(widget)
    duplicate_check_box.setText('Allow duplicates')
    duplicate_check_box.stateChanged.connect(update_checks)

    import_tags_check_box = QCheckBox(widget)
    import_tags_check_box.setText('Import tags from LUTE')
    import_tags_check_box.setChecked(True)
    import_tags_check_box.stateChanged.connect(update_checks)

    """ create button to add new cards to Anki """
    import_button = QPushButton(widget)
    import_button.setText('Import to selected deck')
    import_button.clicked.connect(create_anki_cards)

    """ add all items to the layout and display it """
    import_layout.addRow('Select lute.db file to import:', path_button)
    import_layout.addRow('Connect to lute.db:', connect_button)
    import_layout.addRow('Card type:', model_options)
    import_layout.addRow('Language:', language_options)
    import_layout.addRow('Write tags to add to cards:', tag_input_box)
    import_layout.addRow('Time filter (x days before today):', time_box)
    import_layout.addRow('Select deck for import:', deck_options)
    import_layout.addRow(duplicate_check_box, import_tags_check_box)
    import_layout.addRow('Create new cards:', import_button)
    widget.setLayout(import_layout)
    widget.show()

""" create a new menu item, 'LUTE to Anki importer' """
action = QAction('LUTE to Anki importer', mw)
""" set it to call GUIFunction when it"s clicked """
qconnect(action.triggered, GUIFunction)
""" and add it to the Tools menu """
mw.form.menuTools.addAction(action)