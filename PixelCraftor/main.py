import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QColorDialog, QFileDialog,
                             QScrollArea, QSplitter, QListWidget, QListWidgetItem, 
                             QComboBox, QSpinBox, QToolBar, QStatusBar, QMessageBox,
                             QDockWidget, QTabWidget)
from PySide6.QtGui import (QIcon, QPixmap, QImage, QPainter, QPen, QColor, QKeySequence,
                          QAction, QShortcut, QCursor, QDrag, QFont, QFontMetrics)
from PySide6.QtCore import Qt, QSize, QPoint, QRect, QMimeData, Signal, Slot, QSettings
from canvas import PixelCanvas
from layers import LayerManager, LayerWidget
from tools import ToolPanel
from history import HistoryManager
from settings import Settings
from xbm_converter import XBMConverter
from shortcuts import ShortcutManager, ShortcutList
from themes import ThemeManager
from localization import LocalizationManager
from resolution_widget import ResolutionWidget
from resolution_dialog import ResolutionDialog
class PixelCraftor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.theme_manager = ThemeManager(self)
        self.localization = LocalizationManager(self)
        self.shortcuts = ShortcutManager(self)
        self.setWindowIcon(QIcon("PixelCraftor.ico"))
        self.setup_ui()
        self.load_settings()
        self.setup_shortcuts()
    def setup_ui(self):
        self.setWindowTitle("PixelCraftor")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter)
        self.setup_layers_panel()
        self.setup_canvas_area()
        self.setup_right_panel()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.main_splitter.setSizes([200, 600, 200])
        self.resize(1200, 800)
    def setup_layers_panel(self):
        self.layers_dock = QDockWidget(self.localization.get_text("layers"))
        self.layers_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.layer_widget = LayerWidget()
        self.layers_dock.setWidget(self.layer_widget)
        self.main_splitter.addWidget(self.layers_dock)
        self.layer_manager = LayerManager(self.layer_widget)
    def setup_canvas_area(self):
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setAlignment(Qt.AlignCenter)
        self.canvas = PixelCanvas(128, 64, self)
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_layout.addWidget(self.canvas_scroll)
        self.resolution_widget = ResolutionWidget(self.canvas.width, self.canvas.height)
        self.resolution_widget.resolution_changed.connect(self.change_resolution)
        self.canvas_layout.addWidget(self.resolution_widget)
        self.main_splitter.addWidget(self.canvas_container)
        self.history_manager = HistoryManager(self.canvas)
        self.canvas.position_changed.connect(self.update_position_label)
    def setup_right_panel(self):
        self.right_panel = QTabWidget()
        self.tool_panel = ToolPanel(self.canvas)
        self.right_panel.addTab(self.tool_panel, self.localization.get_text("tools"))
        self.shortcut_list = ShortcutList()
        self.right_panel.addTab(self.shortcut_list, self.localization.get_text("shortcuts"))
        self.main_splitter.addWidget(self.right_panel)
    def setup_menu(self):
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu(self.localization.get_text("file"))
        self.new_action = QAction(QIcon(), self.localization.get_text("new"), self)
        self.new_action.triggered.connect(self.new_file)
        self.new_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_N))
        self.file_menu.addAction(self.new_action)
        self.open_action = QAction(QIcon(), self.localization.get_text("open"), self)
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_O))
        self.file_menu.addAction(self.open_action)
        self.save_action = QAction(QIcon(), self.localization.get_text("save"), self)
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_S))
        self.file_menu.addAction(self.save_action)
        self.save_as_action = QAction(QIcon(), self.localization.get_text("save_as"), self)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.save_as_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_S))
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.export_action = QAction(QIcon(), self.localization.get_text("export"), self)
        self.export_action.triggered.connect(self.export_image)
        self.export_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_E))
        self.file_menu.addAction(self.export_action)
        self.export_xbm_action = QAction(QIcon(), self.localization.get_text("export_xbm"), self)
        self.export_xbm_action.triggered.connect(self.export_xbm)
        self.file_menu.addAction(self.export_xbm_action)
        self.import_xbm_action = QAction(QIcon(), self.localization.get_text("import_xbm"), self)
        self.import_xbm_action.triggered.connect(self.import_xbm)
        self.file_menu.addAction(self.import_xbm_action)
        self.file_menu.addSeparator()
        self.exit_action = QAction(QIcon(), self.localization.get_text("exit"), self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut(QKeySequence(Qt.AltModifier | Qt.Key_F4))
        self.file_menu.addAction(self.exit_action)
        self.edit_menu = self.menu_bar.addMenu(self.localization.get_text("edit"))
        self.undo_action = QAction(QIcon(), self.localization.get_text("undo"), self)
        self.undo_action.triggered.connect(self.history_manager.undo)
        self.undo_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Z))
        self.edit_menu.addAction(self.undo_action)
        self.redo_action = QAction(QIcon(), self.localization.get_text("redo"), self)
        self.redo_action.triggered.connect(self.history_manager.redo)
        self.redo_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Z))
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.cut_action = QAction(QIcon(), "Вырезать", self)
        self.cut_action.triggered.connect(self.cut_selection)
        self.cut_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_X))
        self.edit_menu.addAction(self.cut_action)
        self.copy_action = QAction(QIcon(), "Копировать", self)
        self.copy_action.triggered.connect(self.canvas.copy_selection)
        self.copy_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_C))
        self.edit_menu.addAction(self.copy_action)
        self.paste_action = QAction(QIcon(), "Вставить", self)
        self.paste_action.triggered.connect(self.canvas.paste)
        self.paste_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_V))
        self.edit_menu.addAction(self.paste_action)
        self.delete_action = QAction(QIcon(), "Удалить", self)
        self.delete_action.triggered.connect(self.canvas.delete_selection)
        self.delete_action.setShortcut(QKeySequence(Qt.Key_Delete))
        self.edit_menu.addAction(self.delete_action)
        self.edit_menu.addSeparator()
        self.select_all_action = QAction(QIcon(), self.localization.get_text("select_all"), self)
        self.select_all_action.triggered.connect(self.canvas.select_all)
        self.select_all_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_A))
        self.edit_menu.addAction(self.select_all_action)
        self.clear_action = QAction(QIcon(), self.localization.get_text("clear"), self)
        self.clear_action.triggered.connect(self.canvas.clear)
        self.clear_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Delete))
        self.edit_menu.addAction(self.clear_action)
        self.view_menu = self.menu_bar.addMenu(self.localization.get_text("view"))
        self.zoom_in_action = QAction(QIcon(), self.localization.get_text("zoom_in"), self)
        self.zoom_in_action.triggered.connect(self.canvas.zoom_in)
        self.zoom_in_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Plus))
        self.view_menu.addAction(self.zoom_in_action)
        self.zoom_out_action = QAction(QIcon(), self.localization.get_text("zoom_out"), self)
        self.zoom_out_action.triggered.connect(self.canvas.zoom_out)
        self.zoom_out_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Minus))
        self.view_menu.addAction(self.zoom_out_action)
        self.view_menu.addSeparator()
        self.grid_action = QAction(QIcon(), self.localization.get_text("toggle_grid"), self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(self.toggle_grid)
        self.grid_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_G))
        self.view_menu.addAction(self.grid_action)
        self.rulers_action = QAction(QIcon(), "Показать/скрыть линейки", self)
        self.rulers_action.setCheckable(True)
        self.rulers_action.setChecked(True)
        self.rulers_action.triggered.connect(self.toggle_rulers)
        self.rulers_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_R))
        self.view_menu.addAction(self.rulers_action)
        self.clear_guides_action = QAction(QIcon(), "Очистить направляющие", self)
        self.clear_guides_action.triggered.connect(self.canvas.clear_guides)
        self.clear_guides_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_G))
        self.view_menu.addAction(self.clear_guides_action)
        self.transform_menu = self.menu_bar.addMenu("Трансформация")
        self.flip_h_action = QAction(QIcon(), "Отразить по горизонтали", self)
        self.flip_h_action.triggered.connect(self.canvas.flip_selection_horizontal)
        self.flip_h_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_H))
        self.transform_menu.addAction(self.flip_h_action)
        self.flip_v_action = QAction(QIcon(), "Отразить по вертикали", self)
        self.flip_v_action.triggered.connect(self.canvas.flip_selection_vertical)
        self.flip_v_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_V))
        self.transform_menu.addAction(self.flip_v_action)
        self.rotate_cw_action = QAction(QIcon(), "Повернуть на 90° по часовой", self)
        self.rotate_cw_action.triggered.connect(lambda: self.canvas.rotate_selection(90))
        self.rotate_cw_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.Key_R))
        self.transform_menu.addAction(self.rotate_cw_action)
        self.rotate_ccw_action = QAction(QIcon(), "Повернуть на 90° против часовой", self)
        self.rotate_ccw_action.triggered.connect(lambda: self.canvas.rotate_selection(-90))
        self.rotate_ccw_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_R))
        self.transform_menu.addAction(self.rotate_ccw_action)
        self.scale_up_action = QAction(QIcon(), "Увеличить масштаб", self)
        self.scale_up_action.triggered.connect(lambda: self.canvas.scale_selection(1.2, 1.2))
        self.scale_up_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Plus))
        self.transform_menu.addAction(self.scale_up_action)
        self.scale_down_action = QAction(QIcon(), "Уменьшить масштаб", self)
        self.scale_down_action.triggered.connect(lambda: self.canvas.scale_selection(0.8, 0.8))
        self.scale_down_action.setShortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Minus))
        self.transform_menu.addAction(self.scale_down_action)
        self.settings_menu = self.menu_bar.addMenu(self.localization.get_text("settings"))
        self.resolution_action = QAction(QIcon(), "Изменить разрешение...", self)
        self.resolution_action.triggered.connect(self.resolution_widget.show_resolution_dialog)
        self.settings_menu.addAction(self.resolution_action)
        self.settings_menu.addSeparator()
        self.theme_menu = self.settings_menu.addMenu(self.localization.get_text("theme"))
        self.light_theme_action = QAction(QIcon(), self.localization.get_text("light_theme"), self)
        self.light_theme_action.triggered.connect(lambda: self.theme_manager.set_theme("light"))
        self.theme_menu.addAction(self.light_theme_action)
        self.dark_theme_action = QAction(QIcon(), self.localization.get_text("dark_theme"), self)
        self.dark_theme_action.triggered.connect(lambda: self.theme_manager.set_theme("dark"))
        self.theme_menu.addAction(self.dark_theme_action)
        self.language_menu = self.settings_menu.addMenu(self.localization.get_text("language"))
        self.russian_action = QAction(QIcon(), "Русский", self)
        self.russian_action.triggered.connect(lambda: self.localization.set_language("ru"))
        self.language_menu.addAction(self.russian_action)
        self.english_action = QAction(QIcon(), "English", self)
        self.english_action.triggered.connect(lambda: self.localization.set_language("en"))
        self.language_menu.addAction(self.english_action)
    def setup_toolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.zoom_in_action)
        self.toolbar.addAction(self.zoom_out_action)
    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.position_label = QLabel()
        self.status_bar.addWidget(self.position_label)
        self.canvas_size_label = QLabel(f"{self.canvas.width}x{self.canvas.height}")
        self.status_bar.addPermanentWidget(self.canvas_size_label)
    def setup_shortcuts(self):
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Delete), self.canvas.delete_selection)
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Backspace), self.canvas.delete_selection)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_X), self.cut_selection)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_C), self.canvas.copy_selection)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_V), self.canvas.paste)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_A), self.canvas.select_all)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Z), self.history_manager.undo)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Z), self.history_manager.redo)
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Left), lambda: self.canvas.move_selection(-1, 0))
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Right), lambda: self.canvas.move_selection(1, 0))
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Up), lambda: self.canvas.move_selection(0, -1))
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Down), lambda: self.canvas.move_selection(0, 1))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ShiftModifier | Qt.Key_Left), lambda: self.canvas.move_selection(-10, 0))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ShiftModifier | Qt.Key_Right), lambda: self.canvas.move_selection(10, 0))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ShiftModifier | Qt.Key_Up), lambda: self.canvas.move_selection(0, -10))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ShiftModifier | Qt.Key_Down), lambda: self.canvas.move_selection(0, 10))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Up), self.layer_manager.move_layer_up)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Down), self.layer_manager.move_layer_down)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Plus), self.canvas.zoom_in)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_Minus), self.canvas.zoom_out)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_G), lambda: self.toggle_grid_shortcut())
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_R), lambda: self.toggle_rulers_shortcut())
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_H), self.canvas.flip_selection_horizontal)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_V), self.canvas.flip_selection_vertical)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.AltModifier | Qt.Key_R), lambda: self.canvas.rotate_selection(90))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.AltModifier | Qt.Key_R), lambda: self.canvas.rotate_selection(-90))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Plus), lambda: self.canvas.scale_selection(1.2, 1.2))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_Minus), lambda: self.canvas.scale_selection(0.8, 0.8))
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_N), self.new_file)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_O), self.open_file)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_S), self.save_file)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.ShiftModifier | Qt.Key_S), self.save_file_as)
        self.shortcuts.register_shortcut(QKeySequence(Qt.ControlModifier | Qt.Key_E), self.export_image)
        self.shortcuts.register_shortcut(QKeySequence(Qt.Key_Escape), self.canvas.reset_selection)
        self.shortcut_list.update_shortcuts(self.shortcuts.get_shortcuts())
    def toggle_grid_shortcut(self):
        self.grid_action.setChecked(not self.grid_action.isChecked())
        self.toggle_grid()
    def toggle_rulers_shortcut(self):
        self.rulers_action.setChecked(not self.rulers_action.isChecked())
        self.toggle_rulers()
    def load_settings(self):
        self.settings.load()
        theme = self.settings.get("theme", "light")
        self.theme_manager.set_theme(theme)
        language = self.settings.get("language", "ru")
        self.localization.set_language(language)
        show_grid = self.settings.get("show_grid", True)
        self.grid_action.setChecked(show_grid)
        self.canvas.set_grid_visible(show_grid)
    def save_settings(self):
        self.settings.set("theme", self.theme_manager.current_theme)
        self.settings.set("language", self.localization.current_language)
        self.settings.set("show_grid", self.grid_action.isChecked())
        self.settings.save()
    def toggle_grid(self):
        show_grid = self.grid_action.isChecked()
        self.canvas.set_grid_visible(show_grid)
    def new_file(self):
        dialog = ResolutionDialog(self.canvas.width, self.canvas.height, self)
        def on_resolution_selected(width, height):
            self.canvas.resize_canvas(width, height)
            self.canvas.clear()
            self.layer_manager.clear_layers()
            self.layer_manager.add_layer(self.localization.get_text("background_layer"))
            self.history_manager.clear_history()
            self.canvas_size_label.setText(f"{width}x{height}")
            self.resolution_widget.update_resolution(width, height)
        dialog.resolution_changed.connect(on_resolution_selected)
        dialog.exec()
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.localization.get_text("open_file"),
            "",
            "Images (*.png *.jpg *.bmp *.webp *.pbm *.tga *.ico);;All Files (*)"
        )
        if file_path:
            self.canvas.load_image(file_path)
            self.canvas_size_label.setText(f"{self.canvas.width}x{self.canvas.height}")
            self.resolution_widget.update_resolution(self.canvas.width, self.canvas.height)
    def save_file(self):
        if not hasattr(self, "current_file") or not self.current_file:
            self.save_file_as()
        else:
            self.canvas.save_image(self.current_file)
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.localization.get_text("save_file"),
            "",
            "PNG (*.png);;BMP (*.bmp);;JPEG (*.jpg);;WEBP (*.webp);;PBM (*.pbm);;TGA (*.tga);;ICO (*.ico)"
        )
        if file_path:
            self.current_file = file_path
            self.canvas.save_image(file_path)
    def export_image(self):
        scale, ok = QSpinBox.getInt(
            None, 
            self.localization.get_text("export_scale"),
            self.localization.get_text("select_scale"),
            1, 1, 16, 1
        )
        if ok:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                self.localization.get_text("export_file"),
                "",
                "PNG (*.png);;BMP (*.bmp);;JPEG (*.jpg);;WEBP (*.webp);;PBM (*.pbm);;TGA (*.tga);;ICO (*.ico)"
            )
            if file_path:
                self.canvas.export_image(file_path, scale)
    def export_xbm(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.localization.get_text("export_xbm"),
            "",
            "XBM (*.xbm);;C Header (*.h);;Text (*.txt)"
        )
        if file_path:
            xbm_converter = XBMConverter()
            xbm_data = xbm_converter.image_to_xbm(self.canvas.get_image())
            with open(file_path, 'w') as f:
                f.write(xbm_data)
    def import_xbm(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.localization.get_text("import_xbm"),
            "",
            "XBM (*.xbm);;C Header (*.h);;Text (*.txt);;All Files (*)"
        )
        if file_path:
            xbm_converter = XBMConverter()
            with open(file_path, 'r') as f:
                xbm_data = f.read()
            image = xbm_converter.xbm_to_image(xbm_data)
            if image:
                self.canvas.set_image(image)
                self.canvas_size_label.setText(f"{self.canvas.width}x{self.canvas.height}")
    def closeEvent(self, event):
        self.save_settings()
        event.accept()
    def change_resolution(self, width, height):
        self.canvas.resize_canvas(width, height)
        self.canvas_size_label.setText(f"{width}x{height}")
    def update_position_label(self, x, y):
        self.position_label.setText(f"X: {x}, Y: {y}")
    def cut_selection(self):
        self.canvas.copy_selection()
        self.canvas.delete_selection()
    def toggle_rulers(self):
        visible = self.rulers_action.isChecked()
        self.canvas.set_rulers_visible(visible)
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("PixelCraftor.ico"))
    window = PixelCraftor()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main() 