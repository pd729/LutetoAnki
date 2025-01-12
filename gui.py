# gui.py
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo
from typing import List, Callable
from .config import Config
from .database import LuteDatabase
from .note_creator import NoteCreator
from datetime import date, timedelta

class ImporterGui:
    def __init__(self, config: Config):
        # initialiying variables
        self.config = config
        self.widget = QWidget()
        self.widget.setWindowTitle('Lute to Anki importer')
        self.terms = []
        self.languages = []
        self.selected_model = ''
        self.selected_lang = ''
        self.selected_deck = 'Default'
        self.parents_only = False
        self.empty_translation = False
        self.adjust_ease = False
        self.include_WKI = False
        self.last_days = 0
        self.tags = []
        self.setup_gui()
        
    def setup_gui(self):
        self.create_widgets()
        self.create_layout()
        self.connect_signals()
        self.load_saved_settings()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        self.path_button = QPushButton(self.widget)
        self.connect_label = QLabel('Connect to lute.db:', self.widget)
        self.connect_button = QPushButton('Click to connect', self.widget)
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
        
    def create_model_combobox(self) -> QComboBox:
        """Create and populate the note type combo box"""
        combo = QComboBox(self.widget)
        for model in mw.col.models.all():
            combo.addItem(model['name'])
        if combo.count() > 0:
            self.selected_model = combo.itemText(0)
        return combo
        
    def create_deck_combobox(self) -> QComboBox:
        """Create and populate the deck combo box"""
        combo = QComboBox(self.widget)
        decks = mw.col.decks.all_names_and_ids()
        for deck in decks:
            combo.addItem(deck.name)
        if combo.count() > 0:
            self.selected_deck = combo.itemText(0)
        return combo
        
    def create_layout(self):
        """Creating 2 column layout with widgets defined in create_widgets"""
        layout = QFormLayout(self.widget)
        layout.addRow('Select lute.db file to import:', self.path_button)
        layout.addRow(self.parents_only_check_box, self.empty_translation_check_box)
        layout.addRow(self.include_WKI_check_box, self.import_tags_check_box)
        layout.addRow('Time filter (x days before today):', self.time_box)
        layout.addRow(self.connect_label, self.connect_button)
        layout.addRow('Card type:', self.model_options)
        layout.addRow('Language:', self.language_options)
        layout.addRow('Write tags to add to cards:', self.tag_input_box)
        layout.addRow('Select deck for import:', self.deck_options)
        layout.addRow(self.adjust_ease_check_box, self.duplicate_check_box)
        layout.addRow('Create new cards:', self.import_button)
        self.widget.setLayout(layout)
        
    def connect_signals(self):
        """Function handling updating of values selected in GUI"""
        self.path_button.clicked.connect(self.find_file)
        self.connect_button.clicked.connect(self.connect_to_lutedb)
        self.import_button.clicked.connect(self.create_cards)
        self.model_options.currentIndexChanged.connect(self.update_variables)
        self.language_options.currentIndexChanged.connect(self.update_variables)
        self.deck_options.currentIndexChanged.connect(self.update_variables)
        self.time_box.valueChanged.connect(self.update_variables)
        self.tag_input_box.editingFinished.connect(self.update_variables)
        self.parents_only_check_box.stateChanged.connect(self.update_checks)
        self.empty_translation_check_box.stateChanged.connect(self.update_checks)
        self.duplicate_check_box.stateChanged.connect(self.update_checks)
        self.import_tags_check_box.stateChanged.connect(self.update_checks)
        self.adjust_ease_check_box.stateChanged.connect(self.update_checks)
        self.include_WKI_check_box.stateChanged.connect(self.update_checks)
        
    def load_saved_settings(self):
        """Loading last settings from config.json file"""
        path = self.config.get_config_param('lutedb_path')
        self.path_button.setText(path)

        # loading settings from config.json
        parents_only = self.config.get_config_param('parents_only')
        empty_translation = self.config.get_config_param('empty_translation')
        allow_duplicates = self.config.get_config_param('allow_duplicates')
        import_tags = self.config.get_config_param('import_tags')
        adjust_ease = self.config.get_config_param('adjust_ease')
        include_WKI = self.config.get_config_param('include_WKI')

        # updating states of checkboxes based on loaded settings
        self.parents_only_check_box.setChecked(parents_only)
        self.empty_translation_check_box.setChecked(empty_translation)
        self.duplicate_check_box.setChecked(allow_duplicates)
        self.import_tags_check_box.setChecked(import_tags)
        self.adjust_ease_check_box.setChecked(adjust_ease)
        self.include_WKI_check_box.setChecked(include_WKI)

        # loading and (setting if possible) default deck to use
        saved_deck = self.config.get_config_param('selected_deck')
        if saved_deck in [self.deck_options.itemText(i) for i in range(self.deck_options.count())]:
            self.deck_options.setCurrentText(saved_deck)
        
    def find_file(self):
        """Open file browser to select the lute.db file"""
        file_dialog = QFileDialog()
        db_path = file_dialog.getOpenFileName()[0]
        self.path_button.setText(db_path)
        self.connect_button.setEnabled(True)
        self.connect_label.setText('Connect to lute.db:')
        self.connect_button.setText("Click to connect")
        
    def connect_to_lutedb(self):
        """Connect to the LUTE database and load terms/languages"""
        db_path = self.path_button.text()
        db = LuteDatabase(db_path)
        self.parents_only=self.parents_only_check_box.isChecked(),
        self.empty_translation=self.empty_translation_check_box.isChecked(),
        self.terms, self.languages = db.connect(self.parents_only_check_box.isChecked(), self.empty_translation_check_box.isChecked(),
                                                self.include_WKI_check_box.isChecked(), str(date.today() - timedelta(days=self.time_box.value()))
                                               )
        
        # Update connect_button after loading terms and connect_label to show how many terms were loaded
        self.connect_button.setText('Reload terms')
        self.connect_label.setText(f'Loaded {len(self.terms)} terms')

        if self.terms and self.languages:
            # Update language combo box
            self.language_options.clear()
            for lang in self.languages:
                self.language_options.addItem(lang[1])
            
            # Save path and update UI - enabling creation of Anki notes
            self.config.update_config({'lutedb_path': db_path})
            self.import_button.setEnabled(True)
            
            showInfo(f'Connected and loaded {len(self.terms)} terms')

        # adding infobox in case no terms are loaded
        else:
            showInfo(f'No terms meet criteria based on chosen filters')
            
    def update_variables(self):
        """Update values when user selects different options"""
        if self.language_options.currentIndex() >= 0:
            self.selected_lang = self.languages[self.language_options.currentIndex()][0]
            
        self.selected_model = self.model_options.currentText()
        self.selected_deck = self.deck_options.currentText()
        self.config.update_config({'selected_deck': self.selected_deck})
        self.last_days = self.time_box.value()
        self.tags = self.tag_input_box.text().split()
        
    def update_checks(self):
        """Update checkbox settings"""
        self.config.update_config({
            'parents_only': self.parents_only_check_box.isChecked(),
            'empty_translation': self.empty_translation_check_box.isChecked(),
            'allow_duplicates': self.duplicate_check_box.isChecked(),
            'import_tags': self.import_tags_check_box.isChecked(),
            'adjust_ease': self.adjust_ease_check_box.isChecked(),
            'include_WKI': self.include_WKI_check_box.isChecked()
        })
        
    def create_cards(self):
        """Create new Anki cards from selected terms"""
        creator = NoteCreator(
            model_name=self.selected_model,
            deck_name=self.selected_deck,
            allow_duplicates=self.duplicate_check_box.isChecked(),
            import_tags=self.import_tags_check_box.isChecked(),
            adjust_ease=self.adjust_ease_check_box.isChecked(),
            include_WKI=self.include_WKI_check_box.isChecked(),
            tags=self.tags,
        )
        
        cards_added = creator.create_cards(self.terms, self.selected_lang)
        from aqt.utils import showInfo
        showInfo(f'{cards_added} cards added to deck {self.selected_deck}')
