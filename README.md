# LUTE to Anki importer
Anki Add-on to import terms from LUTE to Anki
This is work in progress and by no means the best or most efficient way to code this but could be useful or used as inspiration for better add-ons for importing terms from LUTE to Anki. Currently it supports only simple cards with Two values - Front: term from LUTE, Back: its translation from LUTE.

## How to use it
1. Click "Select lute.db file to import" button to navigate to and select the lute.db file when using it for the first time (You can find the path in LUTE in the About - Version and software info section as Data path).
<<<<<<< HEAD
2. Choose filters which will be used for loading terms from lute.db - checkboxes to include only parent terms, terms with blank translation, terms with statuses Well known and Ignored and whether you wish to import tags
    Additionally also select from how many previous days to import new terms - default is 0 which means today, e.g. 3 means everything from the previous three days + today will be imported
3. Click "Connect to lute.db" button after selecting your lute.db file and setting up filters to load LUTE data
    If you change filters click "Reload terms" to reflect the changes in loaded terms
4. Select Card type which will be used (currently only term for Front and translation for Back are used)
5. Select language of the terms you want to import (based on language of the text in LUTE from which is the saved term) Currently the language options are loaded after loading terms from LUTE in Step 3
6. Input tags you want to assign to all cards you will import. Unique tags are separated by a space - "Add this tag" will result in cards having tags "Add", "this" and "tag".
7. Select deck to which you want to import terms from LUTE. It automatically selects the last time used deck.
8. Choose additional options from settings checkboxes.
=======
2. Click "Connect to lute.db" button after selecting your lute.db file to load LUTE data
3. Select Card type and language (the terms will be filtered to import only those from selected language)
4. Select language of the terms you want to import (based on language of the text in LUTE from which is the saved term) Currently the language options are loaded from LUTE after Step 2
5. Input tags you want to assign to all cards you will import. Unique tags are separated by a space - "Add this tag" will result in cards having tags "Add", "this" and "tag".
6. Select from how many previous days to import new terms - default is 0 which means today, e.g. 3 means everything from the previous three days + today will be imported
7. Select deck to which you want to import terms from LUTE. It automatically selects the last time used deck.
8. Choose options from settings checkboxes.
>>>>>>> 650c0ebbf9f3234138b5074aae274df7cd203093
9. Click "Import to selected deck" button - this will create cards with Front (First field): word, Back (Second field): translation in the selected deck. Based on selected filters 0 cards might be created.
10. When finished importing close the add-on window and go learn the new cards in Anki.

## Configurable settings
<<<<<<< HEAD
1. Parent terms only: if you want to create notes only for Parent terms from Lute
2. Allowing empty translation: if you want to include also terms for which you have not filled the translation field in Lute
3. Allowing duplicates: if you want to allow duplicates (creating notes with the same Front (first value) already existing in your Anki
4. Importing tags: if you wish to import tags from LUTE (On by default)
5. Adjusting ease (difficulty) of created Anki notes: uses Anki default of 250% for LUTE terms with status 3 and bumps it up/down by 15% for higher/lower level and uses 300% for Well-known and Ignored terms
6. Allow Well-known and ignored: if you have Well-known or Ignored terms with translation in LUTE for which you want to create Anki cards

In Addons menu in Anki you can edit Config (config.json) to also set up the lute.db path and deck to use which are otherwise saved based on your choices in GUI. For all of these settings the last used choice is saved and will be loaded the next time the addon is used.
=======
1. Allowing duplicates: if you want to allow duplicates (creating notes with the same Front (first value) already existing in your Anki
2. Importing tags: if you wish to import tags from LUTE (On by default)
3. Adjusting ease (difficulty) of created Anki notes: uses Anki default of 250% for LUTE terms with status 3 and bumps it up/down by 15% for higher/lower level and uses 300% for Well-known and Ignored terms
4. Allow Well-known and ignored: if you have Well-known or Ignored terms with translation in LUTE for which you want to create Anki cards (they will be always ignored when they have no translation/definition)

In Addons menu in Anki you can edit Config (config.json) to also set up the lute.db path and deck to use which are otherwise saved based on your choices in GUI. For all of these settings the last used choice is saved and will be loaded the next time the addon is used.

## Contact
Discord: HippoShaman#1138
>>>>>>> 650c0ebbf9f3234138b5074aae274df7cd203093
