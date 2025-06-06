from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QColorDialog, QLabel, QGridLayout, QSlider,
                             QGroupBox, QRadioButton, QButtonGroup)
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QBrush
from PySide6.QtCore import Qt, Signal, QSize
class ColorButton(QPushButton):
    color_changed = Signal(QColor)
    def __init__(self, color=Qt.black, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(32, 32)
        self.update_icon()
        self.clicked.connect(self.choose_color)
    def update_icon(self):
        pixmap = QPixmap(24, 24)
        pixmap.fill(self.color)
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(24, 24))
    def choose_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.set_color(color)
    def set_color(self, color):
        self.color = color
        self.update_icon()
        self.color_changed.emit(color)
    def get_color(self):
        return self.color
class ColorPalette(QWidget):
    color_selected = Signal(QColor)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_colors = [
            Qt.black, Qt.white, Qt.red, Qt.green, Qt.blue,
            Qt.cyan, Qt.magenta, Qt.yellow, Qt.gray, Qt.darkGray
        ]
        self.current_color = Qt.black
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        color_group = QGroupBox("Текущий цвет")
        color_layout = QHBoxLayout(color_group)
        self.color_button = ColorButton(self.current_color)
        self.color_button.color_changed.connect(self.on_color_changed)
        color_layout.addWidget(self.color_button)
        layout.addWidget(color_group)
        palette_group = QGroupBox("Палитра")
        palette_layout = QGridLayout(palette_group)
        for i, color in enumerate(self.preset_colors):
            button = ColorButton(color)
            button.color_changed.connect(self.on_preset_color_changed)
            button.clicked.connect(lambda checked, c=color: self.on_preset_color_selected(c))
            palette_layout.addWidget(button, i // 5, i % 5)
        layout.addWidget(palette_group)
        layout.addStretch()
    def on_color_changed(self, color):
        self.current_color = color
        self.color_selected.emit(color)
    def on_preset_color_changed(self, color):
        self.color_button.set_color(color)
    def on_preset_color_selected(self, color):
        self.color_button.set_color(color)
    def get_current_color(self):
        return self.current_color
    def set_current_color(self, color):
        self.color_button.set_color(color)
class ToolButton(QPushButton):
    def __init__(self, tool_name, icon_name=None, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.setFixedSize(32, 32)
        self.setCheckable(True)
        if icon_name:
            self.setIcon(QIcon(icon_name))
            self.setIconSize(QSize(24, 24))
    def get_tool_name(self):
        return self.tool_name
class ToolPanel(QWidget):
    tool_changed = Signal(str)
    color_changed = Signal(QColor)
    def __init__(self, canvas=None, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.current_tool = "pen"
        self.setup_ui()
        if canvas:
            self.tool_changed.connect(canvas.set_tool)
            self.color_changed.connect(canvas.set_color)
    def setup_ui(self):
        layout = QVBoxLayout(self)
        tools_group = QGroupBox("Инструменты")
        tools_layout = QGridLayout(tools_group)
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        self.pen_button = ToolButton("pen")
        self.pen_button.setText("✏️")
        self.pen_button.setToolTip("Карандаш")
        self.pen_button.setChecked(True)
        self.tool_group.addButton(self.pen_button)
        tools_layout.addWidget(self.pen_button, 0, 0)
        self.eraser_button = ToolButton("eraser")
        self.eraser_button.setText("🧽")
        self.eraser_button.setToolTip("Ластик")
        self.tool_group.addButton(self.eraser_button)
        tools_layout.addWidget(self.eraser_button, 0, 1)
        self.rect_button = ToolButton("rectangle")
        self.rect_button.setText("□")
        self.rect_button.setToolTip("Прямоугольник")
        self.tool_group.addButton(self.rect_button)
        tools_layout.addWidget(self.rect_button, 0, 2)
        self.select_button = ToolButton("select")
        self.select_button.setText("◫")
        self.select_button.setToolTip("Выделение")
        self.tool_group.addButton(self.select_button)
        tools_layout.addWidget(self.select_button, 0, 3)
        self.fill_button = ToolButton("fill")
        self.fill_button.setText("🪣")
        self.fill_button.setToolTip("Заливка")
        self.tool_group.addButton(self.fill_button)
        tools_layout.addWidget(self.fill_button, 1, 0)
        self.eyedropper_button = ToolButton("eyedropper")
        self.eyedropper_button.setText("💉")
        self.eyedropper_button.setToolTip("Пипетка")
        self.tool_group.addButton(self.eyedropper_button)
        tools_layout.addWidget(self.eyedropper_button, 1, 1)
        self.line_button = ToolButton("line")
        self.line_button.setText("╱")
        self.line_button.setToolTip("Линия")
        self.tool_group.addButton(self.line_button)
        tools_layout.addWidget(self.line_button, 1, 2)
        self.text_button = ToolButton("text")
        self.text_button.setText("A")
        self.text_button.setToolTip("Текст")
        self.tool_group.addButton(self.text_button)
        tools_layout.addWidget(self.text_button, 1, 3)
        self.pen_button.clicked.connect(lambda: self.set_tool("pen"))
        self.eraser_button.clicked.connect(lambda: self.set_tool("eraser"))
        self.rect_button.clicked.connect(lambda: self.set_tool("rectangle"))
        self.select_button.clicked.connect(lambda: self.set_tool("select"))
        self.fill_button.clicked.connect(lambda: self.set_tool("fill"))
        self.eyedropper_button.clicked.connect(lambda: self.set_tool("eyedropper"))
        self.line_button.clicked.connect(lambda: self.set_tool("line"))
        self.text_button.clicked.connect(lambda: self.set_tool("text"))
        layout.addWidget(tools_group)
        self.color_palette = ColorPalette()
        self.color_palette.color_selected.connect(self.on_color_changed)
        layout.addWidget(self.color_palette)
        layout.addStretch()
    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.tool_changed.emit(tool_name)
        print(f"Выбран инструмент: {tool_name}")
    def on_color_changed(self, color):
        self.color_changed.emit(color)
    def get_current_tool(self):
        return self.current_tool
    def get_current_color(self):
        return self.color_palette.get_current_color() 