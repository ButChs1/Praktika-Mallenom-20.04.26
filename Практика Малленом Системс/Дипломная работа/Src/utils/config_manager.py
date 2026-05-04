import json
import os

class ConfigManager:
    DEFAULT_CONFIG = {
        "language": "ru",
        "theme": "dark"
    }
    CONFIG_FILE = "config.json"
    LOCALES_DIR = "locales"

    @classmethod
    def load_config(cls):
        if not os.path.exists(cls.CONFIG_FILE):
            cls.save_config(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG
        
        try:
            with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return cls.DEFAULT_CONFIG

    @classmethod
    def save_config(cls, config):
        with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    @classmethod
    def get_translations(cls, lang_code):
        file_path = os.path.join(cls.LOCALES_DIR, f"{lang_code}.json")
        if not os.path.exists(file_path):
            file_path = os.path.join(cls.LOCALES_DIR, "ru.json")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки перевода: {e}")
            return {}