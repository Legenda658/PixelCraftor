from PySide6.QtCore import Signal, QObject
class LocalizationManager(QObject):
    language_changed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_language = "ru"
        self.localization = {
            "ru": {
                "app_name": "PixelCraftor",
                "ok": "OK",
                "cancel": "Отмена",
                "yes": "Да",
                "no": "Нет",
                "apply": "Применить",
                "reset": "Сбросить",
                "file": "Файл",
                "edit": "Правка",
                "view": "Вид",
                "settings": "Настройки",
                "help": "Справка",
                "new": "Новый",
                "open": "Открыть...",
                "save": "Сохранить",
                "save_as": "Сохранить как...",
                "export": "Экспорт...",
                "export_xbm": "Экспорт в XBM...",
                "import_xbm": "Импорт из XBM...",
                "exit": "Выход",
                "undo": "Отменить",
                "redo": "Повторить",
                "cut": "Вырезать",
                "copy": "Копировать",
                "paste": "Вставить",
                "delete": "Удалить",
                "select_all": "Выделить всё",
                "clear": "Очистить",
                "zoom_in": "Увеличить",
                "zoom_out": "Уменьшить",
                "toggle_grid": "Показать/скрыть сетку",
                "theme": "Тема",
                "light_theme": "Светлая",
                "dark_theme": "Темная",
                "language": "Язык",
                "about": "О программе",
                "tools": "Инструменты",
                "layers": "Слои",
                "shortcuts": "Горячие клавиши",
                "pen": "Карандаш",
                "eraser": "Ластик",
                "rectangle": "Прямоугольник",
                "select": "Выделение",
                "fill": "Заливка",
                "eyedropper": "Пипетка",
                "line": "Линия",
                "text": "Текст",
                "add_layer": "Добавить слой",
                "remove_layer": "Удалить слой",
                "move_layer_up": "Переместить слой вверх",
                "move_layer_down": "Переместить слой вниз",
                "background_layer": "Фоновый слой",
                "open_file": "Открыть файл",
                "save_file": "Сохранить файл",
                "export_file": "Экспорт файла",
                "export_scale": "Масштаб экспорта",
                "select_scale": "Выберите масштаб:",
            },
            "en": {
                "app_name": "PixelCraftor",
                "ok": "OK",
                "cancel": "Cancel",
                "yes": "Yes",
                "no": "No",
                "apply": "Apply",
                "reset": "Reset",
                "file": "File",
                "edit": "Edit",
                "view": "View",
                "settings": "Settings",
                "help": "Help",
                "new": "New",
                "open": "Open...",
                "save": "Save",
                "save_as": "Save As...",
                "export": "Export...",
                "export_xbm": "Export to XBM...",
                "import_xbm": "Import from XBM...",
                "exit": "Exit",
                "undo": "Undo",
                "redo": "Redo",
                "cut": "Cut",
                "copy": "Copy",
                "paste": "Paste",
                "delete": "Delete",
                "select_all": "Select All",
                "clear": "Clear",
                "zoom_in": "Zoom In",
                "zoom_out": "Zoom Out",
                "toggle_grid": "Toggle Grid",
                "theme": "Theme",
                "light_theme": "Light",
                "dark_theme": "Dark",
                "language": "Language",
                "about": "About",
                "tools": "Tools",
                "layers": "Layers",
                "shortcuts": "Shortcuts",
                "pen": "Pen",
                "eraser": "Eraser",
                "rectangle": "Rectangle",
                "select": "Select",
                "fill": "Fill",
                "eyedropper": "Eyedropper",
                "line": "Line",
                "text": "Text",
                "add_layer": "Add Layer",
                "remove_layer": "Remove Layer",
                "move_layer_up": "Move Layer Up",
                "move_layer_down": "Move Layer Down",
                "background_layer": "Background Layer",
                "open_file": "Open File",
                "save_file": "Save File",
                "export_file": "Export File",
                "export_scale": "Export Scale",
                "select_scale": "Select scale:",
            }
        }
    def set_language(self, language):
        if language not in self.localization:
            return
        self.current_language = language
        self.update_ui()
        self.language_changed.emit(language)
    def get_text(self, key):
        if key in self.localization[self.current_language]:
            return self.localization[self.current_language][key]
        if key in self.localization["ru"]:
            return self.localization["ru"][key]
        return key
    def update_ui(self):
        if not self.parent:
            return
        self.parent.setWindowTitle(self.get_text("app_name"))
        if hasattr(self.parent, "file_menu"):
            self.parent.file_menu.setTitle(self.get_text("file"))
            self.parent.new_action.setText(self.get_text("new"))
            self.parent.open_action.setText(self.get_text("open"))
            self.parent.save_action.setText(self.get_text("save"))
            self.parent.save_as_action.setText(self.get_text("save_as"))
            self.parent.export_action.setText(self.get_text("export"))
            self.parent.export_xbm_action.setText(self.get_text("export_xbm"))
            self.parent.import_xbm_action.setText(self.get_text("import_xbm"))
            self.parent.exit_action.setText(self.get_text("exit"))
        if hasattr(self.parent, "edit_menu"):
            self.parent.edit_menu.setTitle(self.get_text("edit"))
            self.parent.undo_action.setText(self.get_text("undo"))
            self.parent.redo_action.setText(self.get_text("redo"))
            self.parent.select_all_action.setText(self.get_text("select_all"))
            self.parent.clear_action.setText(self.get_text("clear"))
        if hasattr(self.parent, "view_menu"):
            self.parent.view_menu.setTitle(self.get_text("view"))
            self.parent.zoom_in_action.setText(self.get_text("zoom_in"))
            self.parent.zoom_out_action.setText(self.get_text("zoom_out"))
            self.parent.grid_action.setText(self.get_text("toggle_grid"))
        if hasattr(self.parent, "settings_menu"):
            self.parent.settings_menu.setTitle(self.get_text("settings"))
            self.parent.theme_menu.setTitle(self.get_text("theme"))
            self.parent.light_theme_action.setText(self.get_text("light_theme"))
            self.parent.dark_theme_action.setText(self.get_text("dark_theme"))
            self.parent.language_menu.setTitle(self.get_text("language"))
        if hasattr(self.parent, "layers_dock"):
            self.parent.layers_dock.setWindowTitle(self.get_text("layers"))
        if hasattr(self.parent, "right_panel"):
            self.parent.right_panel.setTabText(0, self.get_text("tools"))
            self.parent.right_panel.setTabText(1, self.get_text("shortcuts"))
    def get_current_language(self):
        return self.current_language 