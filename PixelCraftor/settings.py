import json
import os
from PySide6.QtCore import QSettings
class Settings:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = {}
        self.default_settings = {
            "theme": "light",
            "language": "ru",
            "show_grid": True,
            "default_width": 128,
            "default_height": 64,
            "recent_files": [],
            "autosave": True,
            "autosave_interval": 5,  
            "max_history": 50
        }
        self.load()
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")
                self.settings = self.default_settings.copy()
        else:
            self.settings = self.default_settings.copy()
    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    def get(self, key, default=None):
        if key in self.settings:
            return self.settings[key]
        if key in self.default_settings:
            return self.default_settings[key]
        return default
    def set(self, key, value):
        self.settings[key] = value
    def reset(self, key=None):
        if key:
            if key in self.default_settings:
                self.settings[key] = self.default_settings[key]
        else:
            self.settings = self.default_settings.copy()
    def add_recent_file(self, file_path):
        recent_files = self.get("recent_files", [])
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        recent_files = recent_files[:10]
        self.set("recent_files", recent_files)
    def get_recent_files(self):
        return self.get("recent_files", []) 