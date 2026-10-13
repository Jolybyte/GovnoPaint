# paintApp.py
import sys
import os
import math
import random
from datetime import datetime
from functools import partial

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QColorDialog, QFileDialog, QComboBox, QLabel, QMenu, QScrollArea, QSlider,
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QCheckBox, QGroupBox,
    QSizePolicy, QStatusBar, QToolButton, QMessageBox, QButtonGroup,
    QListWidget, QListWidgetItem, QAbstractItemView, QDockWidget, QFrame
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QImage, QFont, QIcon, QPixmap, QShortcut,
    QKeySequence, QCursor, QAction, QLinearGradient, QRadialGradient,
    QConicalGradient, QBrush, QTransform, QPolygonF, QPainterPath
)
from PyQt6.QtCore import Qt, QPoint, QPointF, QSize, QTimer, QRectF, pyqtSignal

# Импорт внешних модулей
try:
    from flood_fill import FloodFill
    import qtawesome as qta
except ImportError as e:
    print(f"⚠️ Ошибка импорта: {e}")
    class DummyFloodFill:
        @staticmethod
        def flood_fill_numpy(img, pt, color): return img
    FloodFill = DummyFloodFill
    class qta:
        @staticmethod
        def icon(name, color='#000'): 
            return QIcon()

try:
    from custom_brushes import CUSTOM_BRUSHES, apply_brush
except ImportError:
    print("⚠️ custom_brushes.py не найден. Кастомные кисти недоступны.")
    CUSTOM_BRUSHES = {}
    apply_brush = None


# -----------------------------------------------------------------------------
# Класс слоя
# -----------------------------------------------------------------------------
class Layer:
    BLEND_MODES = {
        "Normal": QPainter.CompositionMode.CompositionMode_SourceOver,
        "Multiply": QPainter.CompositionMode.CompositionMode_Multiply,
        "Screen": QPainter.CompositionMode.CompositionMode_Screen,
        "Overlay": QPainter.CompositionMode.CompositionMode_Overlay,
        "Darken": QPainter.CompositionMode.CompositionMode_Darken,
        "Lighten": QPainter.CompositionMode.CompositionMode_Lighten,
        "Color Dodge": QPainter.CompositionMode.CompositionMode_ColorDodge,
        "Color Burn": QPainter.CompositionMode.CompositionMode_ColorBurn,
        "Hard Light": QPainter.CompositionMode.CompositionMode_HardLight,
        "Soft Light": QPainter.CompositionMode.CompositionMode_SoftLight,
        "Difference": QPainter.CompositionMode.CompositionMode_Difference,
        "Exclusion": QPainter.CompositionMode.CompositionMode_Exclusion,
    }

    def __init__(self, name="Layer", width=1280, height=720, fill=None):
        self.name = name
        self.image = QImage(width, height, QImage.Format.Format_ARGB32)
        if fill is not None:
            self.image.fill(fill)
        else:
            self.image.fill(Qt.GlobalColor.transparent)
        self.visible = True
        self.opacity = 100          # 0-100
        self.blend_mode = "Normal"
        self.locked_alpha = False
        self.locked_position = False
        self.locked_all = False

    def copy(self):
        new_layer = Layer(self.name)
        new_layer.image = self.image.copy()
        new_layer.visible = self.visible
        new_layer.opacity = self.opacity
        new_layer.blend_mode = self.blend_mode
        new_layer.locked_alpha = self.locked_alpha
        new_layer.locked_position = self.locked_position
        new_layer.locked_all = self.locked_all
        return new_layer

    def composition_mode(self):
        return Layer.BLEND_MODES.get(self.blend_mode, QPainter.CompositionMode.CompositionMode_SourceOver)


