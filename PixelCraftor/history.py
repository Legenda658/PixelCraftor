from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QLabel)
from PySide6.QtGui import QIcon, QPixmap, QImage, QPainter
from PySide6.QtCore import Qt, Signal, QSize, QTimer
class HistoryThumbnail(QWidget):
    def __init__(self, image, description, parent=None):
        super().__init__(parent)
        self.image = image
        self.description = description
        self.setup_ui()
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        self.thumbnail_label = QLabel()
        self.update_thumbnail()
        layout.addWidget(self.thumbnail_label)
        self.description_label = QLabel(self.description)
        layout.addWidget(self.description_label)
        layout.setStretchFactor(self.description_label, 1)
    def update_thumbnail(self):
        thumbnail = self.image.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(thumbnail)
        self.thumbnail_label.setPixmap(pixmap)
    def set_image(self, image):
        self.image = image
        self.update_thumbnail()
    def set_description(self, description):
        self.description = description
        self.description_label.setText(description)
    def get_image(self):
        return self.image
class HistoryWidget(QWidget):
    history_selected = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.currentRowChanged.connect(self.on_history_selected)
        layout.addWidget(self.history_list)
        buttons_layout = QHBoxLayout()
        self.undo_button = QPushButton("↩")
        self.undo_button.setToolTip("Отменить")
        self.undo_button.clicked.connect(self.undo)
        buttons_layout.addWidget(self.undo_button)
        self.redo_button = QPushButton("↪")
        self.redo_button.setToolTip("Повторить")
        self.redo_button.clicked.connect(self.redo)
        buttons_layout.addWidget(self.redo_button)
        self.clear_button = QPushButton("🗑")
        self.clear_button.setToolTip("Очистить историю")
        self.clear_button.clicked.connect(self.clear)
        buttons_layout.addWidget(self.clear_button)
        layout.addLayout(buttons_layout)
    def add_history_item(self, image, description):
        thumbnail = HistoryThumbnail(image, description)
        item = QListWidgetItem()
        item.setSizeHint(thumbnail.sizeHint())
        self.history_list.addItem(item)
        self.history_list.setItemWidget(item, thumbnail)
        self.history_list.setCurrentItem(item)
        return item
    def on_history_selected(self, current_row):
        self.history_selected.emit(current_row)
    def undo(self):
        current_row = self.history_list.currentRow()
        if current_row > 0:
            self.history_list.setCurrentRow(current_row - 1)
    def redo(self):
        current_row = self.history_list.currentRow()
        if current_row < self.history_list.count() - 1:
            self.history_list.setCurrentRow(current_row + 1)
    def clear(self):
        self.history_list.clear()
    def get_current_image(self):
        current_row = self.history_list.currentRow()
        if current_row >= 0:
            item = self.history_list.item(current_row)
            thumbnail = self.history_list.itemWidget(item)
            return thumbnail.get_image()
        return None
    def get_history_count(self):
        return self.history_list.count()
    def get_current_index(self):
        return self.history_list.currentRow()
class HistoryManager:
    def __init__(self, canvas, max_history=50):
        self.canvas = canvas
        self.max_history = max_history
        self.history_widget = None
        self.undo_stack = []
        self.redo_stack = []
        self.current_image = None
        self.is_modified = False
        if canvas:
            self.canvas.canvas_changed.connect(self.on_canvas_changed)
            self.save_state("Начальное состояние")
    def set_history_widget(self, widget):
        self.history_widget = widget
        if widget:
            widget.history_selected.connect(self.on_history_selected)
            self.update_history_widget()
    def save_state(self, description=""):
        image = self.canvas.get_image()
        if self.current_image and image.constBits() == self.current_image.constBits():
            return
        self.current_image = image.copy()
        self.undo_stack.append({
            "image": self.current_image,
            "description": description or f"Состояние {len(self.undo_stack) + 1}"
        })
        self.redo_stack.clear()
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.update_history_widget()
        self.is_modified = True
    def undo(self):
        if len(self.undo_stack) <= 1:
            return False
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        previous_state = self.undo_stack[-1]
        self.canvas.set_image(previous_state["image"])
        self.current_image = previous_state["image"].copy()
        self.update_history_widget()
        return True
    def redo(self):
        if not self.redo_stack:
            return False
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        self.canvas.set_image(next_state["image"])
        self.current_image = next_state["image"].copy()
        self.update_history_widget()
        return True
    def on_canvas_changed(self):
        QTimer.singleShot(100, lambda: self.save_state())
    def on_history_selected(self, index):
        if 0 <= index < len(self.undo_stack):
            state = self.undo_stack[index]
            self.canvas.set_image(state["image"])
            self.current_image = state["image"].copy()
            self.undo_stack = self.undo_stack[:index + 1]
            self.redo_stack.clear()
    def update_history_widget(self):
        if not self.history_widget:
            return
        self.history_widget.clear()
        for state in self.undo_stack:
            self.history_widget.add_history_item(state["image"], state["description"])
    def clear_history(self):
        current_image = self.canvas.get_image().copy()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.undo_stack.append({
            "image": current_image,
            "description": "Начальное состояние"
        })
        self.update_history_widget()
        self.is_modified = False
    def is_modified(self):
        return self.is_modified 