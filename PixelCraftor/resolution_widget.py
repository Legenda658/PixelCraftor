from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Signal, Qt
from resolution_dialog import ResolutionDialog
class ResolutionWidget(QWidget):
    resolution_changed = Signal(int, int)
    def __init__(self, width=128, height=64, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.setup_ui()
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)  
        self.resolution_label = QLabel(f"Разрешение: {self.width} x {self.height}")
        self.change_button = QPushButton("Изменить...")
        self.change_button.setMaximumWidth(100)
        self.change_button.clicked.connect(self.show_resolution_dialog)
        layout.addWidget(self.resolution_label)
        layout.addStretch()
        layout.addWidget(self.change_button)
        self.setLayout(layout)
    def update_resolution(self, width, height):
        self.width = width
        self.height = height
        self.resolution_label.setText(f"Разрешение: {self.width} x {self.height}")
    def show_resolution_dialog(self):
        dialog = ResolutionDialog(self.width, self.height, self)
        dialog.resolution_changed.connect(self.on_resolution_changed)
        dialog.exec()
    def on_resolution_changed(self, width, height):
        self.update_resolution(width, height)
        self.resolution_changed.emit(width, height) 