# -----------------------------------------------------------------------------
# Панель слоёв
# -----------------------------------------------------------------------------
class LayerPanel(QWidget):
    layer_selected = pyqtSignal(int)
    layer_visibility_changed = pyqtSignal(int, bool)
    layer_opacity_changed = pyqtSignal(int, int)
    layer_name_changed = pyqtSignal(int, str)
    move_layer_up = pyqtSignal(int)
    move_layer_down = pyqtSignal(int)

    def __init__(self, paint_widget):
        super().__init__()
        self.paint_widget = paint_widget
        self.setWindowTitle("Слои")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Заголовок
        title = QLabel("🎨 Слои")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 4px;")
        layout.addWidget(title)
        
        # Список слоёв
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
            }
        """)
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        self.list_widget.model().rowsMoved.connect(self.on_rows_moved)
        layout.addWidget(self.list_widget)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("＋")
        add_btn.setToolTip("Добавить слой")
        add_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        add_btn.clicked.connect(self.add_layer)
        
        del_btn = QPushButton("✕")
        del_btn.setToolTip("Удалить слой")
        del_btn.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        del_btn.clicked.connect(self.remove_layer)
        
        dup_btn = QPushButton("⧉")
        dup_btn.setToolTip("Дублировать слой")
        dup_btn.setStyleSheet("font-size: 16px;")
        dup_btn.clicked.connect(self.duplicate_layer)
        
        merge_btn = QPushButton("↓")
        merge_btn.setToolTip("Объединить с нижним")
        merge_btn.setStyleSheet("font-size: 16px;")
        merge_btn.clicked.connect(self.merge_down)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(dup_btn)
        btn_layout.addWidget(merge_btn)
        layout.addLayout(btn_layout)

        # Режим наложения
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("Режим:"))
        self.blend_combo = QComboBox()
        self.blend_combo.addItems(list(Layer.BLEND_MODES.keys()))
        self.blend_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        blend_layout.addWidget(self.blend_combo)
        layout.addLayout(blend_layout)

        self.update_ui()

    def update_ui(self):
        self.list_widget.blockSignals(True)
        current_row = self.list_widget.currentRow()
        self.list_widget.clear()
        
        for i, layer in enumerate(self.paint_widget.layers):
            item = QListWidgetItem()
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(4, 4, 4, 4)
            hbox.setSpacing(6)

            # Миниатюра
            thumb_label = QLabel()
            thumb = layer.image.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            thumb_label.setPixmap(QPixmap.fromImage(thumb))
            thumb_label.setFixedSize(40, 40)
            thumb_label.setStyleSheet("border: 1px solid #999;")
            hbox.addWidget(thumb_label)

            # Имя слоя
            name_label = QLabel(layer.name)
            name_label.setStyleSheet("font-size: 12px;")
            name_label.setFixedWidth(80)
            hbox.addWidget(name_label)

            # Видимость
            vis_check = QCheckBox()
            vis_check.setChecked(layer.visible)
            vis_check.setToolTip("Видимость слоя")
            vis_check.stateChanged.connect(lambda state, idx=i: self.toggle_visibility(idx, state))
            hbox.addWidget(vis_check)

            # Прозрачность
            opacity_slider = QSlider(Qt.Orientation.Horizontal)
            opacity_slider.setRange(0, 100)
            opacity_slider.setValue(layer.opacity)
            opacity_slider.setFixedWidth(60)
            opacity_slider.setToolTip("Прозрачность")
            opacity_slider.valueChanged.connect(lambda val, idx=i: self.change_opacity(idx, val))
            hbox.addWidget(opacity_slider)

            # Кнопки вверх/вниз
            up_btn = QPushButton("↑")
            up_btn.setFixedSize(24, 24)
            up_btn.setToolTip("Переместить вверх")
            up_btn.clicked.connect(lambda _, idx=i: self.move_layer_up.emit(idx))
            
            down_btn = QPushButton("↓")
            down_btn.setFixedSize(24, 24)
            down_btn.setToolTip("Переместить вниз")
            down_btn.clicked.connect(lambda _, idx=i: self.move_layer_down.emit(idx))
            
            hbox.addWidget(up_btn)
            hbox.addWidget(down_btn)

            widget.setLayout(hbox)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

        if 0 <= current_row < len(self.paint_widget.layers):
            self.list_widget.setCurrentRow(current_row)
        else:
            self.list_widget.setCurrentRow(self.paint_widget.current_layer)
        
        # Обновляем комбо режима наложения
        if self.paint_widget.active_layer:
            idx = self.blend_combo.findText(self.paint_widget.active_layer.blend_mode)
            if idx >= 0:
                self.blend_combo.blockSignals(True)
                self.blend_combo.setCurrentIndex(idx)
                self.blend_combo.blockSignals(False)
        
        self.list_widget.blockSignals(False)

    def toggle_visibility(self, index, state):
        if 0 <= index < len(self.paint_widget.layers):
            self.paint_widget.layers[index].visible = (state == Qt.CheckState.Checked.value)
            self.paint_widget.update()

    def change_opacity(self, index, value):
        if 0 <= index < len(self.paint_widget.layers):
            self.paint_widget.layers[index].opacity = value
            self.paint_widget.update()

    def on_blend_mode_changed(self, mode):
        if self.paint_widget.active_layer:
            self.paint_widget.active_layer.blend_mode = mode
            self.paint_widget.update()

    def on_selection_changed(self, row):
        if row >= 0 and row < len(self.paint_widget.layers):
            self.paint_widget.current_layer = row
            self.paint_widget.update()

    def on_rows_moved(self, parent, start, end, destination, row):
        layers = self.paint_widget.layers
        moved_layer = layers.pop(start)
        if row > start:
            row -= 1
        layers.insert(row, moved_layer)
        self.paint_widget.current_layer = row
        self.paint_widget.update()
        self.update_ui()

    def add_layer(self):
        self.paint_widget.add_layer()
        self.update_ui()

    def remove_layer(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.paint_widget.remove_layer(row)
            self.update_ui()

    def duplicate_layer(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.paint_widget.duplicate_layer(row)
            self.update_ui()

    def merge_down(self):
        if self.paint_widget.current_layer > 0:
            self.paint_widget.merge_down()
            self.update_ui()


# -----------------------------------------------------------------------------
# Виджет рисования
# -----------------------------------------------------------------------------
class PaintWidget(QWidget):
    def __init__(self, width=1280, height=720):
        super().__init__()
        self.canvas_width = width
        self.canvas_height = height

        # Слои
        self.layers = []
        self.current_layer = 0
        background = Layer("Background", width, height, Qt.GlobalColor.white)
        self.layers.append(background)

        self.drawing = False
        self.brush_color = QColor(Qt.GlobalColor.black)
        self.secondary_color = QColor(Qt.GlobalColor.white)
        self.brush_size = 2
        self.last_point = QPointF()
        self.tool = "pen"
        self.text = ""
        self.font = QFont("Arial", 16)
        self.undo_stack = []
        self.redo_stack = []
        self.brush_shape = "round"
        self.text_input_mode = False
        self.text_position = QPointF()
        self.antialiasing_enabled = True
        self.transparency_enabled = False
        self.pressure_sensitivity = False
        self.grid_enabled = False
        self.grid_size = 20
        self.flood_fill_tool = FloodFill()
        self.temp_image = None
        self.is_drawing_shape = False
        self.shape_start_point = QPointF()
        self.selection_rect = None
        self.is_selecting = False
        self.copied_selection = None
        self.gradient_type = "linear"
        self.symmetry_enabled = False
        self.symmetry_axes = 1
        self.cursor_circle = False
        self.brush_pressure = 1.0
        self.brush_spacing = 0.1
        self.brush_texture = None
        self.brush_opacity = 1.0
        self.snap_to_grid = False
        self.reference_image = None
        self.reference_opacity = 0.5
        self.zoom_factor = 1.0
        self.zoom_center = QPointF()
        self.ruler_enabled = False
        self.ruler_start = QPointF()
        self.ruler_end = QPointF()
        self.custom_shortcuts = {}
        self.brush_blend_mode = QPainter.CompositionMode.CompositionMode_SourceOver
        self.history_limit = 100

        # Выделение
        self.selection_tool = "rectangle"
        self.selection_mask = None
        self.is_moving_selection = False
        self.selection_offset = QPointF()
        self.selection_content = None
        self.lasso_points = []
        self.is_drawing_lasso = False

        self.auto_save_timer = QTimer(self)
        self.auto_save_interval = 300000
        self.auto_save_path = os.path.expanduser("~/.qtpaint_autosave")
        self.setMouseTracking(True)

        self.tool_brush_sizes = {
            "pen": 2, "eraser": 10, "line": 2, "rectangle": 2, "ellipse": 2,
            "text": 2, "fill": 2, "gradient": 2, "eyedropper": 1, "selection": 1,
            "calligraphy": 5, "fountain_pen": 3, "spray": 10, "oil_brush": 8,
            "colored_pencil": 2, "marker": 6, "texture_pencil": 2, "watercolor_brush": 10, 
            "sketching_pencil": 4, "hatching": 10, "gesture": 8,
            "concept_sketch": 6, "silhouette": 25, "speed_paint": 30,
            "manga_tone": 18, "comic_ink": 5, "screentone": 22,
            "calligraphy_nib": 14, "brush_pen": 10, "graffiti": 28,
            "digital_oil": 22, "impasto": 20, "palette_knife": 35,
            "blender": 28, "texture_stencil": 28, "glaze": 32,
            "perspective": 3, "grid_perspective": 55, "light_ray": 45,
            "splatter": 10, "glow": 20, "rainbow": 3, "fur": 8, "pixel": 10,
            "neon": 8, "ribbon": 8, "engraving": 3, "fire": 20, "smoke": 30, "bubbles": 10, "sparks": 8,
            "vine": 5, "grass": 8, "coral": 10, "furball": 15,
            "kaleidoscope": 5, "lightning": 3, "circuit": 3, "hexgrid": 12, "fractal": 8,
            "crumble": 15, "canvas": 20, "rust": 15,
            "emoji": 12, "ascii": 8, "morse": 5,
            "galaxy": 25, "constellation": 20,
            "rune": 15, "mana": 10, "phoenix": 18,
            "opart": 10, "moire": 15,
            "gravity": 12, "wind": 20, "magnet": 18, "soundwave": 35, "seismic": 45, "bass": 30,
            "cell": 25, "bacteria": 18, "neuron": 28, "dna": 25,
            "watercolor_wash": 35, "inkdrop": 28, "steam": 35,
            "brickwall": 22, "chain": 12, "scaffold": 35,
            "sprinkles": 12, "coffee": 22,
            "musicnotes": 18, "equalizer": 25,
            "qrcode": 18, "matrix": 18,
            "rainbow_spray": 25, "aurora": 55, "tornado": 35,
            "sumi": 12, "charcoal": 10,
            "dali": 18, "escher": 25, "pollock": 35,
        }

        cursor_path = os.path.join(os.path.dirname(__file__), 'assets/pointer.png')
        if os.path.exists(cursor_path):
            self.custom_cursor = QCursor(QPixmap(cursor_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.custom_cursor = QCursor(Qt.CursorShape.CrossCursor)

        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(self.auto_save_interval)
        self.layer_panel = None

    @property
    def active_layer(self):
        if 0 <= self.current_layer < len(self.layers):
            return self.layers[self.current_layer]
        return None

    @property
    def image(self):
        layer = self.active_layer
        return layer.image if layer else QImage()

    @image.setter
    def image(self, value):
        layer = self.active_layer
        if layer and not layer.locked_all:
            layer.image = value

    # Управление слоями
    def add_layer(self, name=None, fill_transparent=True):
        self.save_state()
        if name is None:
            name = f"Layer {len(self.layers)}"
        fill = Qt.GlobalColor.transparent if fill_transparent else Qt.GlobalColor.white
        new_layer = Layer(name, self.canvas_width, self.canvas_height, fill)
        insert_idx = self.current_layer + 1
        self.layers.insert(insert_idx, new_layer)
        self.current_layer = insert_idx
        self.update()
        if self.layer_panel:
            self.layer_panel.update_ui()

    def remove_layer(self, index=None):
        if index is None:
            index = self.current_layer
        if len(self.layers) <= 1:
            return
        self.save_state()
        del self.layers[index]
        if self.current_layer >= len(self.layers):
            self.current_layer = len(self.layers) - 1
        self.update()
        if self.layer_panel:
            self.layer_panel.update_ui()

    def duplicate_layer(self, index=None):
        if index is None:
            index = self.current_layer
        self.save_state()
        original = self.layers[index]
        dup = original.copy()
        dup.name = original.name + " copy"
        self.layers.insert(index + 1, dup)
        self.current_layer = index + 1
        self.update()
        if self.layer_panel:
            self.layer_panel.update_ui()

    def merge_down(self):
        if self.current_layer > 0:
            self.save_state()
            lower = self.layers[self.current_layer - 1]
            active = self.active_layer
            painter = QPainter(lower.image)
            painter.setCompositionMode(active.composition_mode())
            painter.setOpacity(active.opacity / 100.0)
            if active.visible:
                painter.drawImage(0, 0, active.image)
            painter.end()
            del self.layers[self.current_layer]
            self.current_layer -= 1
            self.update()
            if self.layer_panel:
                self.layer_panel.update_ui()

    def flatten(self):
        self.save_state()
        if len(self.layers) <= 1:
            return
        flat = QImage(self.canvas_width, self.canvas_height, QImage.Format.Format_ARGB32)
        flat.fill(Qt.GlobalColor.transparent)
        painter = QPainter(flat)
        for layer in self.layers:
            if layer.visible:
                painter.setCompositionMode(layer.composition_mode())
                painter.setOpacity(layer.opacity / 100.0)
                painter.drawImage(0, 0, layer.image)
        painter.end()
        self.layers = [Layer("Background", self.canvas_width, self.canvas_height)]
        self.layers[0].image = flat
        self.current_layer = 0
        self.update()
        if self.layer_panel:
            self.layer_panel.update_ui()

    # Undo/Redo
    def save_state(self):
        if len(self.undo_stack) >= self.history_limit:
            self.undo_stack.pop(0)
        layers_copy = [layer.copy() for layer in self.layers]
        state = (layers_copy, self.current_layer)
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            layers_copy, idx = self.undo_stack.pop()
            current_state = ([layer.copy() for layer in self.layers], self.current_layer)
            self.redo_stack.append(current_state)
            self.layers = layers_copy
            self.current_layer = idx
            self.update()
            if self.layer_panel:
                self.layer_panel.update_ui()
            self.selection_rect = None
            self.lasso_points = []

    def redo(self):
        if self.redo_stack:
            layers_copy, idx = self.redo_stack.pop()
            current_state = ([layer.copy() for layer in self.layers], self.current_layer)
            self.undo_stack.append(current_state)
            self.layers = layers_copy
            self.current_layer = idx
            self.update()
            if self.layer_panel:
                self.layer_panel.update_ui()
            self.selection_rect = None
            self.lasso_points = []

    # Инструменты
    def set_tool(self, tool):
        self.tool = tool
        self.text_input_mode = (tool == "text")
        if tool in self.tool_brush_sizes:
            self.brush_size = self.tool_brush_sizes[tool]
        self.update()

    def set_brush_color(self, color):
        self.brush_color = color

    def set_secondary_color(self, color):
        self.secondary_color = color

    def set_brush_size(self, size):
        self.brush_size = max(1, size)
        self.tool_brush_sizes[self.tool] = size
        self.update()

    def set_brush_shape(self, shape):
        self.brush_shape = shape

    def set_text(self, text):
        self.text = text

    def set_font(self, font):
        self.font = font

    def set_gradient_type(self, grad_type):
        self.gradient_type = grad_type

    def set_symmetry_axes(self, axes):
        self.symmetry_axes = max(1, min(axes, 16))

    def set_grid_size(self, size):
        self.grid_size = max(1, size)
        if self.grid_enabled:
            self.update()

    def toggle_antialiasing(self):
        self.antialiasing_enabled = not self.antialiasing_enabled
        self.update()

    def toggle_transparency(self):
        self.transparency_enabled = not self.transparency_enabled
        if self.transparency_enabled:
            for layer in self.layers:
                layer.image = layer.image.convertToFormat(QImage.Format.Format_ARGB32)
        self.update()

    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.update()

    def toggle_symmetry(self):
        self.symmetry_enabled = not self.symmetry_enabled
        self.update()

    def toggle_cursor_circle(self):
        self.cursor_circle = not self.cursor_circle
        self.update()

    def toggle_snap_to_grid(self):
        self.snap_to_grid = not self.snap_to_grid

    def toggle_ruler(self):
        self.ruler_enabled = not self.ruler_enabled
        if self.ruler_enabled:
            self.ruler_start = QPointF(0, 0)
            self.ruler_end = QPointF(self.canvas_width, self.canvas_height)
        self.update()

    def set_selection_tool(self, tool):
        self.selection_tool = tool
        if tool in ["rectangle", "lasso"]:
            self.set_tool("selection")
        self.update()

    def select_all(self):
        self.selection_rect = QRectF(0, 0, self.canvas_width, self.canvas_height)
        self.selection_tool = "rectangle"
        self.selection_content = None
        self.is_moving_selection = False
        self.update()

    def get_lasso_bounding_rect(self):
        if not self.lasso_points:
            return None
        min_x = min(p.x() for p in self.lasso_points)
        max_x = max(p.x() for p in self.lasso_points)
        min_y = min(p.y() for p in self.lasso_points)
        max_y = max(p.y() for p in self.lasso_points)
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def create_lasso_mask(self):
        if len(self.lasso_points) < 3:
            return
        polygon = QPolygonF(self.lasso_points)
        self.selection_mask = QImage(self.canvas_width, self.canvas_height, QImage.Format.Format_ARGB32)
        self.selection_mask.fill(Qt.GlobalColor.transparent)
        mask_painter = QPainter(self.selection_mask)
        mask_painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
        mask_painter.setPen(QPen(Qt.GlobalColor.white, 2))
        mask_painter.drawPolygon(polygon)
        mask_painter.end()

    def copy_selection(self):
        if self.selection_rect and self.selection_rect.width() > 2 and self.selection_rect.height() > 2:
            if self.selection_tool == "lasso" and self.selection_mask and self.lasso_points:
                temp = QImage(self.selection_rect.size().toSize(), QImage.Format.Format_ARGB32)
                temp.fill(Qt.GlobalColor.transparent)
                painter = QPainter(temp)
                painter.drawImage(0, 0, self.active_layer.image, self.selection_rect.toRect())
                painter.end()
                mask_rect = self.selection_mask.copy(self.selection_rect.toRect())
                for y in range(temp.height()):
                    for x in range(temp.width()):
                        if mask_rect.pixelColor(x, y).alpha() < 100:
                            temp.setPixelColor(x, y, Qt.GlobalColor.transparent)
                QApplication.clipboard().setPixmap(QPixmap.fromImage(temp))
            else:
                QApplication.clipboard().setPixmap(QPixmap.fromImage(self.active_layer.image.copy(self.selection_rect.toRect())))

    def cut_selection(self):
        if self.selection_rect and self.selection_rect.width() > 2 and self.selection_rect.height() > 2:
            self.copy_selection()
            self.save_state()
            painter = QPainter(self.active_layer.image)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            if self.selection_tool == "lasso" and self.selection_mask:
                for y in range(int(self.selection_rect.height())):
                    for x in range(int(self.selection_rect.width())):
                        if self.selection_mask.pixelColor(int(self.selection_rect.x() + x), int(self.selection_rect.y() + y)).alpha() >= 100:
                            self.active_layer.image.setPixelColor(
                                int(self.selection_rect.x() + x),
                                int(self.selection_rect.y() + y),
                                Qt.GlobalColor.transparent
                            )
            else:
                painter.fillRect(self.selection_rect, Qt.GlobalColor.transparent)
            painter.end()
            self.selection_rect = None
            self.selection_mask = None
            self.lasso_points = []
            self.update()

    def paste_image(self):
        pix = QApplication.clipboard().pixmap()
        if not pix.isNull():
            self.save_state()
            self.selection_rect = QRectF(100, 100, pix.width(), pix.height())
            self.selection_content = pix.toImage()
            self.selection_tool = "rectangle"
            self.is_moving_selection = True
            self.selection_offset = QPointF(100, 100)
            self.update()

    def apply_selection_transform(self):
        if not self.selection_content or not self.selection_rect:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Трансформация")
        layout = QFormLayout(dialog)
        rotate_spin = QSpinBox()
        rotate_spin.setRange(-360, 360)
        scale_spin = QSpinBox()
        scale_spin.setRange(10, 500)
        scale_spin.setValue(100)
        layout.addRow("Поворот (°):", rotate_spin)
        layout.addRow("Масштаб (%):", scale_spin)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            transform = QTransform()
            transform.rotate(rotate_spin.value())
            transform.scale(scale_spin.value() / 100.0, scale_spin.value() / 100.0)
            self.selection_content = self.selection_content.transformed(transform)
            self.selection_rect.setSize(QSizeF(self.selection_content.size()))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.zoom_factor != 1.0:
            painter.translate(self.zoom_center)
            painter.scale(self.zoom_factor, self.zoom_factor)
            painter.translate(-self.zoom_center)

        # Фон
        painter.fillRect(self.rect(), QColor("#f0f0f0"))

        # Отрисовка слоёв
        for layer in self.layers:
            if not layer.visible:
                continue
            painter.save()
            painter.setCompositionMode(layer.composition_mode())
            painter.setOpacity(layer.opacity / 100.0)
            painter.drawImage(0, 0, layer.image)
            painter.restore()

        # Сетка
        if self.grid_enabled:
            painter.setPen(QPen(QColor(200, 200, 200, 100), 1))
            for x in range(0, self.canvas_width, self.grid_size):
                painter.drawLine(x, 0, x, self.canvas_height)
            for y in range(0, self.canvas_height, self.grid_size):
                painter.drawLine(0, y, self.canvas_width, y)

        # Лассо
        if self.is_drawing_lasso and len(self.lasso_points) > 1:
            painter.setPen(QPen(QColor(0, 100, 255), 2))
            for i in range(len(self.lasso_points) - 1):
                painter.drawLine(self.lasso_points[i], self.lasso_points[i + 1])
            if self.lasso_points:
                cursor_pos = self.mapFromGlobal(QCursor.pos())
                painter.drawLine(self.lasso_points[-1], cursor_pos)

        # Выделение
        if self.selection_rect:
            if self.is_moving_selection and self.selection_content:
                painter.drawImage(self.selection_rect.topLeft(), self.selection_content)
                painter.setPen(QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.DashLine))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(self.selection_rect)
            elif self.selection_tool == "lasso" and self.lasso_points and not self.is_moving_selection:
                painter.setPen(QPen(QColor(0, 100, 255), 2))
                painter.setBrush(QBrush(QColor(0, 100, 255, 30)))
                painter.drawPolygon(QPolygonF(self.lasso_points))
            else:
                painter.setPen(QPen(QColor(0, 100, 255), 1, Qt.PenStyle.DashLine))
                painter.setBrush(QBrush(QColor(0, 100, 255, 30)))
                painter.drawRect(self.selection_rect)

        # Линейка
        if self.ruler_enabled:
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            painter.drawLine(self.ruler_start, self.ruler_end)
            length = math.hypot(self.ruler_end.x() - self.ruler_start.x(), 
                              self.ruler_end.y() - self.ruler_start.y())
            mid_point = (self.ruler_start + self.ruler_end) / 2
            painter.drawText(mid_point, f"{length:.1f} px")

        # Текст
        if self.text_input_mode:
            painter.setPen(QPen(self.brush_color))
            painter.setFont(self.font)
            painter.drawText(self.text_position.toPoint(), self.text + "|")

        # Курсор
        if self.cursor_circle and not self.text_input_mode:
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            pos = self.mapFromGlobal(QCursor.pos())
            painter.drawEllipse(pos, self.brush_size, self.brush_size)

    def mousePressEvent(self, event):
        pos = event.position()
        if self.snap_to_grid and self.grid_enabled:
            pos = self.snap_to_grid_pos(pos)

        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool == "selection":
                if self.selection_rect and self.selection_rect.contains(pos) and not self.is_selecting:
                    self.is_moving_selection = True
                    self.selection_offset = pos - self.selection_rect.topLeft()
                    if self.selection_tool == "lasso" and self.selection_mask:
                        temp = QImage(self.selection_rect.size().toSize(), QImage.Format.Format_ARGB32)
                        temp.fill(Qt.GlobalColor.transparent)
                        painter = QPainter(temp)
                        painter.drawImage(0, 0, self.active_layer.image, self.selection_rect.toRect())
                        painter.end()
                        mask_rect = self.selection_mask.copy(self.selection_rect.toRect())
                        for y in range(temp.height()):
                            for x in range(temp.width()):
                                if mask_rect.pixelColor(x, y).alpha() < 100:
                                    temp.setPixelColor(x, y, Qt.GlobalColor.transparent)
                        self.selection_content = temp
                    else:
                        self.selection_content = self.active_layer.image.copy(self.selection_rect.toRect())
                    painter = QPainter(self.active_layer.image)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                    painter.fillRect(self.selection_rect, Qt.GlobalColor.transparent)
                    painter.end()
                    self.update()
                    return
                self.save_state()
                if self.selection_tool == "rectangle":
                    self.is_selecting = True
                    self.selection_rect = QRectF(pos, pos)
                    self.lasso_points = []
                elif self.selection_tool == "lasso":
                    self.is_drawing_lasso = True
                    self.lasso_points = [pos]
                    self.selection_rect = None
                self.update()
            elif self.tool == "eyedropper":
                if self.active_layer:
                    color = self.active_layer.image.pixelColor(pos.toPoint())
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.set_secondary_color(color)
                    else:
                        self.set_brush_color(color)
            elif self.tool == "ruler" and self.ruler_enabled:
                self.ruler_start = pos
                self.ruler_end = pos
            else:
                self.save_state()
                self.drawing = True
                self.last_point = pos
                self.shape_start_point = pos
                if self.tool == "text":
                    self.text_input_mode = True
                    self.text_position = pos
                    self.text = ""
                elif self.tool == "fill":
                    if self.active_layer:
                        self.active_layer.image = self.flood_fill_tool.flood_fill_numpy(
                            self.active_layer.image, pos.toPoint(), self.brush_color)
                elif self.tool in ["rectangle", "ellipse", "line", "gradient"]:
                    self.is_drawing_shape = True
                    if self.active_layer:
                        self.temp_image = self.active_layer.image.copy()
                self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())

    def mouseMoveEvent(self, event):
        pos = event.position()
        if self.snap_to_grid and self.grid_enabled:
            pos = self.snap_to_grid_pos(pos)

        if self.drawing:
            layer = self.active_layer
            if layer is None or layer.locked_all or layer.locked_position:
                return
            if self.tool in ["rectangle", "ellipse", "line", "gradient"] and self.is_drawing_shape:
                if self.temp_image is None:
                    return
                self.active_layer.image = self.temp_image.copy()
                painter = QPainter(self.active_layer.image)
                self.setup_painter(painter)
                rect = QRectF(self.shape_start_point, pos).normalized()
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    size = min(rect.width(), rect.height())
                    if pos.x() < self.shape_start_point.x():
                        rect.setLeft(self.shape_start_point.x() - size)
                    else:
                        rect.setWidth(size)
                    if pos.y() < self.shape_start_point.y():
                        rect.setTop(self.shape_start_point.y() - size)
                    else:
                        rect.setHeight(size)
                if self.tool == "rectangle":
                    painter.drawRect(rect)
                elif self.tool == "ellipse":
                    painter.drawEllipse(rect)
                elif self.tool == "line":
                    self.draw_line_with_symmetry(painter, self.shape_start_point, pos)
                elif self.tool == "gradient":
                    self.apply_gradient(self.shape_start_point, pos)
                painter.end()
            elif self.tool in CUSTOM_BRUSHES and apply_brush:
                painter = QPainter(self.active_layer.image)
                if self.antialiasing_enabled:
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                settings = {
                    'color': self.brush_color,
                    'size': self.brush_size,
                    'density': 20,
                    'scatter': 15,
                    'intensity': 100,
                    'pixel_size': 5,
                    'spacing': 2,
                    'angle': 45,
                    'length': 8
                }
                apply_brush(self.tool, painter, self.last_point, pos, settings)
                painter.end()
                self.last_point = pos
            else:
                # Обычное рисование (pen, eraser, calligraphy и т.д.)
                painter = QPainter(self.active_layer.image)
                self.setup_painter(painter)
                if self.tool == "pen":
                    cap = Qt.PenCapStyle.RoundCap if self.brush_shape == "round" else Qt.PenCapStyle.SquareCap
                    join = Qt.PenJoinStyle.RoundJoin if self.brush_shape == "round" else Qt.PenJoinStyle.MiterJoin
                    painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, cap, join))
                    painter.drawLine(self.last_point, pos)
                elif self.tool == "eraser":
                    painter.setPen(QPen(Qt.GlobalColor.transparent, self.brush_size))
                    painter.drawLine(self.last_point, pos)
                elif self.tool == "calligraphy":
                    direction = pos - self.last_point
                    angle = math.degrees(math.atan2(direction.y(), direction.x())) % 360
                    thickness = self.brush_size * (1 + abs(math.sin(math.radians(angle))))
                    painter.setPen(QPen(self.brush_color, max(1, thickness), Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap))
                    painter.drawLine(self.last_point, pos)
                elif self.tool == "fountain_pen":
                    thickness = self.brush_size + random.uniform(-1, 1)
                    painter.setPen(QPen(self.brush_color, max(1, thickness), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    painter.drawLine(self.last_point, pos)
                elif self.tool == "spray":
                    for _ in range(20):
                        offset = QPointF(random.uniform(-self.brush_size, self.brush_size),
                                       random.uniform(-self.brush_size, self.brush_size))
                        alpha = random.randint(50, 255)
                        color = QColor(self.brush_color)
                        color.setAlpha(alpha)
                        painter.setPen(QPen(color, 1))
                        painter.drawPoint(pos + offset)
                elif self.tool == "oil_brush":
                    color = QColor(self.brush_color)
                    color.setAlpha(150)
                    painter.setPen(QPen(color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    painter.drawLine(self.last_point, pos)
                elif self.tool == "colored_pencil":
                    steps = 10
                    step_size = (pos - self.last_point) / steps
                    for i in range(steps):
                        if random.random() > 0.8:
                            continue
                        point = self.last_point + step_size * i
                        painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                        painter.drawPoint(point)
                elif self.tool == "marker":
                    color = QColor(self.brush_color)
                    color.setAlpha(100)
                    painter.setPen(QPen(color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap))
                    painter.drawLine(self.last_point, pos)
                elif self.tool == "texture_pencil":
                    steps = 10
                    step_size = (pos - self.last_point) / steps
                    for i in range(steps):
                        noise = random.uniform(-1, 1)
                        point = self.last_point + step_size * i + QPointF(noise, noise)
                        painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                        painter.drawPoint(point)
                elif self.tool == "watercolor_brush":
                    gradient = QLinearGradient(self.last_point, pos)
                    gradient.setColorAt(0, self.brush_color)
                    gradient.setColorAt(1, QColor(self.brush_color.red(), self.brush_color.green(), 
                                                  self.brush_color.blue(), 0))
                    painter.setPen(QPen(QBrush(gradient), self.brush_size))
                    painter.drawLine(self.last_point, pos)
                painter.end()
                self.last_point = pos
            self.update()
        elif self.tool == "selection" and self.is_selecting and self.selection_tool == "rectangle":
            self.selection_rect = QRectF(self.shape_start_point, pos).normalized()
            self.update()
        elif self.tool == "selection" and self.is_drawing_lasso:
            self.lasso_points.append(pos)
            self.update()
        elif self.tool == "selection" and self.is_moving_selection:
            new_top_left = pos - self.selection_offset
            self.selection_rect.moveTopLeft(new_top_left)
            self.update()
        elif self.tool == "ruler" and self.ruler_enabled and event.buttons() & Qt.MouseButton.LeftButton:
            self.ruler_end = pos
            self.update()

    def mouseReleaseEvent(self, event):
        pos = event.position()
        if self.snap_to_grid and self.grid_enabled:
            pos = self.snap_to_grid_pos(pos)
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tool == "selection" and self.is_selecting:
                self.is_selecting = False
                if self.selection_tool == "lasso":
                    self.is_drawing_lasso = False
                    if len(self.lasso_points) > 2:
                        if self.lasso_points[0] != self.lasso_points[-1]:
                            self.lasso_points.append(self.lasso_points[0])
                        self.selection_rect = self.get_lasso_bounding_rect()
                        self.create_lasso_mask()
                    else:
                        self.selection_rect = None
                        self.lasso_points = []
                self.update()
            elif self.tool == "selection" and self.is_moving_selection:
                self.is_moving_selection = False
                if self.selection_content and self.selection_rect:
                    painter = QPainter(self.active_layer.image)
                    painter.drawImage(self.selection_rect.topLeft(), self.selection_content)
                    painter.end()
                    self.selection_content = None
                    self.update()
            elif self.drawing:
                if self.tool in ["rectangle", "ellipse", "line", "gradient"] and self.is_drawing_shape:
                    self.is_drawing_shape = False
                    self.temp_image = None
                self.drawing = False
                self.update()

    def setup_painter(self, painter):
        if self.antialiasing_enabled:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.tool == "eraser":
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        else:
            painter.setCompositionMode(self.brush_blend_mode)
        if self.brush_opacity < 1.0:
            painter.setOpacity(self.brush_opacity)

    def draw_line_with_symmetry(self, painter, start, end):
        painter.drawLine(start, end)
        if self.symmetry_enabled and self.symmetry_axes > 1:
            center = QPointF(self.canvas_width / 2, self.canvas_height / 2)
            angle_step = 360 / self.symmetry_axes
            for i in range(1, self.symmetry_axes):
                angle = math.radians(angle_step * i)
                def rotate(p):
                    dx, dy = p.x() - center.x(), p.y() - center.y()
                    new_x = center.x() + dx * math.cos(angle) - dy * math.sin(angle)
                    new_y = center.y() + dx * math.sin(angle) + dy * math.cos(angle)
                    return QPointF(new_x, new_y)
                painter.drawLine(rotate(start), rotate(end))

    def apply_gradient(self, start, end):
        gradient = None
        if self.gradient_type == "linear":
            gradient = QLinearGradient(start, end)
        elif self.gradient_type == "radial":
            r = math.hypot(end.x() - start.x(), end.y() - start.y())
            gradient = QRadialGradient(start, r)
        elif self.gradient_type == "conical":
            a = math.atan2(end.y() - start.y(), end.x() - start.x()) * 180 / math.pi
            gradient = QConicalGradient(start, a)
        if gradient:
            gradient.setColorAt(0, self.brush_color)
            gradient.setColorAt(1, self.secondary_color)
            painter = QPainter(self.active_layer.image)
            painter.setBrush(QBrush(gradient))
            if self.tool == "rectangle":
                painter.drawRect(QRectF(start, end))
            elif self.tool == "ellipse":
                painter.drawEllipse(QRectF(start, end))

    def snap_to_grid_pos(self, pos):
        g = self.grid_size
        return QPointF(round(pos.x() / g) * g, round(pos.y() / g) * g)

    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            zoom = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.zoom_factor *= zoom
            self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))
            self.update()
        elif modifiers & Qt.KeyboardModifier.AltModifier:
            delta = 0.05 if event.angleDelta().y() > 0 else -0.05
            self.brush_opacity = max(0.1, min(1.0, self.brush_opacity + delta))
            self.update()
        else:
            delta = 1 if event.angleDelta().y() > 0 else -1
            self.set_brush_size(self.brush_size + delta)

    def keyPressEvent(self, event):
        if self.text_input_mode:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                painter = QPainter(self.active_layer.image)
                painter.setPen(QPen(self.brush_color))
                painter.setFont(self.font)
                painter.drawText(self.text_position.toPoint(), self.text)
                painter.end()
                self.text_input_mode = False
                self.text = ""
                self.update()
            elif event.key() == Qt.Key.Key_Backspace:
                self.text = self.text[:-1]
                self.update()
            elif event.key() == Qt.Key.Key_Escape:
                self.text_input_mode = False
                self.text = ""
                self.update()
            else:
                self.text += event.text()
                self.update()
        else:
            km = {
                Qt.Key.Key_B: "pen", Qt.Key.Key_E: "eraser", Qt.Key.Key_L: "line",
                Qt.Key.Key_R: "rectangle", Qt.Key.Key_C: "ellipse", Qt.Key.Key_T: "text",
                Qt.Key.Key_G: "fill", Qt.Key.Key_I: "eyedropper", Qt.Key.Key_M: "selection",
                Qt.Key.Key_D: "gradient", Qt.Key.Key_H: "spray", Qt.Key.Key_O: "oil_brush",
                Qt.Key.Key_A: "marker", Qt.Key.Key_W: "watercolor_brush"
            }
            if event.key() in km:
                self.set_tool(km[event.key()])
            elif event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self.set_brush_size(self.brush_size + 1)
            elif event.key() == Qt.Key.Key_Minus:
                self.set_brush_size(max(1, self.brush_size - 1))
            elif event.key() == Qt.Key.Key_Left:
                self.undo()
            elif event.key() == Qt.Key.Key_Right:
                self.redo()
            elif event.key() == Qt.Key.Key_F1:
                self.toggle_grid()
            elif event.key() == Qt.Key.Key_F2:
                self.toggle_symmetry()
            elif event.key() == Qt.Key.Key_F3:
                self.toggle_ruler()
            elif event.key() == Qt.Key.Key_F4:
                self.toggle_cursor_circle()
            elif event.key() == Qt.Key.Key_F5:
                self.toggle_snap_to_grid()
            elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.select_all()

    def resize_canvas(self, w, h):
        self.canvas_width = w
        self.canvas_height = h
        for layer in self.layers:
            old = layer.image
            new_img = QImage(w, h, QImage.Format.Format_ARGB32)
            new_img.fill(Qt.GlobalColor.transparent)
            painter = QPainter(new_img)
            painter.drawImage(0, 0, old)
            painter.end()
            layer.image = new_img
        self.update()

    def clear(self):
        self.save_state()
        self.layers = [Layer("Background", self.canvas_width, self.canvas_height, Qt.GlobalColor.white)]
        self.current_layer = 0
        self.selection_rect = None
        self.lasso_points = []
        self.update()
        if self.layer_panel:
            self.layer_panel.update_ui()

    def save(self, filename):
        flat = QImage(self.canvas_width, self.canvas_height, QImage.Format.Format_ARGB32)
        flat.fill(Qt.GlobalColor.white)
        painter = QPainter(flat)
        for layer in self.layers:
            if layer.visible:
                painter.setCompositionMode(layer.composition_mode())
                painter.setOpacity(layer.opacity / 100.0)
                painter.drawImage(0, 0, layer.image)
        painter.end()
        flat.save(filename)

    def open(self, filename):
        img = QImage()
        img.load(filename)
        self.canvas_width = img.width()
        self.canvas_height = img.height()
        self.layers = [Layer("Background", self.canvas_width, self.canvas_height)]
        self.layers[0].image = img.convertToFormat(QImage.Format.Format_ARGB32)
        self.current_layer = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.selection_rect = None
        self.lasso_points = []
        self.update()
        if self.layer_panel:
            self.layer_panel.update_ui()

    def show_context_menu(self, position):
        menu = QMenu(self)
        tools_menu = menu.addMenu("Инструменты")
        tools_menu.addAction("Карандаш", lambda: self.set_tool("pen"))
        tools_menu.addAction("Ластик", lambda: self.set_tool("eraser"))
        tools_menu.addAction("Линия", lambda: self.set_tool("line"))
        tools_menu.addAction("Прямоугольник", lambda: self.set_tool("rectangle"))
        tools_menu.addAction("Эллипс", lambda: self.set_tool("ellipse"))
        tools_menu.addAction("Заливка", lambda: self.set_tool("fill"))
        tools_menu.addAction("Градиент", lambda: self.set_tool("gradient"))
        
        custom_menu = tools_menu.addMenu("Кисти")
        for tool_id, name in CUSTOM_BRUSHES.items():
            custom_menu.addAction(name, lambda t=tool_id: self.set_tool(t))
        
        sel_menu = tools_menu.addMenu("Выделение")
        sel_menu.addAction("Прямоугольное", lambda: self.set_selection_tool("rectangle"))
        sel_menu.addAction("Лассо", lambda: self.set_selection_tool("lasso"))
        menu.addSeparator()
        menu.addAction("Копировать", self.copy_selection)
        menu.addAction("Вырезать", self.cut_selection)
        menu.addAction("Вставить", self.paste_image)
        menu.addSeparator()
        menu.addAction("Отменить", self.undo)
        menu.addAction("Повторить", self.redo)
        menu.exec(self.mapToGlobal(position))

    def auto_save(self):
        try:
            if not os.path.exists(self.auto_save_path):
                os.makedirs(self.auto_save_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.auto_save_path, f"autosave_{timestamp}.png")
            self.save(filename)
        except Exception as e:
            print(f"Auto-save failed: {e}")


# -----------------------------------------------------------------------------
# Диалог разрешения
# -----------------------------------------------------------------------------
class ResolutionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Размер холста")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 5000)
        self.width_spin.setValue(1280)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 5000)
        self.height_spin.setValue(720)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout = QFormLayout()
        layout.addRow("Ширина:", self.width_spin)
        layout.addRow("Высота:", self.height_spin)
        layout.addRow(btns)
        self.setLayout(layout)

    def get_resolution(self):
        return self.width_spin.value(), self.height_spin.value()


# -----------------------------------------------------------------------------
# Главное окно
# -----------------------------------------------------------------------------
class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GovnoPaint v6.7")
        self.resize(1200, 800)
        icon_path = os.path.join(os.path.dirname(__file__), 'assets/brush.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.paint_widget = PaintWidget()
        self.current_file = None

        # Панель слоёв
        self.layer_panel = LayerPanel(self.paint_widget)
        self.paint_widget.layer_panel = self.layer_panel
        dock = QDockWidget("Слои", self)
        dock.setWidget(self.layer_panel)
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        self.setup_ui()
        self.setup_shortcuts()
        self.setStyleSheet(self.modern_stylesheet())

    def modern_stylesheet(self):
        return """
        QMainWindow { background-color: #f8f9fa; }
        QToolBar { background-color: #ffffff; border-bottom: 1px solid #e0e0e0; padding: 8px; spacing: 4px; }
        QToolButton { background: transparent; border: none; border-radius: 4px; padding: 6px; min-width: 32px; min-height: 32px; }
        QToolButton:hover { background: #e9ecef; }
        QToolButton:pressed { background: #dee2e6; }
        QToolButton:checked { background: #0d6efd; color: white; }
        QComboBox, QSpinBox { padding: 4px 8px; border: 1px solid #ced4da; border-radius: 4px; background: white; }
        QComboBox:hover, QSpinBox:hover { border-color: #868e96; }
        QSlider::groove:horizontal { border: 1px solid #ced4da; height: 4px; background: #e9ecef; border-radius: 2px; }
        QSlider::handle:horizontal { background: #0d6efd; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
        QSlider::handle:horizontal:hover { background: #0b5ed7; }
        QDockWidget { border: 1px solid #e0e0e0; }
        QDockWidget::title { background: #f8f9fa; padding: 6px; border-bottom: 1px solid #e0e0e0; }
        """

    def setup_ui(self):
        self.create_toolbar()
        self.create_menus()
        self.create_statusbar()
        scroll = QScrollArea()
        scroll.setWidget(self.paint_widget)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

    def create_tool_button(self, icon_name, tooltip, callback, color="#343a40"):
        btn = QToolButton()
        try:
            btn.setIcon(qta.icon(icon_name, color=color))
        except:
            btn.setText(icon_name)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        return btn

    def create_toolbar(self):
        tb = self.addToolBar("Инструменты")
        tb.setMovable(False)
        
        # Файловые операции
        tb.addWidget(self.create_tool_button("fa5s.file", "Новый", self.new_file))
        tb.addWidget(self.create_tool_button("fa5s.folder-open", "Открыть", self.open_image))
        tb.addWidget(self.create_tool_button("fa5s.save", "Сохранить", self.save_image))
        tb.addSeparator()
        tb.addWidget(self.create_tool_button("fa5s.undo", "Отменить", self.paint_widget.undo))
        tb.addWidget(self.create_tool_button("fa5s.redo", "Повторить", self.paint_widget.redo))
        tb.addSeparator()

        # Инструменты
        tools = {
            "pen": ("fa5s.pen", "Карандаш"),
            "eraser": ("fa5s.eraser", "Ластик"),
            "line": ("fa5s.ruler", "Линия"),
            "rectangle": ("fa5s.square", "Прямоугольник"),
            "ellipse": ("fa5s.circle", "Эллипс"),
            "text": ("fa5s.font", "Текст"),
            "fill": ("fa5s.fill-drip", "Заливка"),
            "gradient": ("fa5s.fill", "Градиент"),
        }
        self.tool_buttons = {}
        group = QButtonGroup(self)
        group.setExclusive(True)
        for tool, (icon, tip) in tools.items():
            btn = self.create_tool_button(icon, tip, partial(self.set_tool, tool))
            btn.setCheckable(True)
            group.addButton(btn)
            self.tool_buttons[tool] = btn
            tb.addWidget(btn)
        self.tool_buttons["pen"].setChecked(True)

        tb.addSeparator()

        # Кастомные кисти
        self.custom_brush_combo = QComboBox()
        self.custom_brush_combo.addItem("🖌️ Кисти", "none")
        for tool_id, name in CUSTOM_BRUSHES.items():
            self.custom_brush_combo.addItem(f"  {name}", tool_id)
        self.custom_brush_combo.currentIndexChanged.connect(self.on_custom_brush_selected)
        tb.addWidget(self.custom_brush_combo)

        tb.addSeparator()

        # Цвет и размер
        self.color_btn = self.create_tool_button("fa5s.paint-brush", "Цвет", self.choose_color)
        tb.addWidget(self.color_btn)
        
        tb.addWidget(QLabel("Размер:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(2)
        self.size_slider.setFixedWidth(80)
        self.size_slider.valueChanged.connect(lambda v: self.paint_widget.set_brush_size(v))
        tb.addWidget(self.size_slider)

    def set_tool(self, tool):
        self.paint_widget.set_tool(tool)
        for t, btn in self.tool_buttons.items():
            btn.setChecked(t == tool)
        # Сбрасываем комбо кистей
        if tool not in CUSTOM_BRUSHES:
            self.custom_brush_combo.blockSignals(True)
            self.custom_brush_combo.setCurrentIndex(0)
            self.custom_brush_combo.blockSignals(False)

    def on_custom_brush_selected(self, index):
        tool = self.custom_brush_combo.itemData(index)
        if tool and tool != "none":
            self.set_tool(tool)

    def create_menus(self):
        mb = self.menuBar()
        
        file_menu = mb.addMenu("Файл")
        file_menu.addAction("Новый", self.new_file)
        file_menu.addAction("Открыть", self.open_image)
        file_menu.addAction("Сохранить", self.save_image)
        file_menu.addAction("Сохранить как", self.save_image_as)
        file_menu.addSeparator()
        file_menu.addAction("Выход", self.close)

        edit_menu = mb.addMenu("Правка")
        edit_menu.addAction("Отменить", self.paint_widget.undo)
        edit_menu.addAction("Повторить", self.paint_widget.redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Вырезать", self.paint_widget.cut_selection)
        edit_menu.addAction("Копировать", self.paint_widget.copy_selection)
        edit_menu.addAction("Вставить", self.paint_widget.paste_image)

        layer_menu = mb.addMenu("Слои")
        layer_menu.addAction("Добавить слой", self.paint_widget.add_layer)
        layer_menu.addAction("Удалить слой", self.paint_widget.remove_layer)
        layer_menu.addAction("Дублировать", self.paint_widget.duplicate_layer)
        layer_menu.addAction("Объединить с нижним", self.paint_widget.merge_down)
        layer_menu.addAction("Свести все", self.paint_widget.flatten)

        view_menu = mb.addMenu("Вид")
        view_menu.addAction("Сетка", self.paint_widget.toggle_grid)
        view_menu.addAction("Линейка", self.paint_widget.toggle_ruler)
        view_menu.addAction("Симметрия", self.paint_widget.toggle_symmetry)

    def create_statusbar(self):
        sb = self.statusBar()
        self.tool_label = QLabel("Инструмент: Карандаш")
        self.size_label = QLabel("Размер: 2px")
        sb.addPermanentWidget(self.tool_label)
        sb.addPermanentWidget(self.size_label)
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_statusbar)
        self.status_timer.start(100)

    def update_statusbar(self):
        tool_names = {
            "pen": "Карандаш", "eraser": "Ластик", "line": "Линия",
            "rectangle": "Прямоугольник", "ellipse": "Эллипс", "text": "Текст",
            "fill": "Заливка", "gradient": "Градиент", "eyedropper": "Пипетка",
            "selection": "Выделение", 
            "sketching_pencil": "Скетч-карандаш", "hatching": "Штриховка", "gesture": "Жестовая",
            "concept_sketch": "Концепт-скетч", "silhouette": "Силуэт", "speed_paint": "Спидпейнт",
            "manga_tone": "Манга-тон", "comic_ink": "Комикс-инк", "screentone": "Скринтон",
            "calligraphy_nib": "Каллиграфия", "brush_pen": "Брашпен", "graffiti": "Граффити",
            "digital_oil": "Цифровое масло", "impasto": "Импасто", "palette_knife": "Мастихин",
            "blender": "Блендер", "texture_stencil": "Текстурный трафарет", "glaze": "Лессировка",
            "perspective": "Перспектива", "grid_perspective": "Сетка перспективы", "light_ray": "Световые лучи",
            "splatter": "Брызги", "glow": "Свечение", "rainbow": "Радужная",
            "fur": "Мех", "pixel": "Пиксельная", "neon": "Неон",
            "ribbon": "Лента", "engraving": "Гравировка", "fire": "Огонь", "smoke": "Дым", "bubbles": "Пузыри", "sparks": "Искры",
            "vine": "Лианы", "grass": "Трава", "coral": "Кораллы", "furball": "Пушистик",
            "kaleidoscope": "Калейдоскоп", "lightning": "Молния", "circuit": "Микросхема", 
            "hexgrid": "Соты", "fractal": "Фрактал",
            "crumble": "Крошка", "canvas": "Холст", "rust": "Ржавчина",
            "emoji": "Эмодзи", "ascii": "ASCII-арт", "morse": "Морзе",
            "galaxy": "Галактика", "constellation": "Созвездие",
            "rune": "Руны", "mana": "Мана", "phoenix": "Феникс",
            "opart": "Оп-арт", "moire": "Муар",
            "gravity": "Гравитация", "wind": "Ветер", "magnet": "Магнит", "soundwave": "Звуковая волна", "seismic": "Сейсмическая", "bass": "Бас",
            "cell": "Клетки", "bacteria": "Бактерии", "neuron": "Нейроны", "dna": "ДНК",
            "watercolor_wash": "Акварель", "inkdrop": "Чернила", "steam": "Пар",
            "brickwall": "Кирпичи", "chain": "Цепь", "scaffold": "Леса",
            "sprinkles": "Посыпка", "coffee": "Кофе",
            "musicnotes": "Ноты", "equalizer": "Эквалайзер",
            "qrcode": "QR-код", "matrix": "Матрица",
            "rainbow_spray": "Радужный спрей", "aurora": "Аврора", "tornado": "Торнадо",
            "sumi": "Суми-э", "charcoal": "Уголь",
            "dali": "Дали", "escher": "Эшер", "pollock": "Поллок",
        }
        tool_name = tool_names.get(self.paint_widget.tool, self.paint_widget.tool)
        self.tool_label.setText(f"Инструмент: {tool_name}")
        self.size_label.setText(f"Размер: {self.paint_widget.brush_size}px")
        
        if hasattr(self, 'size_slider') and self.size_slider.value() != self.paint_widget.brush_size:
            self.size_slider.blockSignals(True)
            self.size_slider.setValue(self.paint_widget.brush_size)
            self.size_slider.blockSignals(False)

    def setup_shortcuts(self):
        shortcuts = {
            "Ctrl+Z": self.paint_widget.undo,
            "Ctrl+Y": self.paint_widget.redo,
            "Ctrl+C": self.paint_widget.copy_selection,
            "Ctrl+X": self.paint_widget.cut_selection,
            "Ctrl+V": self.paint_widget.paste_image,
            "Ctrl+S": self.save_image,
            "Ctrl+Shift+S": self.save_image_as,
            "Ctrl+O": self.open_image,
            "Ctrl+N": self.new_file,
            "Ctrl+A": self.paint_widget.select_all,
            "Ctrl+T": self.paint_widget.apply_selection_transform,
        }
        for key, func in shortcuts.items():
            QShortcut(QKeySequence(key), self).activated.connect(func)

    def new_file(self):
        dlg = ResolutionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            w, h = dlg.get_resolution()
            self.paint_widget.canvas_width = w
            self.paint_widget.canvas_height = h
            self.paint_widget.layers = [Layer("Background", w, h, Qt.GlobalColor.white)]
            self.paint_widget.current_layer = 0
            self.paint_widget.undo_stack.clear()
            self.paint_widget.redo_stack.clear()
            self.paint_widget.selection_rect = None
            self.paint_widget.lasso_points = []
            self.paint_widget.update()
            if self.paint_widget.layer_panel:
                self.paint_widget.layer_panel.update_ui()
            self.current_file = None
            self.setWindowTitle("GovnoPaint - Новый рисунок")

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            self.paint_widget.open(filename)
            self.current_file = filename
            self.setWindowTitle(f"GovnoPaint - {os.path.basename(filename)}")

    def save_image(self):
        if self.current_file:
            self.paint_widget.save(self.current_file)
        else:
            self.save_image_as()

    def save_image_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp)")
        if filename:
            self.paint_widget.save(filename)
            self.current_file = filename
            self.setWindowTitle(f"GovnoPaint - {os.path.basename(filename)}")

    def choose_color(self):
        color = QColorDialog.getColor(self.paint_widget.brush_color, self, "Цвет кисти")
        if color.isValid():
            self.paint_widget.set_brush_color(color)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PaintApp()
    window.show()
    sys.exit(app.exec())