# LUTE to Anki importer

Anki Add-on to import terms from LUTE to Anki.

This is still work in progress and by no means the best or most efficient way to code this. It currently supports creating simple cards with two fields:

- Front: Term from LUTE
- Back: Translation from LUTE.

## How to use it

1. **Select database**: Click "Select lute.db file to import" to choose your lute.db file. (Find this path in LUTE under *About > Version and software info > Data path*). If it is already set up the add-on will automatically try to connect to the .db file and load terms based on previous filters and settings.
2. **Configure Filters**:
    - Include only parent terms
    - Include terms with blank translations
    - Include terms with statuses: Well-known and Ignored
    - Import tags (enabled by default)
    - Select how many previous days to import terms from (default is 0 for today)
3. **Connect to Database**: Click "Connect to lute.db" to load terms if path not set already. Use "Reload terms" if filters change.
4. **Select Card type**: Choose the Anki card type (default: term on Front, translation on Back).
5. **Select language**: Choose the language for imported terms.Currently the language options are loaded after loading terms from LUTE in Step 3
6. **Add tags**: Input space-separated tags you want to assign to all imported cards. Unique tags are separated by a space - "Add this tag" will result in cards having tags "Add", "this" and "tag".
7. **Select deck**: Pick the target deck (automatically selects the last used deck).
8. **Auto Import**: Enable the auto-import feature to automatically sync new LUTE terms everytime you open Anki.
9. **Import**: Click "Import to selected deck" button to create the cards
10. **Finish**: Close the add-on window and start reviewing your new cards in Anki.

## Configurable settings

1. **Parent terms only**: if you want to create notes only for Parent terms from Lute
2. **Allowing empty translation**: if you want to include also terms for which you have not filled the translation field in Lute
3. **Allowing duplicates**: if you want to allow duplicates (creating notes with the same Front (first value) already existing in your Anki)
4. **Importing tags**: if you wish to import tags from LUTE (On by default)
5. **Adjusting ease** (difficulty) of created Anki notes:
    - Default: 250%
    - Well-known/Ignored: 300%
    - Adjusts by 15% for higher/lower levels
6. **Allow Well-Known and Ignored**: if you have Well-known or Ignored terms with translation in LUTE for which you want to create Anki cards

### Advanced Configuration

You can manually configure settings in Anki's Add-ons menu:

**Config File:**

- Edit `config.json` to set the `lute.db` path, preferred deck, and auto-import frequency.
- Last-used options are saved and auto-loaded for future sessions.
