import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QFrame, QSlider, QComboBox,
    QMenu, QInputDialog, QMessageBox, QSizePolicy, QScrollArea
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QImage, QPixmap, QIcon, QFont,
    QBrush, QPainterPath
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint
from enum import Enum
import os

# -----------------------------------------------------------------------------
# Режимы наложения
# -----------------------------------------------------------------------------
class BlendMode(Enum):
    NORMAL = "Normal"
    MULTIPLY = "Multiply"
    SCREEN = "Screen"
    OVERLAY = "Overlay"
    DARKEN = "Darken"
    LIGHTEN = "Lighten"
    COLOR_DODGE = "Color Dodge"
    COLOR_BURN = "Color Burn"
    HARD_LIGHT = "Hard Light"
    SOFT_LIGHT = "Soft Light"
    DIFFERENCE = "Difference"
    EXCLUSION = "Exclusion"

    def to_composition_mode(self):
        mapping = {
            BlendMode.NORMAL: QPainter.CompositionMode.CompositionMode_SourceOver,
            BlendMode.MULTIPLY: QPainter.CompositionMode.CompositionMode_Multiply,
            BlendMode.SCREEN: QPainter.CompositionMode.CompositionMode_Screen,
            BlendMode.OVERLAY: QPainter.CompositionMode.CompositionMode_Overlay,
            BlendMode.DARKEN: QPainter.CompositionMode.CompositionMode_Darken,
            BlendMode.LIGHTEN: QPainter.CompositionMode.CompositionMode_Lighten,
            BlendMode.COLOR_DODGE: QPainter.CompositionMode.CompositionMode_ColorDodge,
            BlendMode.COLOR_BURN: QPainter.CompositionMode.CompositionMode_ColorBurn,
            BlendMode.HARD_LIGHT: QPainter.CompositionMode.CompositionMode_HardLight,
            BlendMode.SOFT_LIGHT: QPainter.CompositionMode.CompositionMode_SoftLight,
            BlendMode.DIFFERENCE: QPainter.CompositionMode.CompositionMode_Difference,
            BlendMode.EXCLUSION: QPainter.CompositionMode.CompositionMode_Exclusion,
        }
        return mapping.get(self, QPainter.CompositionMode.CompositionMode_SourceOver)


