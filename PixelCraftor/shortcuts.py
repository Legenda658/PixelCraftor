from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt, Signal
class ShortcutManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.shortcuts = {}
    def register_shortcut(self, key_sequence, callback):
        shortcut = QShortcut(key_sequence, self.parent)
        shortcut.activated.connect(callback)
        key_string = key_sequence.toString()
        self.shortcuts[key_string] = {
            "key_sequence": key_sequence,
            "callback": callback,
            "shortcut": shortcut,
            "description": self.get_description(key_string)
        }
        return shortcut
    def unregister_shortcut(self, key_sequence):
        key_string = key_sequence.toString()
        if key_string in self.shortcuts:
            shortcut = self.shortcuts[key_string]["shortcut"]
            shortcut.setEnabled(False)
            shortcut.deleteLater()
            del self.shortcuts[key_string]
    def get_shortcuts(self):
        return self.shortcuts
    def get_description(self, key_string):
        descriptions = {
            "Del": "Удалить выделение",
            "Backspace": "Удалить выделение",
            "Left": "Переместить выделение влево на 1px",
            "Right": "Переместить выделение вправо на 1px",
            "Up": "Переместить выделение вверх на 1px",
            "Down": "Переместить выделение вниз на 1px",
            "Shift+Left": "Переместить выделение влево на 10px",
            "Shift+Right": "Переместить выделение вправо на 10px",
            "Shift+Up": "Переместить выделение вверх на 10px",
            "Shift+Down": "Переместить выделение вниз на 10px",
            "Ctrl+Up": "Переместить слой вверх",
            "Ctrl+Down": "Переместить слой вниз",
            "Ctrl+C": "Копировать выделение",
            "Ctrl+V": "Вставить",
            "Ctrl+A": "Выделить всё",
            "Ctrl+Z": "Отменить",
            "Ctrl+Shift+Z": "Повторить",
            "Ctrl++": "Увеличить масштаб",
            "Ctrl+-": "Уменьшить масштаб",
            "Esc": "Сбросить выделение"
        }
        if key_string in descriptions:
            return descriptions[key_string]
        return ""
class ShortcutList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Клавиша", "Действие"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
    def update_shortcuts(self, shortcuts):
        self.table.setRowCount(0)
        row = 0
        for key_string, shortcut_info in shortcuts.items():
            self.table.insertRow(row)
            key_item = QTableWidgetItem(key_string)
            description_item = QTableWidgetItem(shortcut_info["description"])
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, description_item)
            row += 1
        self.table.sortItems(0)
    def set_language(self, language):
        if language == "ru":
            self.table.setHorizontalHeaderLabels(["Клавиша", "Действие"])
        else:
            self.table.setHorizontalHeaderLabels(["Key", "Action"]) 