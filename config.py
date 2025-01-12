from pathlib import Path
import json
from aqt import mw
import os
from typing import Tuple, Dict, Any

class Config:
    def __init__(self):
        """Initializing addon directory and ID"""
        self.addon_dir = os.path.dirname(os.path.abspath(__file__))
        self.addon_id = os.path.basename(self.addon_dir)
        
    def get_config(self) -> Dict[str, Any]:
        """Get current config or return default config if none exists"""
        config = mw.addonManager.getConfig(self.addon_id)
        if config is None:
            config = {
                'lutedb_path': 'Open file manager',
                'parents_only': False,
                'empty_translation': False,
                'allow_duplicates': False,
                'import_tags': True,
                'selected_deck': "Default",
                'adjust_ease': False,
                'include_WKI': False
            }
        return config
    
    def update_config(self, updates: dict) -> bool:
        """Update config with new values while preserving existing ones"""
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
            print(f'Debug - Config update failed: {str(e)}')
            return False
        
    def get_config_param(self, param: str):
        """Loading parameters from config.json file"""
        try:
            conf = self.get_config()
            return conf.get(param)
        except Exception as e:
            defaults = {
                'lutedb_path': 'Open file manager',
                'parents_only': False,
                'empty_translation': False,
                'allow_duplicates': False,
                'import_tags': True,
                'selected_deck': "Default",
                'adjust_ease': False,
                'include_WKI': False
                }
            print(f'Debug - Loading {param} failed: {str(e)}')
            return defaults.get(param)  # Returns the default value for the param