# -----------------------------------------------------------------------------
# Класс слоя
# -----------------------------------------------------------------------------
class Layer:
    def __init__(self, name="Layer", width=1280, height=720):
        self.name = name
        self.image = QImage(width, height, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.transparent)
        self.visible = True
        self.locked = False
        self.opacity = 1.0
        self.blend_mode = BlendMode.NORMAL
        self.is_group = False
        self.parent_group = None
        self.children = []
        
    def copy(self):
        new_layer = Layer(self.name + " copy", self.image.width(), self.image.height())
        new_layer.image = self.image.copy()
        new_layer.visible = self.visible
        new_layer.locked = self.locked
        new_layer.opacity = self.opacity
        new_layer.blend_mode = self.blend_mode
        return new_layer
    
    def create_thumbnail(self, size=64):
        """Создает миниатюру слоя с шахматным фоном"""
        thumb = QImage(size, size, QImage.Format.Format_ARGB32)
        
        # Рисуем шахматный фон
        painter = QPainter(thumb)
        tile_size = size // 4
        for y in range(0, size, tile_size):
            for x in range(0, size, tile_size):
                if (x // tile_size + y // tile_size) % 2 == 0:
                    painter.fillRect(x, y, tile_size, tile_size, QColor(200, 200, 200))
                else:
                    painter.fillRect(x, y, tile_size, tile_size, QColor(255, 255, 255))
        
        # Рисуем миниатюру изображения
        scaled = self.image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
        painter.drawImage(0, 0, scaled)
        painter.end()
        
        return QPixmap.fromImage(thumb)


# -----------------------------------------------------------------------------
# Панель слоев (Photoshop-style)
# -----------------------------------------------------------------------------
class LayersPanel(QWidget):
    layer_selected = pyqtSignal(int)
    layer_visibility_changed = pyqtSignal(int, bool)
    layer_added = pyqtSignal()
    layer_removed = pyqtSignal(int)
    layer_moved = pyqtSignal(int, int)
    layer_merged = pyqtSignal()
    refresh_canvas = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.current_layer_index = -1
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Заголовок
        header = QLabel("СЛОИ")
        header.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                background-color: #3c3c3c;
                border-radius: 4px;
            }
        """)
        layout.addWidget(header)
        
        # Список слоев
        self.layers_list = QListWidget()
        self.layers_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 2px;
                outline: none;
            }
            QListWidget::item {
                background-color: #333;
                border: 1px solid #444;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
                min-height: 64px;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
                border: 1px solid #5a9ae9;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        self.layers_list.setIconSize(QSize(56, 56))
        self.layers_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.layers_list.currentRowChanged.connect(self.on_layer_selected)
        self.layers_list.model().rowsMoved.connect(self.on_layers_reordered)
        layout.addWidget(self.layers_list)
        
        # Кнопки управления слоями
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(2)
        
        buttons_data = [
            ("➕", "Добавить слой", self.add_layer),
            ("➖", "Удалить слой", self.remove_current_layer),
            ("📋", "Дублировать слой", self.duplicate_layer),
            ("🔽", "Объединить с выделенным", self.merge_down),
            ("⬆", "Переместить вверх", self.move_layer_up),
            ("⬇", "Переместить вниз", self.move_layer_down),
        ]
        
        for text, tooltip, callback in buttons_data:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setFixedSize(32, 32)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    border: 1px solid #555;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QPushButton:pressed {
                    background-color: #666;
                }
            """)
            buttons_layout.addWidget(btn)
        
        layout.addLayout(buttons_layout)
        
        # Настройки слоя
        settings_group = QFrame()
        settings_group.setStyleSheet("""
            QFrame {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: #ccc;
                font-size: 11px;
            }
            QComboBox {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 4px;
                background: #444;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4a90d9;
                border: none;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(4)
        
        # Непрозрачность
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Непрозрачность:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.opacity_label = QLabel("100%")
        self.opacity_label.setFixedWidth(35)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        settings_layout.addLayout(opacity_layout)
        
        # Режим наложения
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("Режим:"))
        self.blend_combo = QComboBox()
        for mode in BlendMode:
            self.blend_combo.addItem(mode.value)
        self.blend_combo.currentTextChanged.connect(self.change_blend_mode)
        blend_layout.addWidget(self.blend_combo)
        settings_layout.addLayout(blend_layout)
        
        # Блокировка слоя
        self.lock_button = QPushButton("🔒 Заблокировать")
        self.lock_button.setCheckable(True)
        self.lock_button.clicked.connect(self.toggle_lock)
        self.lock_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px;
                color: #ccc;
                font-size: 11px;
            }
            QPushButton:checked {
                background-color: #d94a4a;
                border-color: #e95a5a;
            }
        """)
        settings_layout.addWidget(self.lock_button)
        
        layout.addWidget(settings_group)
        
        # Контекстное меню
        self.layers_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.layers_list.customContextMenuRequested.connect(self.show_context_menu)
    
    def add_layer(self, name=None, image=None):
        """Добавляет новый слой"""
        if name is None:
            name = f"Слой {len(self.layers) + 1}"
        
        # Определяем размеры из существующих слоев или используем размер холста
        width = 1280
        height = 720
        if self.layers:
            width = self.layers[0].image.width()
            height = self.layers[0].image.height()
        
        new_layer = Layer(name, width, height)
        
        if image:
            new_layer.image = image
        
        # Добавляем слой в начало списка (поверх всех)
        self.layers.insert(0, new_layer)
        self.current_layer_index = 0
        
        self.refresh_list()
        self.layers_list.setCurrentRow(0)
        self.layer_added.emit()
        self.refresh_canvas.emit()
    
    def remove_current_layer(self):
        """Удаляет текущий слой"""
        if len(self.layers) <= 1:
            QMessageBox.warning(self, "Предупреждение", "Нельзя удалить последний слой!")
            return
        
        if self.current_layer_index >= 0:
            # Проверяем, не заблокирован ли слой
            if self.layers[self.current_layer_index].locked:
                QMessageBox.warning(self, "Предупреждение", "Слой заблокирован!")
                return
            
            removed_index = self.current_layer_index
            self.layers.pop(removed_index)
            
            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = len(self.layers) - 1
            
            self.refresh_list()
            self.layers_list.setCurrentRow(self.current_layer_index)
            self.layer_removed.emit(removed_index)
            self.refresh_canvas.emit()
    
    def duplicate_layer(self):
        """Дублирует текущий слой"""
        if self.current_layer_index >= 0:
            current = self.layers[self.current_layer_index]
            new_layer = current.copy()
            self.layers.insert(self.current_layer_index, new_layer)
            self.current_layer_index += 1
            
            self.refresh_list()
            self.layers_list.setCurrentRow(self.current_layer_index)
            self.layer_added.emit()
            self.refresh_canvas.emit()
    
    def merge_down(self):
        """Объединяет текущий слой с нижележащим"""
        if self.current_layer_index < len(self.layers) - 1 and len(self.layers) > 1:
            current = self.layers[self.current_layer_index]
            below = self.layers[self.current_layer_index + 1]
            
            # Создаем новое изображение
            merged = QImage(below.image.size(), QImage.Format.Format_ARGB32)
            merged.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(merged)
            painter.drawImage(0, 0, below.image)
            painter.setOpacity(current.opacity)
            painter.setCompositionMode(current.blend_mode.to_composition_mode())
            painter.drawImage(0, 0, current.image)
            painter.end()
            
            below.image = merged
            below.name = current.name
            below.opacity = 1.0
            below.blend_mode = BlendMode.NORMAL
            
            self.layers.pop(self.current_layer_index)
            
            self.refresh_list()
            self.layers_list.setCurrentRow(self.current_layer_index)
            self.layer_merged.emit()
            self.refresh_canvas.emit()
    
    def move_layer_up(self):
        """Перемещает слой вверх в стеке"""
        if self.current_layer_index > 0:
            self.layers[self.current_layer_index], self.layers[self.current_layer_index - 1] = \
                self.layers[self.current_layer_index - 1], self.layers[self.current_layer_index]
            self.current_layer_index -= 1
            
            self.refresh_list()
            self.layers_list.setCurrentRow(self.current_layer_index)
            self.refresh_canvas.emit()
    
    def move_layer_down(self):
        """Перемещает слой вниз в стеке"""
        if self.current_layer_index < len(self.layers) - 1:
            self.layers[self.current_layer_index], self.layers[self.current_layer_index + 1] = \
                self.layers[self.current_layer_index + 1], self.layers[self.current_layer_index]
            self.current_layer_index += 1
            
            self.refresh_list()
            self.layers_list.setCurrentRow(self.current_layer_index)
            self.refresh_canvas.emit()
    
    def toggle_visibility(self, index):
        """Переключает видимость слоя"""
        if 0 <= index < len(self.layers):
            self.layers[index].visible = not self.layers[index].visible
            self.refresh_list()
            self.layer_visibility_changed.emit(index, self.layers[index].visible)
            self.refresh_canvas.emit()
    
    def toggle_lock(self):
        """Блокирует/разблокирует текущий слой"""
        if self.current_layer_index >= 0:
            layer = self.layers[self.current_layer_index]
            layer.locked = not layer.locked
            self.lock_button.setChecked(layer.locked)
            if layer.locked:
                self.lock_button.setText("🔓 Разблокировать")
            else:
                self.lock_button.setText("🔒 Заблокировать")
    
    def change_opacity(self, value):
        """Изменяет непрозрачность текущего слоя"""
        if self.current_layer_index >= 0:
            self.layers[self.current_layer_index].opacity = value / 100.0
            self.opacity_label.setText(f"{value}%")
            self.refresh_canvas.emit()
    
    def change_blend_mode(self, mode_name):
        """Изменяет режим наложения текущего слоя"""
        if self.current_layer_index >= 0:
            for mode in BlendMode:
                if mode.value == mode_name:
                    self.layers[self.current_layer_index].blend_mode = mode
                    break
            self.refresh_canvas.emit()
    
    def on_layer_selected(self, index):
        """Обработчик выбора слоя"""
        if index >= 0 and index < len(self.layers):
            self.current_layer_index = index
            self.layer_selected.emit(index)
            self.update_layer_settings()
    
    def on_layers_reordered(self, parent, start, end, dest, row):
        """Обработчик переупорядочивания слоев"""
        # Обновляем порядок слоев в списке
        moved_layer = self.layers.pop(start)
        if row > start:
            row -= 1
        self.layers.insert(row, moved_layer)
        self.current_layer_index = row
        self.refresh_list()
        self.refresh_canvas.emit()
    
    def update_layer_settings(self):
        """Обновляет настройки для текущего слоя"""
        if self.current_layer_index >= 0:
            layer = self.layers[self.current_layer_index]
            
            # Блокируем сигналы, чтобы избежать рекурсии
            self.opacity_slider.blockSignals(True)
            self.blend_combo.blockSignals(True)
            
            self.opacity_slider.setValue(int(layer.opacity * 100))
            self.opacity_label.setText(f"{int(layer.opacity * 100)}%")
            
            index = self.blend_combo.findText(layer.blend_mode.value)
            if index >= 0:
                self.blend_combo.setCurrentIndex(index)
            
            self.lock_button.setChecked(layer.locked)
            if layer.locked:
                self.lock_button.setText("🔓 Разблокировать")
            else:
                self.lock_button.setText("🔒 Заблокировать")
            
            self.opacity_slider.blockSignals(False)
            self.blend_combo.blockSignals(False)
    
    def refresh_list(self):
        """Обновляет отображение списка слоев"""
        self.layers_list.clear()
        
        for i, layer in enumerate(self.layers):
            # Создаем виджет для элемента списка
            widget = QWidget()
            widget_layout = QHBoxLayout(widget)
            widget_layout.setContentsMargins(2, 2, 2, 2)
            widget_layout.setSpacing(4)
            
            # Миниатюра слоя
            thumb_label = QLabel()
            thumb_label.setFixedSize(56, 56)
            thumb_label.setPixmap(layer.create_thumbnail(56))
            thumb_label.setStyleSheet("border: 1px solid #555; border-radius: 2px;")
            widget_layout.addWidget(thumb_label)
            
            # Информация о слое
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            
            # Имя слоя
            name_label = QLabel(layer.name)
            name_label.setStyleSheet(f"""
                QLabel {{
                    color: {'#4a90d9' if i == self.current_layer_index else '#ccc'};
                    font-weight: {'bold' if i == self.current_layer_index else 'normal'};
                    font-size: 12px;
                }}
            """)
            info_layout.addWidget(name_label)
            
            # Кнопки управления
            control_layout = QHBoxLayout()
            control_layout.setSpacing(2)
            
            # Видимость
            visibility_btn = QPushButton("👁" if layer.visible else "👁‍🗨")
            visibility_btn.setFixedSize(24, 24)
            visibility_btn.setToolTip("Показать/скрыть слой")
            visibility_btn.clicked.connect(lambda checked, idx=i: self.toggle_visibility(idx))
            visibility_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #555;
                    border-radius: 2px;
                }
            """)
            control_layout.addWidget(visibility_btn)
            
            # Тип слоя
            type_label = QLabel("🖼")
            type_label.setToolTip("Растровый слой")
            control_layout.addWidget(type_label)
            
            info_layout.addLayout(control_layout)
            widget_layout.addLayout(info_layout)
            
            # Создаем элемент списка
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 64))
            
            self.layers_list.addItem(item)
            self.layers_list.setItemWidget(item, widget)
    
    def show_context_menu(self, position):
        """Показывает контекстное меню для слоев"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 4px 20px;
                border-radius: 2px;
                color: #ccc;
            }
            QMenu::item:selected {
                background-color: #4a90d9;
            }
        """)
        
        menu.addAction("Добавить слой", self.add_layer)
        menu.addAction("Дублировать слой", self.duplicate_layer)
        menu.addAction("Удалить слой", self.remove_current_layer)
        menu.addSeparator()
        menu.addAction("Объединить с нижним", self.merge_down)
        menu.addAction("Объединить видимые", self.merge_visible)
        menu.addSeparator()
        menu.addAction("Растрировать слой", lambda: None)
        menu.addAction("Создать обтравочную маску", lambda: None)
        
        menu.exec(self.layers_list.mapToGlobal(position))
    
    def merge_visible(self):
        """Объединяет все видимые слои"""
        if not self.layers:
            return
        
        # Находим первый видимый слой
        first_visible = None
        visible_indices = []
        
        for i, layer in enumerate(self.layers):
            if layer.visible:
                if first_visible is None:
                    first_visible = i
                visible_indices.append(i)
        
        if len(visible_indices) < 2:
            return
        
        # Создаем объединенное изображение
        merged = QImage(self.layers[0].image.size(), QImage.Format.Format_ARGB32)
        merged.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(merged)
        for i in reversed(visible_indices):  # Снизу вверх
            layer = self.layers[i]
            painter.setOpacity(layer.opacity)
            painter.setCompositionMode(layer.blend_mode.to_composition_mode())
            painter.drawImage(0, 0, layer.image)
        painter.end()
        
        # Заменяем первый видимый слой объединенным
        self.layers[first_visible].image = merged
        self.layers[first_visible].name = "Объединенный слой"
        self.layers[first_visible].opacity = 1.0
        self.layers[first_visible].blend_mode = BlendMode.NORMAL
        
        # Удаляем остальные видимые слои (в обратном порядке)
        for i in reversed(visible_indices[1:]):
            self.layers.pop(i)
        
        self.current_layer_index = min(first_visible, len(self.layers) - 1)
        self.refresh_list()
        self.layers_list.setCurrentRow(self.current_layer_index)
        self.refresh_canvas.emit()
    
    def get_merged_image(self):
        """Возвращает объединенное изображение всех видимых слоев"""
        if not self.layers:
            return QImage(1280, 720, QImage.Format.Format_ARGB32)
        
        result = QImage(self.layers[0].image.size(), QImage.Format.Format_ARGB32)
        result.fill(Qt.GlobalColor.white)
        
        painter = QPainter(result)
        
        # Рисуем слои снизу вверх
        for layer in reversed(self.layers):
            if layer.visible:
                painter.setOpacity(layer.opacity)
                painter.setCompositionMode(layer.blend_mode.to_composition_mode())
                painter.drawImage(0, 0, layer.image)
        
        painter.end()
        return result
    
    def get_current_layer(self):
        """Возвращает текущий активный слой"""
        if self.current_layer_index >= 0 and self.current_layer_index < len(self.layers):
            return self.layers[self.current_layer_index]
        return None