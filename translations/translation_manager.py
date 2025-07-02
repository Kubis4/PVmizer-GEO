# translations/translation_manager.py
import importlib
import sys

class TranslationManager:
    def __init__(self, default_language='sk'):
        self.current_language = default_language
        self.version = 0
        self.translations = {}

        # Define available languages
        self.available_languages = ['en', 'sk']
        
        # Load all translations from separate files
        for lang in self.available_languages:
            try:
                # Print debugging info
                print(f"Attempting to load translations for {lang}...")
                
                # Dynamic import of language modules
                module_name = f'translations.{lang}'
                lang_module = importlib.import_module(module_name)
                
                # Check if the module contains 'translations' attribute
                if hasattr(lang_module, 'translations'):
                    self.translations[lang] = lang_module.translations
                    print(f"Loaded {len(self.translations[lang])} translations for {lang}")
                    
                    # Print first 3 keys as a sample
                    sample_keys = list(self.translations[lang].keys())[:3]
                    print(f"Sample keys for {lang}: {sample_keys}")
                else:
                    print(f"Error: Module {module_name} does not have a 'translations' dictionary")
                    # Try to print module contents for debugging
                    print(f"Module contents: {dir(lang_module)}")
            except ImportError as e:
                print(f"Error importing {lang}: {e}")
                print(f"Python path: {sys.path}")
            except Exception as e:
                print(f"Unexpected error loading {lang}: {type(e).__name__}: {e}")
    
    def get_text(self, key):
        """Get text for the given key in the current language"""
        # First try current language
        if self.current_language in self.translations and key in self.translations[self.current_language]:
            return self.translations[self.current_language][key]
        
        # Fallback to English
        if 'en' in self.translations and key in self.translations['en']:
            return self.translations['en'][key]
        
        # Return key if all else fails
        return key
    
    def set_language(self, language_code):
        """Set the current language"""
        if language_code in self.translations:
            print(f"Changing language from {self.current_language} to {language_code}")
            self.current_language = language_code
            # Increment version to force UI refresh
            self.version += 1
            return True
        return False
    
# Create a global instance of the TranslationManager
translator = TranslationManager(default_language='sk')

# Global translation function
def _(key):
    """Get translated text for key in current language"""
    return translator.get_text(key)