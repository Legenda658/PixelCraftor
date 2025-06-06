from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QComboBox, QGridLayout)
from PySide6.QtCore import Qt, Signal
class ResolutionDialog(QDialog):
    resolution_changed = Signal(int, int)
    def __init__(self, current_width=128, current_height=64, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор разрешения")
        self.setMinimumWidth(300)
        self.current_width = current_width
        self.current_height = current_height
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel("Ширина:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 1024)
        self.width_spin.setValue(self.current_width)
        grid_layout.addWidget(self.width_spin, 0, 1)
        grid_layout.addWidget(QLabel("Высота:"), 1, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 1024)
        self.height_spin.setValue(self.current_height)
        grid_layout.addWidget(self.height_spin, 1, 1)
        grid_layout.addWidget(QLabel("Предустановки:"), 2, 0)
        self.presets_combo = QComboBox()
        self.presets_combo.addItem("Выберите...")
        self.presets_combo.addItem("128 x 64 (OLED дисплей)")
        self.presets_combo.addItem("256 x 128")
        self.presets_combo.addItem("320 x 240")
        self.presets_combo.addItem("640 x 480")
        self.presets_combo.addItem("800 x 600")
        self.presets_combo.addItem("16 x 16 (Иконка)")
        self.presets_combo.addItem("32 x 32 (Иконка)")
        self.presets_combo.addItem("48 x 48 (Иконка)")
        self.presets_combo.addItem("64 x 64 (Иконка)")
        self.presets_combo.currentIndexChanged.connect(self.preset_selected)
        grid_layout.addWidget(self.presets_combo, 2, 1)
        layout.addLayout(grid_layout)
        buttons_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("ОК")
        self.ok_button.clicked.connect(self.accept_resolution)
        self.ok_button.setDefault(True)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    def preset_selected(self, index):
        if index == 0:
            return
        width, height = 0, 0
        if index == 1:  
            width, height = 128, 64
        elif index == 2:  
            width, height = 256, 128
        elif index == 3:  
            width, height = 320, 240
        elif index == 4:  
            width, height = 640, 480
        elif index == 5:  
            width, height = 800, 600
        elif index == 6:  
            width, height = 16, 16
        elif index == 7:  
            width, height = 32, 32
        elif index == 8:  
            width, height = 48, 48
        elif index == 9:  
            width, height = 64, 64
        if width > 0 and height > 0:
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
        self.presets_combo.setCurrentIndex(0)
    def accept_resolution(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        self.resolution_changed.emit(width, height)
        self.accept() 