from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QMenu, QLabel, QCheckBox)
from PySide6.QtGui import QIcon, QImage, QPainter, QColor, QAction
from PySide6.QtCore import Qt, Signal, QSize
class LayerItem(QWidget):
    visibility_changed = Signal(bool)
    def __init__(self, name, visible=True, parent=None):
        super().__init__(parent)
        self.layer_name = str(name)
        self.visible = visible
        self.setup_ui()
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        self.visibility_checkbox = QCheckBox()
        self.visibility_checkbox.setChecked(self.visible)
        self.visibility_checkbox.stateChanged.connect(self.toggle_visibility)
        layout.addWidget(self.visibility_checkbox)
        self.name_label = QLabel(self.layer_name)
        layout.addWidget(self.name_label)
        layout.setStretchFactor(self.name_label, 1)
    def toggle_visibility(self, state):
        self.visible = (state == Qt.Checked)
        self.visibility_changed.emit(self.visible)
    def set_name(self, name):
        self.layer_name = str(name)
        self.name_label.setText(self.layer_name)
    def get_name(self):
        return self.layer_name
    def set_visible(self, visible):
        self.visible = visible
        self.visibility_checkbox.setChecked(visible)
    def is_visible(self):
        return self.visible
class LayerWidget(QWidget):
    layer_added = Signal(str)
    layer_removed = Signal(int)
    layer_moved = Signal(int, int)
    layer_visibility_changed = Signal(int, bool)
    current_layer_changed = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.layer_list = QListWidget()
        self.layer_list.setDragDropMode(QListWidget.InternalMove)
        self.layer_list.setSelectionMode(QListWidget.SingleSelection)
        self.layer_list.model().rowsMoved.connect(self.on_layers_reordered)
        self.layer_list.currentRowChanged.connect(self.on_current_layer_changed)
        self.main_layout.addWidget(self.layer_list)
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.add_button.setToolTip("Добавить слой")
        self.add_button.clicked.connect(self.add_layer)
        self.buttons_layout.addWidget(self.add_button)
        self.remove_button = QPushButton("-")
        self.remove_button.setToolTip("Удалить слой")
        self.remove_button.clicked.connect(self.remove_layer)
        self.buttons_layout.addWidget(self.remove_button)
        self.up_button = QPushButton("↑")
        self.up_button.setToolTip("Переместить слой вверх")
        self.up_button.clicked.connect(self.move_layer_up)
        self.buttons_layout.addWidget(self.up_button)
        self.down_button = QPushButton("↓")
        self.down_button.setToolTip("Переместить слой вниз")
        self.down_button.clicked.connect(self.move_layer_down)
        self.buttons_layout.addWidget(self.down_button)
        self.main_layout.addLayout(self.buttons_layout)
    def add_layer(self, name="Новый слой"):
        layer_item = LayerItem(name)
        item = QListWidgetItem()
        item.setSizeHint(layer_item.sizeHint())
        self.layer_list.addItem(item)
        self.layer_list.setItemWidget(item, layer_item)
        layer_item.visibility_changed.connect(lambda visible: self.on_layer_visibility_changed(self.layer_list.row(item), visible))
        self.layer_list.setCurrentItem(item)
        self.layer_added.emit(name)
        return item
    def remove_layer(self):
        current_row = self.layer_list.currentRow()
        if current_row >= 0:
            if self.layer_list.count() > 1:
                self.layer_list.takeItem(current_row)
                self.layer_removed.emit(current_row)
    def move_layer_up(self):
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            current_item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(current_row - 1, current_item)
            self.layer_list.setCurrentItem(current_item)
            self.layer_moved.emit(current_row, current_row - 1)
    def move_layer_down(self):
        current_row = self.layer_list.currentRow()
        if current_row >= 0 and current_row < self.layer_list.count() - 1:
            current_item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(current_row + 1, current_item)
            self.layer_list.setCurrentItem(current_item)
            self.layer_moved.emit(current_row, current_row + 1)
    def on_layers_reordered(self, parent, start, end, destination, row):
        self.layer_moved.emit(start, row)
    def on_layer_visibility_changed(self, index, visible):
        self.layer_visibility_changed.emit(index, visible)
    def on_current_layer_changed(self, current_row):
        self.current_layer_changed.emit(current_row)
    def get_layer_count(self):
        return self.layer_list.count()
    def get_current_layer_index(self):
        return self.layer_list.currentRow()
    def get_layer_name(self, index):
        item = self.layer_list.item(index)
        if item:
            layer_item = self.layer_list.itemWidget(item)
            return layer_item.get_name()
        return None
    def set_layer_name(self, index, name):
        item = self.layer_list.item(index)
        if item:
            layer_item = self.layer_list.itemWidget(item)
            layer_item.set_name(name)
    def is_layer_visible(self, index):
        item = self.layer_list.item(index)
        if item:
            layer_item = self.layer_list.itemWidget(item)
            return layer_item.is_visible()
        return False
    def set_layer_visible(self, index, visible):
        item = self.layer_list.item(index)
        if item:
            layer_item = self.layer_list.itemWidget(item)
            layer_item.set_visible(visible)
    def clear_layers(self):
        self.layer_list.clear()
class LayerManager:
    def __init__(self, layer_widget):
        self.layer_widget = layer_widget
        self.layers = []
        self.layer_widget.layer_added.connect(self.on_layer_added)
        self.layer_widget.layer_removed.connect(self.on_layer_removed)
        self.layer_widget.layer_moved.connect(self.on_layer_moved)
        self.layer_widget.layer_visibility_changed.connect(self.on_layer_visibility_changed)
        self.layer_widget.current_layer_changed.connect(self.on_current_layer_changed)
    def add_layer(self, name="Новый слой"):
        layer_image = QImage(128, 64, QImage.Format_ARGB32)
        layer_image.fill(Qt.transparent)
        self.layers.append({
            "name": name,
            "image": layer_image,
            "visible": True
        })
        self.layer_widget.add_layer(name)
    def remove_layer(self, index):
        if 0 <= index < len(self.layers):
            del self.layers[index]
    def move_layer_up(self):
        self.layer_widget.move_layer_up()
    def move_layer_down(self):
        self.layer_widget.move_layer_down()
    def on_layer_added(self, name):
        layer_image = QImage(128, 64, QImage.Format_ARGB32)
        layer_image.fill(Qt.transparent)
        self.layers.append({
            "name": name,
            "image": layer_image,
            "visible": True
        })
    def on_layer_removed(self, index):
        if 0 <= index < len(self.layers):
            del self.layers[index]
    def on_layer_moved(self, from_index, to_index):
        if 0 <= from_index < len(self.layers) and 0 <= to_index < len(self.layers):
            layer = self.layers.pop(from_index)
            self.layers.insert(to_index, layer)
    def on_layer_visibility_changed(self, index, visible):
        if 0 <= index < len(self.layers):
            self.layers[index]["visible"] = visible
    def on_current_layer_changed(self, index):
        pass
    def get_current_layer(self):
        index = self.layer_widget.get_current_layer_index()
        if 0 <= index < len(self.layers):
            return self.layers[index]
        return None
    def get_composite_image(self):
        if not self.layers:
            return None
        result = QImage(128, 64, QImage.Format_ARGB32)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        for i, layer in enumerate(self.layers):
            if layer["visible"]:
                painter.drawImage(0, 0, layer["image"])
        painter.end()
        return result
    def clear_layers(self):
        self.layers.clear()
        self.layer_widget.clear_layers() 