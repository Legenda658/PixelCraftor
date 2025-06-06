from PySide6.QtWidgets import QWidget, QApplication, QInputDialog, QFontDialog
from PySide6.QtGui import (QPainter, QPen, QColor, QPixmap, QImage, 
                          QCursor, QPainterPath, QBrush, QFont, QFontMetrics,
                          QTransform)
from PySide6.QtCore import Qt, QPoint, QRect, QSize, Signal, Slot
import os
from PIL import Image
class PixelCanvas(QWidget):
    canvas_changed = Signal()  
    position_changed = Signal(int, int)  
    def __init__(self, width=128, height=64, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.scale = 8
        self.current_color = QColor(0, 0, 0)
        self.current_tool = "pen"
        self.image = QImage(self.width, self.height, QImage.Format_ARGB32)
        self.image.fill(Qt.white)
        self.undo_buffer = []
        self.redo_buffer = []
        self.selection = None
        self.selection_start = None
        self.selection_image = None
        self.drawing = False
        self.last_pos = None
        self.eraser_mode = False
        self.show_grid = True
        self.grid_size = 8  
        self.grid_color = QColor(200, 200, 200)  
        self.grid_style = Qt.SolidLine  
        self.show_rulers = True  
        self.ruler_size = 20  
        self.ruler_color = QColor(80, 80, 80)  
        self.ruler_text_color = QColor(50, 50, 50)  
        self.ruler_font = QFont("Arial", 7)  
        self.guides = []  
        self.guide_color = QColor(0, 120, 215)  
        self.creating_guide = False  
        self.guide_orientation = None  
        self.active_guide_index = -1  
        self.line_start = None
        self.text_font = QFont("Arial", 8)  
        self.floating_text = None
        self.floating_text_pos = None
        self.is_dragging_text = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.update_size()
    def update_size(self):
        ruler_offset = self.ruler_size if self.show_rulers else 0
        width = self.width * self.scale + ruler_offset
        height = self.height * self.scale + ruler_offset
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        self.update()
    def resize_canvas(self, width, height):
        self.save_state()
        old_image = self.image.copy()
        self.width = width
        self.height = height
        self.image = QImage(width, height, QImage.Format_ARGB32)
        self.image.fill(Qt.white)
        painter = QPainter(self.image)
        painter.drawImage(0, 0, old_image)
        painter.end()
        self.update_size()
        self.canvas_changed.emit()
    def set_scale(self, scale):
        self.scale = max(1, min(32, scale))
        self.update_size()
    def zoom_in(self):
        self.set_scale(self.scale + 1)
    def zoom_out(self):
        self.set_scale(self.scale - 1)
    def set_color(self, color):
        self.current_color = color
    def set_tool(self, tool):
        print(f"Canvas: установлен инструмент {tool}")
        self.current_tool = tool
        if tool != "text":
            self.floating_text = None
            self.floating_text_pos = None
            self.is_dragging_text = False
            self.update()
        self.eraser_mode = (tool == "eraser")
    def set_grid_visible(self, visible):
        self.show_grid = visible
        self.update()
    def set_grid_size(self, size):
        self.grid_size = max(1, size)  
        self.update()
    def set_grid_color(self, color):
        self.grid_color = color
        self.update()
    def set_grid_style(self, style):
        self.grid_style = style
        self.update()
    def clear(self):
        self.save_state()
        self.image.fill(Qt.white)
        self.update()
        self.canvas_changed.emit()
    def save_state(self):
        self.undo_buffer.append(self.image.copy())
        self.redo_buffer.clear()
    def undo(self):
        if self.undo_buffer:
            self.redo_buffer.append(self.image.copy())
            self.image = self.undo_buffer.pop()
            self.update()
            self.canvas_changed.emit()
    def redo(self):
        if self.redo_buffer:
            self.undo_buffer.append(self.image.copy())
            self.image = self.redo_buffer.pop()
            self.update()
            self.canvas_changed.emit()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        ruler_offset = self.ruler_size if self.show_rulers else 0
        painter.drawImage(
            QRect(ruler_offset, ruler_offset, 
                  self.width * self.scale, 
                  self.height * self.scale), 
            self.image
        )
        if self.show_grid and self.scale >= 4:
            painter.setPen(QPen(self.grid_color, 1, self.grid_style))
            for x in range(0, self.width + 1, self.grid_size):
                painter.drawLine(
                    x * self.scale + ruler_offset, ruler_offset, 
                    x * self.scale + ruler_offset, self.height * self.scale + ruler_offset
                )
            for y in range(0, self.height + 1, self.grid_size):
                painter.drawLine(
                    ruler_offset, y * self.scale + ruler_offset, 
                    self.width * self.scale + ruler_offset, y * self.scale + ruler_offset
                )
        if self.show_rulers:
            self.draw_rulers(painter, ruler_offset)
        self.draw_guides(painter, ruler_offset)
        if self.selection:
            painter.setPen(QPen(QColor(0, 120, 215), 1, Qt.DashLine))
            painter.drawRect(
                self.selection.x() * self.scale + ruler_offset,
                self.selection.y() * self.scale + ruler_offset,
                self.selection.width() * self.scale,
                self.selection.height() * self.scale
            )
        if self.current_tool == "line" and self.line_start and self.last_pos:
            painter.setPen(QPen(self.current_color, 1, Qt.SolidLine))
            painter.drawLine(
                self.line_start.x() * self.scale + self.scale // 2 + ruler_offset,
                self.line_start.y() * self.scale + self.scale // 2 + ruler_offset,
                self.last_pos.x() * self.scale + self.scale // 2 + ruler_offset,
                self.last_pos.y() * self.scale + self.scale // 2 + ruler_offset
            )
        if self.floating_text and self.floating_text_pos:
            temp_image = QImage(
                self.width * self.scale + ruler_offset, 
                self.height * self.scale + ruler_offset, 
                QImage.Format_ARGB32
            )
            temp_image.fill(Qt.transparent)
            text_painter = QPainter(temp_image)
            text_painter.setPen(self.current_color)
            try:
                text_painter.setFont(self.text_font)
                font_metrics = text_painter.fontMetrics()
                text_width = font_metrics.horizontalAdvance(self.floating_text)
                text_height = font_metrics.height()
                text_painter.drawText(
                    self.floating_text_pos.x() * self.scale + ruler_offset,
                    self.floating_text_pos.y() * self.scale + font_metrics.ascent() + ruler_offset,
                    self.floating_text
                )
                painter.fillRect(
                    self.floating_text_pos.x() * self.scale - 2 + ruler_offset,
                    self.floating_text_pos.y() * self.scale - 2 + ruler_offset,
                    text_width + 4,
                    text_height + 4,
                    QColor(200, 200, 255, 128)
                )
            except Exception as e:
                print(f"Ошибка при отображении текста: {e}")
                painter.setPen(self.current_color)
                painter.drawText(
                    self.floating_text_pos.x() * self.scale + ruler_offset,
                    self.floating_text_pos.y() * self.scale + 10 + ruler_offset,
                    self.floating_text
                )
            finally:
                text_painter.end()
            painter.drawImage(0, 0, temp_image)
    def draw_rulers(self, painter, offset):
        ruler_rect_h = QRect(offset, 0, self.width * self.scale, offset)
        ruler_rect_v = QRect(0, offset, offset, self.height * self.scale)
        painter.fillRect(ruler_rect_h, self.ruler_color.lighter(120))
        painter.fillRect(ruler_rect_v, self.ruler_color.lighter(120))
        painter.fillRect(0, 0, offset, offset, self.ruler_color.lighter(110))  
        painter.setPen(self.ruler_text_color)
        painter.setFont(self.ruler_font)
        for x in range(0, self.width + 1, 5):  
            x_pos = x * self.scale + offset
            if x % 10 == 0:  
                painter.drawLine(x_pos, offset - 5, x_pos, offset - 1)
                if x % 20 == 0:
                    painter.drawText(x_pos - 10, 2, 20, offset - 6, Qt.AlignCenter, str(x))
            else:
                painter.drawLine(x_pos, offset - 3, x_pos, offset - 1)
        for y in range(0, self.height + 1, 5):  
            y_pos = y * self.scale + offset
            if y % 10 == 0:  
                painter.drawLine(offset - 5, y_pos, offset - 1, y_pos)
                if y % 20 == 0:
                    painter.save()
                    painter.translate(offset - 10, y_pos)
                    painter.rotate(-90)
                    painter.drawText(-10, 0, 20, offset - 6, Qt.AlignCenter, str(y))
                    painter.restore()
            else:
                painter.drawLine(offset - 3, y_pos, offset - 1, y_pos)
    def draw_guides(self, painter, offset):
        if not self.guides:
            return
        painter.setPen(QPen(self.guide_color, 1, Qt.DashLine))
        for i, (orientation, position) in enumerate(self.guides):
            if orientation == 'horizontal':
                y = position * self.scale + offset
                painter.drawLine(offset, y, self.width * self.scale + offset, y)
            elif orientation == 'vertical':
                x = position * self.scale + offset
                painter.drawLine(x, offset, x, self.height * self.scale + offset)
    def mousePressEvent(self, event):
        ruler_offset = self.ruler_size if self.show_rulers else 0
        if self.show_rulers:
            if event.position().x() < ruler_offset and event.position().y() >= ruler_offset:
                self.creating_guide = True
                self.guide_orientation = 'horizontal'
                y = int((event.position().y() - ruler_offset) / self.scale)
                self.add_guide('horizontal', y)
                self.active_guide_index = len(self.guides) - 1
                return
            elif event.position().x() >= ruler_offset and event.position().y() < ruler_offset:
                self.creating_guide = True
                self.guide_orientation = 'vertical'
                x = int((event.position().x() - ruler_offset) / self.scale)
                self.add_guide('vertical', x)
                self.active_guide_index = len(self.guides) - 1
                return
            elif event.position().x() < ruler_offset and event.position().y() < ruler_offset:
                self.clear_guides()
                return
        if self.guides:
            for i, (orientation, position) in enumerate(self.guides):
                if orientation == 'horizontal':
                    y = position * self.scale + ruler_offset
                    if abs(event.position().y() - y) <= 5:  
                        self.active_guide_index = i
                        self.creating_guide = True
                        self.guide_orientation = 'horizontal'
                        return
                elif orientation == 'vertical':
                    x = position * self.scale + ruler_offset
                    if abs(event.position().x() - x) <= 5:  
                        self.active_guide_index = i
                        self.creating_guide = True
                        self.guide_orientation = 'vertical'
                        return
        x = int((event.position().x() - ruler_offset) / self.scale)
        y = int((event.position().y() - ruler_offset) / self.scale)
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if self.floating_text:
            if event.button() == Qt.LeftButton:
                try:
                    font_metrics = QFontMetrics(self.text_font)
                    text_width = font_metrics.horizontalAdvance(self.floating_text)
                    text_height = font_metrics.height()
                    text_rect = QRect(
                        self.floating_text_pos.x(),
                        self.floating_text_pos.y(),
                        text_width // self.scale + 1,
                        text_height // self.scale + 1
                    )
                    if text_rect.contains(x, y):
                        self.is_dragging_text = True
                        self.last_pos = QPoint(x, y)
                        print("Начато перетаскивание текста")
                    else:
                        self.save_state()
                        self.draw_text_at_position(self.floating_text_pos.x(), self.floating_text_pos.y(), self.floating_text)
                        self.floating_text = None
                        self.floating_text_pos = None
                        self.is_dragging_text = False
                        print("Текст зафиксирован при повторном нажатии мыши")
                except Exception as e:
                    print(f"Ошибка при обработке текста: {e}")
                    self.save_state()
                    self.draw_text_at_position(self.floating_text_pos.x(), self.floating_text_pos.y(), self.floating_text)
                    self.floating_text = None
                    self.floating_text_pos = None
                    self.is_dragging_text = False
            elif event.button() == Qt.RightButton:
                self.floating_text = None
                self.floating_text_pos = None
                self.is_dragging_text = False
                print("Ввод текста отменен")
            self.update()
            return
        self.save_state()
        is_right_click = event.button() == Qt.RightButton
        if is_right_click and self.current_tool != "eraser":
            self.eraser_mode = True
        if self.current_tool == "pen" or self.current_tool == "eraser":
            self.drawing = True
            self.last_pos = QPoint(x, y)
            self.draw_pixel(x, y)
        elif self.current_tool == "rectangle":
            self.drawing = True
            self.selection_start = QPoint(x, y)
            self.selection = QRect(x, y, 1, 1)
        elif self.current_tool == "select":
            self.drawing = True
            if self.selection and self.selection.contains(x, y):
                print("Начало перемещения выделения")
                self.last_pos = QPoint(x, y)
                if not self.selection_image:
                    self.selection_image = self.image.copy(self.selection)
            else:
                print("Начало нового выделения")
                self.selection_start = QPoint(x, y)
                self.selection = QRect(x, y, 1, 1)
                self.selection_image = None
        elif self.current_tool == "fill":
            self.fill(x, y)
        elif self.current_tool == "eyedropper":
            if 0 <= x < self.width and 0 <= y < self.height:
                try:
                    color = self.image.pixelColor(x, y)
                    print(f"Пипетка: получен цвет {color.name()} в точке ({x}, {y})")
                    self.current_color = color
                    main_window = self.window()
                    if main_window and hasattr(main_window, "tool_panel"):
                        main_window.tool_panel.color_palette.set_current_color(color)
                        print(f"Пипетка: цвет {color.name()} установлен в палитре")
                except Exception as e:
                    print(f"Ошибка в инструменте пипетка: {e}")
        elif self.current_tool == "line":
            self.drawing = True
            self.line_start = QPoint(x, y)
            self.last_pos = QPoint(x, y)
        elif self.current_tool == "text":
            if not self.floating_text:
                try:
                    if self.choose_font():
                        text, ok = QInputDialog.getText(self, "Ввод текста", "Введите текст:")
                        if ok and text:
                            self.floating_text = text
                            self.floating_text_pos = QPoint(x, y)
                            print(f"Создан плавающий текст: '{text}' в позиции ({x}, {y})")
                except Exception as e:
                    print(f"Ошибка при вводе текста: {e}")
        self.update()
    def mouseMoveEvent(self, event):
        ruler_offset = self.ruler_size if self.show_rulers else 0
        x = int((event.position().x() - ruler_offset) / self.scale)
        y = int((event.position().y() - ruler_offset) / self.scale)
        if self.creating_guide and self.active_guide_index >= 0:
            if self.guide_orientation == 'horizontal':
                y = max(0, min(self.height - 1, y))
                self.guides[self.active_guide_index] = ('horizontal', y)
            elif self.guide_orientation == 'vertical':
                x = max(0, min(self.width - 1, x))
                self.guides[self.active_guide_index] = ('vertical', x)
            self.update()
            return
        self.position_changed.emit(x, y)
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if self.is_dragging_text and self.floating_text and self.last_pos:
            dx = x - self.last_pos.x()
            dy = y - self.last_pos.y()
            if dx != 0 or dy != 0:
                try:
                    font_metrics = QFontMetrics(self.text_font)
                    text_width = font_metrics.horizontalAdvance(self.floating_text) // self.scale
                    text_height = font_metrics.height() // self.scale
                    new_x = max(0, min(self.width - text_width, self.floating_text_pos.x() + dx))
                    new_y = max(0, min(self.height - text_height, self.floating_text_pos.y() + dy))
                    self.floating_text_pos = QPoint(new_x, new_y)
                    self.last_pos = QPoint(x, y)
                except Exception as e:
                    print(f"Ошибка при перемещении текста: {e}")
                    self.floating_text_pos = QPoint(x, y)
                    self.last_pos = QPoint(x, y)
                self.update()
            return
        if self.floating_text and not self.is_dragging_text:
            self.floating_text_pos = QPoint(x, y)
            self.update()
            return
        modifiers = QApplication.keyboardModifiers()
        temp_eraser_mode = modifiers & Qt.AltModifier
        if temp_eraser_mode and self.current_tool != "eraser":
            old_eraser_mode = self.eraser_mode
            self.eraser_mode = True
            if self.drawing and self.last_pos and self.current_tool == "pen":
                self.draw_line(self.last_pos.x(), self.last_pos.y(), x, y)
                self.last_pos = QPoint(x, y)
                self.update()
            self.eraser_mode = old_eraser_mode
            return
        if self.drawing and (self.current_tool == "pen" or self.current_tool == "eraser"):
            if self.last_pos:
                self.draw_line(self.last_pos.x(), self.last_pos.y(), x, y)
            self.last_pos = QPoint(x, y)
        elif self.drawing and self.current_tool == "rectangle":
            self.selection = QRect(
                min(self.selection_start.x(), x),
                min(self.selection_start.y(), y),
                abs(x - self.selection_start.x()) + 1,
                abs(y - self.selection_start.y()) + 1
            )
            self.update()
        elif self.drawing and self.current_tool == "select":
            if self.selection_start:  
                self.selection = QRect(
                    min(self.selection_start.x(), x),
                    min(self.selection_start.y(), y),
                    abs(x - self.selection_start.x()) + 1,
                    abs(y - self.selection_start.y()) + 1
                )
                print(f"Обновление выделения: {self.selection}")
            elif self.last_pos and self.selection and self.selection_image:  
                dx = x - self.last_pos.x()
                dy = y - self.last_pos.y()
                if dx != 0 or dy != 0:
                    new_left = max(0, min(self.width - self.selection.width(), self.selection.left() + dx))
                    new_top = max(0, min(self.height - self.selection.height(), self.selection.top() + dy))
                    self.selection.moveTopLeft(QPoint(new_left, new_top))
                    self.last_pos = QPoint(x, y)
                    print(f"Перемещение выделения на ({dx}, {dy})")
            self.update()
        elif self.drawing and self.current_tool == "line":
            self.last_pos = QPoint(x, y)
            self.update()
    def mouseReleaseEvent(self, event):
        if self.creating_guide:
            self.creating_guide = False
            self.active_guide_index = -1
            return
        if self.is_dragging_text:
            self.is_dragging_text = False
            self.update()
            return
        if not self.drawing:
            return
        ruler_offset = self.ruler_size if self.show_rulers else 0
        x = int((event.position().x() - ruler_offset) / self.scale)
        y = int((event.position().y() - ruler_offset) / self.scale)
        if self.current_tool == "rectangle" and self.selection:
            if event.modifiers() & Qt.ShiftModifier:
                size = max(self.selection.width(), self.selection.height())
                self.selection = QRect(self.selection.x(), self.selection.y(), size, size)
            self.draw_rectangle(self.selection)
            self.selection = None
        elif self.current_tool == "select" and self.selection:
            if self.selection.width() <= 1 and self.selection.height() <= 1:
                self.selection = None
                self.selection_image = None
                print("Выделение отменено (слишком маленькое)")
            else:
                if self.selection_start:
                    self.selection_image = self.image.copy(self.selection)
                    self.selection_start = None
                    print(f"Выделение завершено: {self.selection}")
        elif self.current_tool == "line" and self.line_start:
            self.draw_line_tool(self.line_start.x(), self.line_start.y(), x, y)
            self.line_start = None
        if event.button() == Qt.RightButton and self.current_tool != "eraser":
            self.eraser_mode = False
        self.drawing = False
        self.last_pos = None
        self.canvas_changed.emit()
        self.update()
    def keyPressEvent(self, event):
        key = event.key()
        if self.floating_text:
            if key == Qt.Key_Escape:
                self.floating_text = None
                self.floating_text_pos = None
                self.is_dragging_text = False
                self.update()
                return
            elif key == Qt.Key_Return or key == Qt.Key_Enter:
                self.save_state()
                self.draw_text_at_position(self.floating_text_pos.x(), self.floating_text_pos.y(), self.floating_text)
                self.floating_text = None
                self.floating_text_pos = None
                self.is_dragging_text = False
                self.update()
                return
        if key == Qt.Key_Alt and self.current_tool != "eraser":
            self.eraser_mode = True
            self.update()
            return
        if self.selection and self.selection_image:
            if key == Qt.Key_R and event.modifiers() & Qt.ControlModifier:
                self.rotate_selection(90)
                return
            elif key == Qt.Key_R and event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
                self.rotate_selection(-90)
                return
            elif key == Qt.Key_H and event.modifiers() & Qt.ControlModifier:
                self.flip_selection_horizontal()
                return
            elif key == Qt.Key_V and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
                self.flip_selection_vertical()
                return
            elif key == Qt.Key_Plus and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
                self.scale_selection(1.2, 1.2)
                return
            elif key == Qt.Key_Minus and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
                self.scale_selection(0.8, 0.8)
                return
        if self.selection:
            if key == Qt.Key_Delete or key == Qt.Key_Backspace:
                self.delete_selection()
            elif key == Qt.Key_Escape:
                self.reset_selection()
        if event.modifiers() & Qt.ControlModifier:
            if key == Qt.Key_C:
                self.copy_selection()
            elif key == Qt.Key_V:
                self.paste()
            elif key == Qt.Key_A:
                self.select_all()
            elif key == Qt.Key_Z:
                if event.modifiers() & Qt.ShiftModifier:
                    self.redo()
                else:
                    self.undo()
            elif key == Qt.Key_Plus:
                self.zoom_in()
            elif key == Qt.Key_Minus:
                self.zoom_out()
        event.accept()
    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_Alt and self.current_tool != "eraser":
            self.eraser_mode = False
            self.update()
        event.accept()
    def draw_pixel(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        color = Qt.white if self.eraser_mode else self.current_color
        self.image.setPixelColor(x, y, color)
        self.update()
    def draw_line(self, x1, y1, x2, y2):
        color = Qt.white if self.eraser_mode else self.current_color
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            if x1 >= 0 and x1 < self.width and y1 >= 0 and y1 < self.height:
                self.image.setPixelColor(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        self.update()
    def draw_rectangle(self, rect):
        color = Qt.white if self.eraser_mode else self.current_color
        x1 = max(0, rect.left())
        y1 = max(0, rect.top())
        x2 = min(self.width - 1, rect.right())
        y2 = min(self.height - 1, rect.bottom())
        for x in range(x1, x2 + 1):
            self.image.setPixelColor(x, y1, color)
            self.image.setPixelColor(x, y2, color)
        for y in range(y1 + 1, y2):
            self.image.setPixelColor(x1, y, color)
            self.image.setPixelColor(x2, y, color)
        self.update()
    def fill_rectangle(self, rect):
        color = Qt.white if self.eraser_mode else self.current_color
        x1 = max(0, rect.left())
        y1 = max(0, rect.top())
        x2 = min(self.width - 1, rect.right())
        y2 = min(self.height - 1, rect.bottom())
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.image.setPixelColor(x, y, color)
        self.update()
    def select_all(self):
        self.selection = QRect(0, 0, self.width, self.height)
        self.selection_image = self.image.copy()
        self.update()
    def reset_selection(self):
        self.selection = None
        self.selection_image = None
        self.selection_start = None
        self.update()
        print("Выделение сброшено")
    def delete_selection(self):
        if not self.selection:
            return
        self.save_state()
        painter = QPainter(self.image)
        painter.fillRect(self.selection, Qt.white)
        painter.end()
        self.selection = None
        self.selection_image = None
        self.update()
        self.canvas_changed.emit()
        print("Выделение удалено")
    def copy_selection(self):
        if not self.selection:
            return
        if not self.selection_image:
            self.selection_image = self.image.copy(self.selection)
        clipboard = QApplication.clipboard()
        clipboard.setImage(self.selection_image)
        print("Выделение скопировано в буфер обмена")
    def paste(self):
        clipboard = QApplication.clipboard()
        clipboard_image = clipboard.image()
        if clipboard_image.isNull():
            print("Буфер обмена пуст или не содержит изображения")
            return
        self.save_state()
        self.selection = QRect(0, 0, 
                              min(clipboard_image.width(), self.width), 
                              min(clipboard_image.height(), self.height))
        self.selection_image = clipboard_image
        print(f"Изображение вставлено из буфера обмена ({clipboard_image.width()}x{clipboard_image.height()})")
        self.update()
    def move_selection(self, dx, dy):
        if not self.selection or not self.selection_image:
            return
        self.save_state()
        painter = QPainter(self.image)
        painter.fillRect(self.selection, Qt.white)
        new_left = max(0, min(self.width - self.selection.width(), self.selection.left() + dx))
        new_top = max(0, min(self.height - self.selection.height(), self.selection.top() + dy))
        self.selection.moveTopLeft(QPoint(new_left, new_top))
        painter.drawImage(self.selection.topLeft(), self.selection_image)
        painter.end()
        self.update()
        self.canvas_changed.emit()
        print(f"Выделение перемещено на ({dx}, {dy})")
    def get_image(self):
        return self.image
    def set_image(self, image):
        if isinstance(image, QImage):
            self.image = image
        else:
            self.image = QImage(image)
        self.width = self.image.width()
        self.height = self.image.height()
        self.update_size()
        self.canvas_changed.emit()
    def load_image(self, file_path):
        if not os.path.exists(file_path):
            return False
        try:
            pil_image = Image.open(file_path)
            if pil_image.mode != "RGBA":
                pil_image = pil_image.convert("RGBA")
            img_data = pil_image.tobytes("raw", "RGBA")
            qimage = QImage(img_data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
            self.set_image(qimage)
            return True
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return False
    def save_image(self, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
            return self.image.save(file_path)
        elif file_ext in ['.pbm', '.tga', '.ico']:
            try:
                buffer = self.image.bits().asstring(self.image.byteCount())
                pil_image = Image.frombuffer(
                    "RGBA", 
                    (self.image.width(), self.image.height()), 
                    buffer, 
                    'raw', 
                    'BGRA', 
                    0, 
                    1
                )
                pil_image.save(file_path)
                return True
            except Exception as e:
                print(f"Ошибка сохранения изображения: {e}")
                return False
        else:
            return self.image.save(file_path)
    def export_image(self, file_path, scale=1):
        if scale <= 0:
            scale = 1
        scaled_width = self.width * scale
        scaled_height = self.height * scale
        scaled_image = QImage(scaled_width, scaled_height, QImage.Format_ARGB32)
        scaled_image.fill(Qt.white)
        painter = QPainter(scaled_image)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        for y in range(self.height):
            for x in range(self.width):
                color = self.image.pixelColor(x, y)
                if color != Qt.white:  
                    painter.fillRect(x * scale, y * scale, scale, scale, color)
        painter.end()
        return self.save_image_with_format(scaled_image, file_path)
    def save_image_with_format(self, image, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
            return image.save(file_path)
        elif file_ext in ['.pbm', '.tga', '.ico']:
            try:
                buffer = image.bits().asstring(image.byteCount())
                pil_image = Image.frombuffer(
                    "RGBA", 
                    (image.width(), image.height()), 
                    buffer, 
                    'raw', 
                    'BGRA', 
                    0, 
                    1
                )
                pil_image.save(file_path)
                return True
            except Exception as e:
                print(f"Ошибка сохранения изображения: {e}")
                return False
        else:
            return image.save(file_path)
    def fill(self, x, y):
        print(f"Canvas: заливка в точке ({x}, {y})")
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        target_color = self.image.pixelColor(x, y)
        fill_color = Qt.white if self.eraser_mode else self.current_color
        if target_color == fill_color:
            return
        queue = [(x, y)]
        visited = set()
        while queue:
            px, py = queue.pop(0)
            if (px < 0 or px >= self.width or py < 0 or py >= self.height or
                (px, py) in visited):
                continue
            if self.image.pixelColor(px, py) != target_color:
                continue
            self.image.setPixelColor(px, py, fill_color)
            visited.add((px, py))
            queue.append((px + 1, py))
            queue.append((px - 1, py))
            queue.append((px, py + 1))
            queue.append((px, py - 1))
        self.update()
        self.canvas_changed.emit()
    def draw_line_tool(self, x1, y1, x2, y2):
        print(f"Canvas: рисование линии от ({x1}, {y1}) до ({x2}, {y2})")
        color = Qt.white if self.eraser_mode else self.current_color
        self.draw_line(x1, y1, x2, y2)
        self.update()
        self.canvas_changed.emit()
    def draw_text_at_position(self, x, y, text):
        print(f"Canvas: рисование текста '{text}' в точке ({x}, {y})")
        if not text:
            return
        color = Qt.white if self.eraser_mode else self.current_color
        try:
            self.save_state()
            painter = QPainter(self.image)
            painter.setPen(color)
            try:
                painter.setFont(self.text_font)  
                font_metrics = painter.fontMetrics()
                painter.drawText(x, y + font_metrics.ascent(), text)
            except Exception as e:
                print(f"Ошибка при установке шрифта: {e}")
                painter.drawText(x, y + 8, text)
            finally:
                painter.end()
            self.update()
            self.canvas_changed.emit()
        except Exception as e:
            print(f"Ошибка при рисовании текста: {e}")
    def choose_font(self):
        current_font = self.text_font
        font, ok = QFontDialog.getFont(current_font, self, "Выбор шрифта")
        if ok:
            self.text_font = font
            return True
        return False
    def set_text_font(self, font):
        self.text_font = font
        self.update()
    def set_rulers_visible(self, visible):
        self.show_rulers = visible
        self.update_size()
        self.update()
    def add_guide(self, orientation, position):
        self.guides.append((orientation, position))
        self.update()
    def remove_guide(self, index):
        if 0 <= index < len(self.guides):
            del self.guides[index]
            self.update()
    def clear_guides(self):
        self.guides = []
        self.update()
    def flip_selection_horizontal(self):
        if not self.selection or not self.selection_image:
            return
        self.save_state()
        mirrored = self.selection_image.mirrored(True, False)
        painter = QPainter(self.image)
        painter.fillRect(self.selection, Qt.white)
        painter.drawImage(self.selection.topLeft(), mirrored)
        painter.end()
        self.selection_image = mirrored
        self.update()
        self.canvas_changed.emit()
        print("Выделение отражено по горизонтали")
    def flip_selection_vertical(self):
        if not self.selection or not self.selection_image:
            return
        self.save_state()
        mirrored = self.selection_image.mirrored(False, True)
        painter = QPainter(self.image)
        painter.fillRect(self.selection, Qt.white)
        painter.drawImage(self.selection.topLeft(), mirrored)
        painter.end()
        self.selection_image = mirrored
        self.update()
        self.canvas_changed.emit()
        print("Выделение отражено по вертикали")
    def rotate_selection(self, angle):
        if not self.selection or not self.selection_image:
            return
        self.save_state()
        transform = QTransform()
        center_x = self.selection_image.width() / 2
        center_y = self.selection_image.height() / 2
        transform.translate(center_x, center_y)
        transform.rotate(angle)
        transform.translate(-center_x, -center_y)
        rotated = self.selection_image.transformed(transform, Qt.SmoothTransformation)
        if rotated.width() != self.selection.width() or rotated.height() != self.selection.height():
            new_width = rotated.width()
            new_height = rotated.height()
            new_x = self.selection.x() - (new_width - self.selection.width()) // 2
            new_y = self.selection.y() - (new_height - self.selection.height()) // 2
            new_x = max(0, min(self.width - new_width, new_x))
            new_y = max(0, min(self.height - new_height, new_y))
            self.selection = QRect(new_x, new_y, new_width, new_height)
        painter = QPainter(self.image)
        painter.fillRect(self.selection, Qt.white)
        painter.drawImage(self.selection.topLeft(), rotated)
        painter.end()
        self.selection_image = rotated
        self.update()
        self.canvas_changed.emit()
        print(f"Выделение повернуто на {angle} градусов")
    def scale_selection(self, scale_x, scale_y):
        if not self.selection or not self.selection_image:
            return
        self.save_state()
        new_width = int(self.selection.width() * scale_x)
        new_height = int(self.selection.height() * scale_y)
        if new_width <= 0 or new_height <= 0 or \
           self.selection.x() + new_width > self.width or \
           self.selection.y() + new_height > self.height:
            print("Ошибка масштабирования: выход за границы холста")
            return
        scaled = self.selection_image.scaled(
            new_width, new_height, 
            Qt.KeepAspectRatio if scale_x == scale_y else Qt.IgnoreAspectRatio, 
            Qt.FastTransformation
        )
        painter = QPainter(self.image)
        painter.fillRect(self.selection, Qt.white)
        self.selection = QRect(self.selection.x(), self.selection.y(), new_width, new_height)
        painter.drawImage(self.selection.topLeft(), scaled)
        painter.end()
        self.selection_image = scaled
        self.update()
        self.canvas_changed.emit()
        print(f"Выделение масштабировано ({scale_x}x, {scale_y}y)")