# translations/__init__.py

# Import translation dictionaries
from .en import translations as en_translations
from .sk import translations as sk_translations

class TranslationManager:
    def __init__(self, default_language='sk'):
        self.translations = {
            'en': en_translations,
            'sk': sk_translations
        }
        self.current_language = default_language
    
    def set_language(self, language_code):
        """Change the current language"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_text(self, key):
        """Get translation for the given key"""
        if self.current_language in self.translations and key in self.translations[self.current_language]:
            return self.translations[self.current_language][key]
        
        # Fallback to English if translation not found
        if 'en' in self.translations and key in self.translations['en']:
            return self.translations['en'][key]
        
        # Return the key itself if translation not found
        return key

    def get_fresh_translator(self):
        """Return a translation function that uses the current language state"""
        def translate(key):
            return self.get_text(key)
        return translate
# Create the global translator instance
translator = TranslationManager()

# Define the dynamic translation function
def _(key):
    return translator.get_text(key)