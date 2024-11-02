# LUTE to Anki importer
Anki Add-on to import terms from LUTE to Anki
This is work in progress and by no means the best or most efficient way to code this but could be useful or used as inspiration for better add-ons for importing terms from LUTE to Anki. Currently it supports only simple cards with Two values - Front: term from LUTE, Back: its translation from LUTE.

## How to use it
1. Click "Select lute.db file to import" button to navigate to and select the lute.db file (You can find the path in LUTE in the About - Version and software info section as Data path). After setting it up first time the path should load automatically in the future.
2. Click "Connect to lute.db" button after selecting your lute.db file to load LUTE data
3. Select Card type and language (the terms will be filtered to import only those from selected language)
4. Select language of the terms you want to import (based on language of the text in LUTE from which is the saved term) Currently the language options are loaded from LUTE after Step 2
5. Input tags you want to assign to all cards you will import. Unique tags are separated by a space - "Add this tag" will result in cards having tags "Add", "this" and "tag".
6. Select from how many previous days to import new terms - default is 0 which means today, e.g. 3 means everything from the previous three days + today will be imported
7. Select deck to which you want to import terms from LUTE.
8. Check if you want to allow duplicates (creating notes with the same Front (first value) already existing in your Anki and if you wish to import tags from LUTE (On by default).
9. Click "Import to selected deck" button - this will create cards with Front (First field): word, Back (Second field): translation in the selected deck. Based on selected filters 0 cards might be created.
10. When finished importing close the add-on window and go learn the new cards in Anki.

## Contact
Discord: HippoShaman#1138
