from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, Signal, QObject
class ThemeManager(QObject):
    theme_changed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_theme = "light"
        self.light_theme = {
            "window": QColor(240, 240, 240),
            "window_text": QColor(0, 0, 0),
            "base": QColor(255, 255, 255),
            "alternate_base": QColor(233, 233, 233),
            "text": QColor(0, 0, 0),
            "button": QColor(240, 240, 240),
            "button_text": QColor(0, 0, 0),
            "bright_text": QColor(0, 0, 0),
            "highlight": QColor(42, 130, 218),
            "highlight_text": QColor(255, 255, 255),
            "link": QColor(42, 130, 218),
            "tool_tip_base": QColor(255, 255, 220),
            "tool_tip_text": QColor(0, 0, 0)
        }
        self.dark_theme = {
            "window": QColor(53, 53, 53),
            "window_text": QColor(255, 255, 255),
            "base": QColor(25, 25, 25),
            "alternate_base": QColor(53, 53, 53),
            "text": QColor(255, 255, 255),
            "button": QColor(53, 53, 53),
            "button_text": QColor(255, 255, 255),
            "bright_text": QColor(255, 255, 255),
            "highlight": QColor(42, 130, 218),
            "highlight_text": QColor(255, 255, 255),
            "link": QColor(42, 130, 218),
            "tool_tip_base": QColor(42, 42, 42),
            "tool_tip_text": QColor(255, 255, 255)
        }
    def set_theme(self, theme_name):
        if theme_name not in ["light", "dark"]:
            return
        self.current_theme = theme_name
        theme_colors = self.light_theme if theme_name == "light" else self.dark_theme
        palette = QPalette()
        palette.setColor(QPalette.Window, theme_colors["window"])
        palette.setColor(QPalette.WindowText, theme_colors["window_text"])
        palette.setColor(QPalette.Base, theme_colors["base"])
        palette.setColor(QPalette.AlternateBase, theme_colors["alternate_base"])
        palette.setColor(QPalette.Text, theme_colors["text"])
        palette.setColor(QPalette.Button, theme_colors["button"])
        palette.setColor(QPalette.ButtonText, theme_colors["button_text"])
        palette.setColor(QPalette.BrightText, theme_colors["bright_text"])
        palette.setColor(QPalette.Highlight, theme_colors["highlight"])
        palette.setColor(QPalette.HighlightedText, theme_colors["highlight_text"])
        palette.setColor(QPalette.Link, theme_colors["link"])
        palette.setColor(QPalette.ToolTipBase, theme_colors["tool_tip_base"])
        palette.setColor(QPalette.ToolTipText, theme_colors["tool_tip_text"])
        QApplication.setPalette(palette)
        if theme_name == "dark":
            QApplication.setStyle("Fusion")
            style_sheet = """
            QToolTip { 
                color: #ffffff; 
                background-color: #2a2a2a; 
                border: 1px solid #767676; 
            }
            QMenu { 
                background-color: #2a2a2a; 
                border: 1px solid #767676; 
            }
            QMenu::item:selected { 
                background-color: #2a82da; 
            }
            """
            QApplication.instance().setStyleSheet(style_sheet)
        else:
            QApplication.setStyle("Fusion")
            QApplication.instance().setStyleSheet("")
        self.theme_changed.emit(theme_name)
    def get_current_theme(self):
        return self.current_theme 