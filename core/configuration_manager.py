#!/usr/bin/env python3
"""
Configuration Manager - Manages application configuration and state
"""
from PyQt5.QtCore import QObject

class ConfigurationManager(QObject):
    """Manages application configuration and state"""
    
    def __init__(self):
        super().__init__()
        # Basic settings
        self.scale_factor = 0.05
        self.dark_theme = True
        
        # Feature availability
        self.enhanced_mode = False
        self.enhanced_roof_mode = False
        
        # Drawing state
        self.roof_points = []
        self.roof_boundary = []
        self.ridge_data = []
        self.original_image_size = None
        
        # Models and tools
        self.roof_model = None
        self.snipping_tool = None
        
        # Detect available features
        self._detect_features()
    
    
    def get_wall_height_from_slider(self, slider_value):
        """Convert slider value to wall height in meters"""
        return slider_value / 10.0
    
    def get_roof_type_from_combo(self, combo_text):
        """Convert combo box text to roof type"""
        text = combo_text.lower()
        if "flat" in text:
            return "flat"
        elif "gable" in text:
            return "gable"
        elif "hip" in text:
            return "hip"
        elif "pyramid" in text:
            return "pyramid"
        return "flat"
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            import json
            import os
            
            # Create settings directory if it doesn't exist
            settings_dir = os.path.join(os.path.expanduser("~"), ".pvmizer_geo")
            os.makedirs(settings_dir, exist_ok=True)
            
            # Prepare settings data
            settings_data = {
                'dark_theme': getattr(self, 'dark_theme', False),
                'enhanced_features': getattr(self, 'enhanced_features', {}),
                'window_geometry': getattr(self, 'window_geometry', None),
                'last_location': getattr(self, 'last_location', ''),
                'building_defaults': getattr(self, 'building_defaults', {
                    'wall_height': 3.0,
                    'roof_type': 'Flat',
                    'roof_pitch': 15.0
                })
            }
            
            # Save to file
            settings_file = os.path.join(settings_dir, 'settings.json')
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            
            print(f"✅ Settings saved to: {settings_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            return False

    def load_settings(self):
        """Load settings from file"""
        try:
            import json
            import os
            
            settings_file = os.path.join(os.path.expanduser("~"), ".pvmizer_geo", 'settings.json')
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings_data = json.load(f)
                
                # Apply loaded settings
                self.dark_theme = settings_data.get('dark_theme', False)
                self.enhanced_features = settings_data.get('enhanced_features', {})
                self.window_geometry = settings_data.get('window_geometry', None)
                self.last_location = settings_data.get('last_location', '')
                self.building_defaults = settings_data.get('building_defaults', {
                    'wall_height': 3.0,
                    'roof_type': 'Flat', 
                    'roof_pitch': 15.0
                })
                
                print("✅ Settings loaded successfully")
                return True
            else:
                print("ℹ️ No settings file found, using defaults")
                return False
                
        except Exception as e:
            print(f"❌ Error loading settings: {e}")
            return False