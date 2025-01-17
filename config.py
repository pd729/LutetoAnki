# config.py
import json
from aqt import mw
import os
from typing import Dict, Any
from .logger import log_info, log_error

defaults = {
            'lutedb_path': 'Open file manager',
            'parents_only': False,
            'empty_translation': False,
            'allow_duplicates': False,
            'import_tags': False,
            'selected_deck': "Default",
            'selected_model': 'Basic',
            'adjust_ease': False,
            'include_WKI': False,
            'selected_lang': 0,
            'last_days': 0,
            'tags': [],
            'auto_import': False
            }

class Config:
    def __init__(self):
        """ Initializing addon directory and ID """
        global defaults
        self.addon_dir = os.path.dirname(os.path.abspath(__file__))
        self.addon_id = os.path.basename(self.addon_dir)
        self.default_config = defaults

    # Get exisiting config or use the default one
    def get_config(self) -> Dict[str, Any]:
        """Get current config directly from config.json"""
        config_path = os.path.join(self.addon_dir, 'config.json')
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                log_info('Configuration loaded succesfully')
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to default config if file not found or invalid
            global defaults
            config = defaults
        return config
    
    def update_config(self, updates: dict) -> bool:
        """ Update config with new values while preserving existing ones """
        try:
            # Get current config
            current_config = self.get_config()
            
            # Update with new values
            current_config.update(updates)
            
            # Save updated config
            config_path = os.path.join(self.addon_dir, 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=4)
                
            # Update Anki's config
            mw.addonManager.writeConfig(self.addon_id, current_config)

            return True
        except Exception as e:
            log_error(f'[config] Configuration update failed: {str(e)}')
            return False
        
    def get_config_param(self, param: str):
        """ Loading parameters from config.json file """
        try:
            conf = self.get_config()
            return conf.get(param)
        except Exception as e:
            global defaults
            log_error(f'[config] Requested config parameter {param} not found, using default: {str(e)}')
            return defaults.get(param)  # Returns the default value for the param