# gui.py
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo
from datetime import date, datetime, timedelta
from typing import List
from .config import Config
from .database import LuteDatabase
from .note_creator import NoteCreator
from .logger import log_info, log_warning, log_error
import os

class ImporterGui:
    def __init__(self, config: Config):
        self.config = config
        self.widget = QWidget()
        self.widget.setWindowTitle('Lute to Anki Importer')
        self.terms = []
        self.languages = []
        self.selected_model = ''
        self.selected_lang = ''
        self.selected_deck = 'Default'
        self.parents_only = False
        self.empty_translation = False
        self.adjust_ease = False
        self.include_WKI = False
        self.auto_import = False
        self.last_days = 0
        self.tags = []
        self.setup_gui()

    def setup_gui(self):
        self.create_widgets()
        self.create_layout()
        self.connect_signals()
        self.load_saved_settings()

    def create_widgets(self):
        """ Create all GUI widgets """
        self.path_button = QPushButton(self.widget)
        self.connect_button = QPushButton('Click to connect to lute.db', self.widget)
        self.import_button = QPushButton('Import to selected deck', self.widget)
        self.import_button.setEnabled(False)

        self.model_options = self.create_model_combobox()
        self.language_options = QComboBox(self.widget)
        self.deck_options = self.create_deck_combobox()

        self.time_box = QSpinBox(self.widget)
        self.time_box.setRange(0, 365)

        self.tag_input_box = QLineEdit(self.widget)

        self.parents_only_check_box = QCheckBox('Only parent terms', self.widget)
        self.empty_translation_check_box = QCheckBox('Allow blank translation', self.widget)
        self.duplicate_check_box = QCheckBox('Allow duplicates', self.widget)
        self.import_tags_check_box = QCheckBox('Import tags from LUTE', self.widget)
        self.adjust_ease_check_box = QCheckBox('Adjust ease based on Lute status', self.widget)
        self.include_WKI_check_box = QCheckBox('Include Well known, Ignored', self.widget)
        self.auto_import_check_box = QCheckBox('Enable Auto Import', self.widget)

        # Grouping together checkboxes for easier referencing and updating
        self.checkboxes = {
            'parents_only': self.parents_only_check_box,
            'empty_translation': self.empty_translation_check_box,
            'allow_duplicates': self.duplicate_check_box,
            'import_tags': self.import_tags_check_box,
            'adjust_ease': self.adjust_ease_check_box,
            'include_WKI': self.include_WKI_check_box,
            'auto_import': self.auto_import_check_box
        }

        self.db_group = QGroupBox("Database Connection")
    
    def populate_combobox(self, combo: QComboBox, items: List[str]):
        """ Helper to populate combo boxes with items """
        combo.clear()
        combo.addItems(items)

    def create_model_combobox(self):
        combo = QComboBox(self.widget)
        model_names = [model['name'] for model in mw.col.models.all()]
        self.populate_combobox(combo, model_names)
        if combo.count() > 0:
            saved_deck = self.config.get_config_param('selected_deck')
            if saved_deck in [combo.itemText(i) for i in range(combo.count())]:
                combo.setCurrentText(saved_deck)
        return combo

    def create_deck_combobox(self):
        combo = QComboBox(self.widget)
        deck_names = [deck.name for deck in mw.col.decks.all_names_and_ids()]
        self.populate_combobox(combo, deck_names)
        if combo.count() > 0:
            self.selected_deck = combo.itemText(0)
        return combo

    def create_layout(self):
        """ Creating layout with widgets defined in create_widgets """
        layout = QVBoxLayout(self.widget)

        db_layout = QFormLayout()
        db_layout.addRow('Select lute.db file to import:', self.path_button)
        db_layout.addRow(self.connect_button)
        self.db_group.setLayout(db_layout)

        options_group = QGroupBox("Import Options")
        options_layout = QFormLayout()
        options_layout.addRow(self.parents_only_check_box, self.empty_translation_check_box)
        options_layout.addRow(self.include_WKI_check_box, self.import_tags_check_box)
        options_layout.addRow(self.adjust_ease_check_box, self.duplicate_check_box)
        options_layout.addRow('Age (days since created)::', self.time_box)
        options_layout.addRow('Write tags to add to cards:', self.tag_input_box)
        options_group.setLayout(options_layout)

        deck_group = QGroupBox("Deck and Model Selection")
        deck_layout = QFormLayout()
        deck_layout.addRow('Card type:', self.model_options)
        deck_layout.addRow('Language:', self.language_options)
        deck_layout.addRow('Select deck for import:', self.deck_options)
        deck_group.setLayout(deck_layout)

        layout.addWidget(options_group)
        layout.addWidget(self.db_group)
        layout.addWidget(deck_group)
        layout.addWidget(self.auto_import_check_box)
        layout.addWidget(self.import_button)
        self.widget.setLayout(layout)

    def connect_signals(self):
        """ Function handling updating of values selected in GUI """
        self.path_button.clicked.connect(self.find_file)
        self.connect_button.clicked.connect(self.connect_to_lutedb)
        self.import_button.clicked.connect(self.create_cards)
        self.model_options.currentIndexChanged.connect(self.update_variables)
        self.language_options.currentIndexChanged.connect(self.update_variables)
        self.deck_options.currentIndexChanged.connect(self.update_variables)
        self.time_box.valueChanged.connect(self.update_variables)
        self.tag_input_box.editingFinished.connect(self.update_variables)

        # Batch connect all checkboxes to update_checks
        for checkbox in self.checkboxes.values():
            checkbox.stateChanged.connect(self.update_checks)
        
    def load_saved_settings(self):
        """ Loading last settings from config.json file """
        log_info(f'[gui] Loading saved settings from config.json')
        path = self.config.get_config_param('lutedb_path')
        self.path_button.setText(path)

        # loading settings from config.json
        parents_only = self.config.get_config_param('parents_only')
        empty_translation = self.config.get_config_param('empty_translation')
        allow_duplicates = self.config.get_config_param('allow_duplicates')
        import_tags = self.config.get_config_param('import_tags')
        adjust_ease = self.config.get_config_param('adjust_ease')
        include_WKI = self.config.get_config_param('include_WKI')
        last_days = self.config.get_config_param('last_days')
        auto_import = self.config.get_config_param('auto_import')
        selected_deck = self.config.get_config_param('selected_deck')

        # updating states of checkboxes based on loaded settings
        self.parents_only_check_box.setChecked(parents_only)
        self.empty_translation_check_box.setChecked(empty_translation)
        self.duplicate_check_box.setChecked(allow_duplicates)
        self.import_tags_check_box.setChecked(import_tags)
        self.adjust_ease_check_box.setChecked(adjust_ease)
        self.include_WKI_check_box.setChecked(include_WKI)
        self.time_box.setValue(last_days)
        self.auto_import_check_box.setChecked(auto_import)
        self.deck_options.setCurrentText(selected_deck)

        # Attempt automatic connection if a valid path is set
        if path != 'Open file manager' and os.path.exists(path):
            log_info(f'[gui] Attempting to connect to LUTE database at {path}')
            self.connect_to_lutedb()
        else:
            log_info(f'[gui] No valid LUTE database path found in config.')

    def find_file(self):
        """ Open file browser to select the lute.db file """
        file_dialog = QFileDialog()
        db_path = file_dialog.getOpenFileName()[0]
        self.path_button.setText(db_path)
        self.connect_button.setEnabled(True)
        self.connect_button.setText('Click to connect')
        
    def connect_to_lutedb(self):
        """ Connect to the LUTE database and load terms/languages """
        log_info('[gui] User initiated connection to LUTE database.')
        db_path = self.path_button.text()
        db = LuteDatabase(db_path)
        self.parents_only=self.parents_only_check_box.isChecked()
        self.empty_translation=self.empty_translation_check_box.isChecked()
        self.terms, self.languages = db.connect(self.parents_only, self.empty_translation,
                                                self.include_WKI_check_box.isChecked(), date.today() -      timedelta(days=self.time_box.value())
                                               )
        
        # Update connect_and import button after loading terms
        self.connect_button.setText('Reload terms')
        self.import_button.setText(f'Import {len(self.terms)} terms to deck {self.selected_deck}')

        # Get the current time in HH:MM:SS format
        current_time = datetime.now().strftime("%H:%M:%S")
    
        # Update the Database Connection group title
        self.db_group.setTitle(f"Database Connection - {current_time} ({len(self.terms)} terms)")

        if self.terms and self.languages:
            # Update language combo box
            self.language_options.clear()
            for lang in self.languages:
                self.language_options.addItem(lang[1])
            
            # Save path and update UI - enabling creation of Anki notes
            self.config.update_config({'lutedb_path': db_path})
            self.import_button.setEnabled(True)

        else:
            log_warning(f'[gui] No terms meet criteria based on chosen filters')
            
    def update_variables(self):
        """ Update values when user selects different options """
        if self.language_options.currentIndex() >= 0:
            self.selected_lang = self.languages[self.language_options.currentIndex()][0]
            self.config.update_config({'selected_lang': self.selected_lang})
            
        self.selected_model = self.model_options.currentText()
        self.config.update_config({'selected_model': self.selected_model})
        self.selected_deck = self.deck_options.currentText()
        self.config.update_config({'selected_deck': self.selected_deck})
        self.last_days = self.time_box.value()
        self.config.update_config({'last_days': self.last_days})
        self.tags = self.tag_input_box.text().split()
        self.config.update_config({'tags': self.tags})
        
    def update_checks(self):
        """ Update checkbox settings """
        updates = {key: checkbox.isChecked() for key, checkbox in self.checkboxes.items()}
        self.config.update_config(updates)

    def create_cards(self):
        log_info('User initiated card creation process.')
        creator = NoteCreator(
            model_name=self.selected_model,
            deck_name=self.selected_deck,
            allow_duplicates=self.duplicate_check_box.isChecked(),
            import_tags=self.import_tags_check_box.isChecked(),
            adjust_ease=self.adjust_ease_check_box.isChecked(),
            tags=self.tag_input_box.text().split()
        )
        cards_added = creator.create_cards(self.terms, self.selected_lang)
        log_info(f'[gui] Total {cards_added} cards successfully added to deck {self.selected_deck}\n(ignored {len(self.terms)-cards_added} duplicates)')
        showInfo(f'Total {cards_added} cards successfully added to deck {self.selected_deck}\n(ignored {len(self.terms)-cards_added} duplicates)')