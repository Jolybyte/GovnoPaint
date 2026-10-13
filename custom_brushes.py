# custom_brushes.py
import math
import random
import numpy as np
from PyQt6.QtCore import QPointF, Qt, QRectF, QLineF
from PyQt6.QtGui import (
    QPen, QColor, QPainterPath, QLinearGradient, QRadialGradient,
    QConicalGradient, QBrush, QPolygonF, QFont, QFontMetrics
)

class BrushBase:
    """Базовый класс для кистей."""
    pass

# ============================================================================
# ЭКСПЕРИМЕНТАЛЬНЫЕ / ОСНОВНЫЕ КИСТИ
# ============================================================================

class SplatterBrush:
    """Брызги — хаотичные капли краски."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 5)
        density = settings.get('density', 20)
        scatter = settings.get('scatter', 15)
        for _ in range(density):
            offset = QPointF(random.uniform(-scatter, scatter), random.uniform(-scatter, scatter))
            alpha = random.randint(80, 255)
            c = QColor(color)
            c.setAlpha(alpha)
            painter.setPen(QPen(c, random.uniform(0.5, 2.5)))
            painter.drawPoint(current_point + offset)

class GlowBrush:
    """Свечение — мягкий ореол вокруг мазка."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 255, 0))
        size = settings.get('size', 15)
        intensity = settings.get('intensity', 100)
        steps = 3
        for i in range(steps, 0, -1):
            c = QColor(color)
            c.setAlpha(int(intensity * (i / steps)))
            pen = QPen(c, size * (i / steps), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(last_point, current_point)

class RainbowBrush:
    """Радуга — спектр по направлению движения."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 3)
        dx = current_point.x() - last_point.x()
        dy = current_point.y() - last_point.y()
        angle = math.atan2(dy, dx) * 180 / math.pi
        hue = (angle + 360) % 360
        color = QColor.fromHsv(int(hue), 255, 255)
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(last_point, current_point)

class FurBrush:
    """Мех — ворсинки во все стороны."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(139, 90, 43))
        size = settings.get('size', 4)
        density = settings.get('density', 15)
        length = settings.get('length', 8)
        for _ in range(density):
            angle = random.uniform(0, 2 * math.pi)
            dx = math.cos(angle) * length
            dy = math.sin(angle) * length
            p1 = current_point + QPointF(random.uniform(-2, 2), random.uniform(-2, 2))
            p2 = p1 + QPointF(dx, dy)
            c = QColor(color)
            c.setAlpha(random.randint(150, 255))
            painter.setPen(QPen(c, size * 0.5))
            painter.drawLine(p1, p2)

class PixelBrush:
    """Пиксель-арт — крупные квадраты."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        pixel_size = settings.get('pixel_size', 5)
        vec = current_point - last_point
        steps = max(1, int(vec.manhattanLength() / pixel_size))
        for i in range(steps):
            pt = last_point + (vec * i / steps)
            px = math.floor(pt.x() / pixel_size) * pixel_size
            py = math.floor(pt.y() / pixel_size) * pixel_size
            painter.fillRect(int(px), int(py), int(pixel_size), int(pixel_size), color)

class NeonBrush:
    """Неон — светящаяся трубка."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 0, 255))
        size = settings.get('size', 6)
        glow_size = size * 2
        glow_color = QColor(color)
        glow_color.setAlpha(80)
        painter.setPen(QPen(glow_color, glow_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(last_point, current_point)
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(last_point, current_point)

class RibbonBrush:
    """Лента — волнистая линия."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 255))
        base_size = settings.get('size', 8)
        path = QPainterPath()
        path.moveTo(last_point)
        dx = current_point.x() - last_point.x()
        dy = current_point.y() - last_point.y()
        dist = math.hypot(dx, dy)
        if dist < 2:
            return
        steps = max(2, int(dist / 3))
        for i in range(steps + 1):
            t = i / steps
            px = last_point.x() + dx * t
            py = last_point.y() + dy * t
            perp_x = -dy / dist
            perp_y = dx / dist
            wave = math.sin(t * 10) * base_size * 0.5
            px += perp_x * wave
            py += perp_y * wave
            path.lineTo(QPointF(px, py))
        painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

class EngravingBrush:
    """Гравировка — штриховка под углом."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 1)
        spacing = settings.get('spacing', 2)
        angle = settings.get('angle', 45)
        rad = math.radians(angle)
        dx = math.cos(rad) * spacing
        dy = math.sin(rad) * spacing
        vec = current_point - last_point
        steps = max(1, int(vec.manhattanLength() / spacing))
        painter.setPen(QPen(color, size))
        for i in range(steps):
            pt = last_point + (vec * i / steps)
            p1 = pt + QPointF(-dx, -dy)
            p2 = pt + QPointF(dx, dy)
            painter.drawLine(p1, p2)

# ============================================================================
# ЧАСТИЦЫ И ЭМИССИЯ
# ============================================================================

class FireBrush:
    """Огонь — языки пламени с градиентом."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 20)
        density = settings.get('density', 10)
        for _ in range(density):
            t = random.random()
            pt = last_point + (current_point - last_point) * t
            offset = QPointF(random.uniform(-5, 5), random.uniform(-10, 2))
            flame_len = random.uniform(size * 0.5, size * 1.5)
            flame_width = random.uniform(2, 5)
            gradient = QLinearGradient(pt, pt + QPointF(0, -flame_len))
            gradient.setColorAt(0, QColor(255, 255, 50, 200))
            gradient.setColorAt(0.5, QColor(255, 120, 0, 180))
            gradient.setColorAt(1, QColor(255, 0, 0, 0))
            painter.setPen(QPen(QBrush(gradient), flame_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(pt + offset, pt + offset + QPointF(0, -flame_len))

class SmokeBrush:
    """Дым — полупрозрачные клубы."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(150, 150, 150))
        size = settings.get('size', 30)
        density = settings.get('density', 8)
        for _ in range(density):
            center = last_point + (current_point - last_point) * random.random()
            c = QColor(color)
            c.setAlpha(random.randint(20, 60))
            r = random.uniform(5, size)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(center, r, r * random.uniform(0.5, 0.8))

class BubblesBrush:
    """Пузыри — мыльные пузырьки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 200, 255))
        density = settings.get('density', 12)
        size = settings.get('size', 10)
        for _ in range(density):
            pos = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            r = random.uniform(3, size)
            c = QColor(color)
            c.setAlpha(random.randint(80, 160))
            painter.setPen(QPen(c, 1.5))
            painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
            painter.drawEllipse(pos, r, r)
            # Блик
            highlight = pos + QPointF(-r*0.3, -r*0.3)
            painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
            painter.drawEllipse(highlight, r*0.2, r*0.2)

class SparksBrush:
    """Искры — разлетающиеся частицы."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 200, 0))
        density = settings.get('density', 25)
        size = settings.get('size', 8)
        for _ in range(density):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(5, size * 2)
            end_pos = current_point + QPointF(math.cos(angle) * dist, math.sin(angle) * dist)
            c = QColor(color)
            c.setAlpha(random.randint(150, 255))
            painter.setPen(QPen(c, 1.5))
            painter.drawLine(current_point, end_pos)
            painter.setPen(QPen(c, random.uniform(0.5, 2)))
            painter.drawPoint(end_pos)

# ============================================================================
# ОРГАНИЧЕСКИЕ
# ============================================================================

class VineBrush:
    """Лианы — извивающиеся растительные побеги."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(34, 139, 34))
        size = settings.get('size', 3)
        chaos = settings.get('chaos', 5)
        path = QPainterPath()
        path.moveTo(last_point)
        vec = current_point - last_point
        steps = max(2, int(vec.manhattanLength() / 2))
        for i in range(1, steps + 1):
            t = i / steps
            pt = last_point + vec * t
            offset = QPointF(math.sin(t * 20) * chaos, math.cos(t * 15) * chaos)
            path.lineTo(pt + offset)
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)
        # Листочки
        for i in range(0, steps, 5):
            t = i / steps
            pt = last_point + vec * t
            angle = random.uniform(0, 2 * math.pi)
            leaf_color = QColor(random.randint(50, 150), random.randint(100, 200), random.randint(20, 80))
            painter.setPen(QPen(leaf_color, 1))
            painter.setBrush(QBrush(leaf_color))
            leaf_path = QPainterPath()
            leaf_path.moveTo(pt)
            leaf_path.cubicTo(
                pt + QPointF(math.cos(angle)*4, math.sin(angle)*4),
                pt + QPointF(math.cos(angle+1)*4, math.sin(angle+1)*4),
                pt + QPointF(math.cos(angle+0.5)*6, math.sin(angle+0.5)*6)
            )
            painter.drawPath(leaf_path)

class GrassBrush:
    """Трава — пучки травинок."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(50, 180, 50))
        size = settings.get('size', 8)
        density = settings.get('density', 20)
        for _ in range(density):
            base = current_point + QPointF(random.uniform(-size, size), random.uniform(-2, 2))
            length = random.uniform(5, size * 2)
            sway = random.uniform(-0.5, 0.5)
            top = base + QPointF(sway * length * 0.5, -length)
            c = QColor(color)
            c.setGreen(min(255, c.green() + random.randint(-30, 30)))
            painter.setPen(QPen(c, 1.5))
            painter.drawLine(base, top)

class CoralBrush:
    """Кораллы — ветвистые структуры."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 127, 80))
        size = settings.get('size', 5)
        branches = settings.get('branches', 4)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 2:
            return
        for _ in range(branches):
            t = random.random()
            base = last_point + vec * t
            angle = math.atan2(vec.y(), vec.x()) + random.uniform(-1.2, 1.2)
            length = random.uniform(5, size * 3)
            end = base + QPointF(math.cos(angle) * length, math.sin(angle) * length)
            c = QColor(color)
            c.setRed(min(255, c.red() + random.randint(-20, 50)))
            painter.setPen(QPen(c, random.uniform(1, 3), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(base, end)

class FurballBrush:
    """Пушистик — очень мягкая размытая кисть с ворсинками."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 150, 100))
        size = settings.get('size', 15)
        density = settings.get('density', 40)
        for _ in range(density):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, size)
            pt = current_point + QPointF(math.cos(angle) * dist, math.sin(angle) * dist)
            c = QColor(color)
            c.setAlpha(random.randint(50, 120))
            painter.setPen(QPen(c, random.uniform(0.5, 2)))
            painter.drawPoint(pt)

# ============================================================================
# ГЕОМЕТРИЧЕСКИЕ / АБСТРАКТНЫЕ
# ============================================================================

class KaleidoscopeBrush:
    """Калейдоскоп — симметричное многократное отражение."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 3)
        rays = settings.get('rays', 8)
        center = current_point
        for i in range(rays):
            angle = (360 / rays) * i
            rad = math.radians(angle)
            rot = QPointF(
                (last_point.x() - center.x()) * math.cos(rad) - (last_point.y() - center.y()) * math.sin(rad) + center.x(),
                (last_point.x() - center.x()) * math.sin(rad) + (last_point.y() - center.y()) * math.cos(rad) + center.y()
            )
            painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(rot, current_point)

class LightningBrush:
    """Молния — зигзагообразные электрические разряды."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 230, 255))
        size = settings.get('size', 2)
        segments = settings.get('segments', 7)
        glow_color = QColor(100, 180, 255, 80)
        painter.setPen(QPen(glow_color, size * 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        path = LightningBrush._build_lightning(last_point, current_point, segments, 20)
        painter.drawPath(path)
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)
    
    @staticmethod
    def _build_lightning(start, end, segments, offset_max):
        path = QPainterPath()
        path.moveTo(start)
        vec = end - start
        for i in range(1, segments):
            t = i / segments
            base = start + vec * t
            perp = QPointF(-vec.y(), vec.x())
            perp_len = math.hypot(perp.x(), perp.y())
            if perp_len > 0:
                perp = perp / perp_len
            offset = perp * random.uniform(-offset_max, offset_max) * (1 - abs(2*t - 1))
            path.lineTo(base + offset)
        path.lineTo(end)
        return path

class CircuitBrush:
    """Микросхема — ортогональные дорожки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 255, 100))
        size = settings.get('size', 2)
        if random.random() > 0.5:
            mid = QPointF(current_point.x(), last_point.y())
        else:
            mid = QPointF(last_point.x(), current_point.y())
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap))
        painter.drawLine(last_point, mid)
        painter.drawLine(mid, current_point)
        # Узел
        painter.setBrush(QBrush(color))
        painter.drawEllipse(current_point, size, size)

class HexGridBrush:
    """Соты — шестиугольная сетка."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 200, 0))
        size = settings.get('size', 10)
        hex_radius = size / 2
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cx = current_point.x() + dx * size * 1.5
                cy = current_point.y() + dy * size * math.sqrt(3)
                if dx % 2 != 0:
                    cy += size * math.sqrt(3) / 2
                polygon = QPolygonF()
                for i in range(6):
                    angle = math.pi / 3 * i - math.pi / 6
                    px = cx + math.cos(angle) * hex_radius
                    py = cy + math.sin(angle) * hex_radius
                    polygon.append(QPointF(px, py))
                painter.setPen(QPen(color, 1))
                painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
                painter.drawPolygon(polygon)

class FractalBrush:
    """Фрактал — рекурсивное ветвление."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 150, 0))
        size = settings.get('size', 4)
        depth = settings.get('depth', 3)
        FractalBrush._branch(painter, last_point, current_point, depth, size, color)
    
    @staticmethod
    def _branch(painter, start, end, depth, size, color):
        if depth <= 0:
            return
        painter.setPen(QPen(color, size * depth * 0.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(start, end)
        vec = end - start
        dist = math.hypot(vec.x(), vec.y()) * 0.7
        angle = math.atan2(vec.y(), vec.x())
        for sign in [-1, 1]:
            new_angle = angle + sign * random.uniform(0.3, 0.8)
            new_end = end + QPointF(math.cos(new_angle) * dist, math.sin(new_angle) * dist)
            FractalBrush._branch(painter, end, new_end, depth - 1, size, color)

# ============================================================================
# ТЕКСТУРНЫЕ
# ============================================================================

class CrumbleBrush:
    """Крошка — мелкие осколки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(150, 120, 80))
        size = settings.get('size', 12)
        density = settings.get('density', 30)
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            poly = QPolygonF()
            for _ in range(random.randint(3, 6)):
                poly.append(pt + QPointF(random.uniform(-3, 3), random.uniform(-3, 3)))
            c = QColor(color)
            c.setAlpha(random.randint(100, 255))
            painter.setPen(QPen(c.darker(120), 1))
            painter.setBrush(QBrush(c))
            painter.drawPolygon(poly)

class CanvasTextureBrush:
    """Холст — имитация фактурной бумаги."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 250, 240))
        size = settings.get('size', 20)
        for _ in range(50):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            c = QColor(color.red(), color.green(), color.blue(), random.randint(10, 40))
            painter.setPen(QPen(c, 1))
            painter.drawPoint(pt)

class RustBrush:
    """Ржавчина — коррозия металла."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 15)
        density = settings.get('density', 20)
        colors = [QColor(180, 80, 20), QColor(200, 120, 40), QColor(160, 60, 10), QColor(210, 140, 30)]
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            c = QColor(random.choice(colors))
            c.setAlpha(random.randint(150, 255))
            r = random.uniform(1, 4)
            painter.setPen(QPen(c.darker(110), 1))
            painter.setBrush(QBrush(c))
            painter.drawEllipse(pt, r, r)

# ============================================================================
# СИМВОЛЬНЫЕ / ТЕКСТОВЫЕ
# ============================================================================

class EmojiBrush:
    """Эмодзи — рисует случайными смайликами."""
    EMOJIS = ['🌟', '💫', '✨', '🔥', '💖', '🎨', '🌈', '🦋', '🌸', '🍀', '⭐', '💎', '🎵', '🦄']
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 12)
        density = settings.get('density', 3)
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            emoji = random.choice(EmojiBrush.EMOJIS)
            font = QFont("Segoe UI Emoji", int(size))
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255, 200)))
            painter.drawText(pt, emoji)

class AsciiBrush:
    """ASCII-арт — символы разной плотности."""
    CHARS = '@%#*+=-:. '
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 8)
        density = settings.get('density', 5)
        font = QFont("Courier New", int(size))
        painter.setFont(font)
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            char = random.choice(AsciiBrush.CHARS)
            c = QColor(color)
            c.setAlpha(random.randint(100, 255))
            painter.setPen(QPen(c, 1))
            painter.drawText(pt, char)

class MorseBrush:
    """Азбука Морзе — рисует точки и тире."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 3)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        num_symbols = max(2, int(dist / 5))
        for i in range(num_symbols):
            t = i / num_symbols
            pt = last_point + vec * t
            if random.random() > 0.5:
                # Тире
                painter.drawLine(pt, pt + QPointF(3, 0))
            else:
                # Точка
                painter.drawPoint(pt)

# ============================================================================
# КОСМИЧЕСКИЕ
# ============================================================================

class GalaxyBrush:
    """Галактика — спиральные рукава из звёзд."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        density = settings.get('density', 50)
        size = settings.get('size', 20)
        center = current_point
        for _ in range(density):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, size)
            spiral_angle = angle + dist * 0.3
            pt = center + QPointF(math.cos(spiral_angle) * dist, math.sin(spiral_angle) * dist)
            brightness = int(255 * (1 - dist / size))
            c = QColor.fromHsv(random.randint(200, 280), random.randint(50, 200), brightness)
            c.setAlpha(random.randint(150, 255))
            painter.setPen(QPen(c, random.uniform(0.5, 2)))
            painter.drawPoint(pt)

class ConstellationBrush:
    """Созвездие — соединённые звёзды."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 255, 200))
        size = settings.get('size', 15)
        density = settings.get('density', 6)
        points = []
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            points.append(pt)
        # Линии между ближайшими
        for i, p1 in enumerate(points):
            for j, p2 in enumerate(points):
                if i < j and math.hypot(p2.x() - p1.x(), p2.y() - p1.y()) < size:
                    c = QColor(color)
                    c.setAlpha(80)
                    painter.setPen(QPen(c, 0.5))
                    painter.drawLine(p1, p2)
        # Звёзды
        for pt in points:
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(pt, 2, 2)

# ============================================================================
# МАГИЧЕСКИЕ / ФЭНТЕЗИ
# ============================================================================

class RuneBrush:
    """Руны — магические символы."""
    RUNES = ['ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', 'ᚲ', 'ᚷ', 'ᚹ', 'ᚺ', 'ᚾ', 'ᛁ', 'ᛃ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛊ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ', 'ᛚ', 'ᛜ', 'ᛟ', 'ᛞ']
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 150, 255))
        size = settings.get('size', 10)
        density = settings.get('density', 3)
        font = QFont("Segoe UI Historic", int(size * 2))
        painter.setFont(font)
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size*2, size*2), random.uniform(-size*2, size*2))
            rune = random.choice(RuneBrush.RUNES)
            c = QColor(color)
            c.setAlpha(random.randint(150, 255))
            painter.setPen(QPen(c, 1))
            painter.drawText(pt, rune)

class ManaBrush:
    """Мана — потоки магической энергии."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 100, 255))
        size = settings.get('size', 8)
        density = settings.get('density', 15)
        for _ in range(density):
            t = random.random()
            pt = last_point + (current_point - last_point) * t
            perp = QPointF(-(current_point.y() - last_point.y()), current_point.x() - last_point.x())
            perp_len = math.hypot(perp.x(), perp.y())
            if perp_len > 0:
                perp = perp / perp_len
            offset = perp * math.sin(t * 15) * size
            c = QColor.fromHsv((color.hue() + int(t * 60)) % 360, 255, 255)
            c.setAlpha(random.randint(100, 200))
            painter.setPen(QPen(c, random.uniform(1, 3), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(pt + offset)

class PhoenixBrush:
    """Феникс — огненные перья."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 15)
        density = settings.get('density', 12)
        vec = current_point - last_point
        angle = math.atan2(vec.y(), vec.x())
        for _ in range(density):
            feather_angle = angle + random.uniform(-0.5, 0.5)
            length = random.uniform(5, size)
            end = current_point + QPointF(math.cos(feather_angle) * length, math.sin(feather_angle) * length)
            gradient = QLinearGradient(current_point, end)
            gradient.setColorAt(0, QColor(255, 200, 0, 255))
            gradient.setColorAt(0.5, QColor(255, 100, 0, 200))
            gradient.setColorAt(1, QColor(255, 0, 0, 0))
            painter.setPen(QPen(QBrush(gradient), random.uniform(1, 3), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(current_point, end)

# ============================================================================
# ОПТИЧЕСКИЕ ИЛЛЮЗИИ
# ============================================================================

class OpArtBrush:
    """Оп-арт — оптические иллюзии из линий."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 5)
        density = settings.get('density', 20)
        spacing = size / density
        painter.setPen(QPen(color, 1))
        for i in range(density):
            offset = i * spacing - size/2
            p1 = last_point + QPointF(offset, offset)
            p2 = current_point + QPointF(offset, offset)
            painter.drawLine(p1, p2)

class MoireBrush:
    """Муар — интерференционный узор."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 15)
        density = settings.get('density', 30)
        for i in range(density):
            angle = (i / density) * 2 * math.pi
            r = size * (i / density)
            pt = current_point + QPointF(math.cos(angle) * r, math.sin(angle) * r)
            c = QColor(color)
            c.setAlpha(int(255 * (1 - i/density)))
            painter.setPen(QPen(c, 1))
            painter.drawPoint(pt)

# ============================================================================
# ИНТЕРАКТИВНЫЕ / КОНТЕКСТНЫЕ
# ============================================================================

class GravityBrush:
    """Гравитация — капли стекают вниз."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 100, 255))
        size = settings.get('size', 8)
        density = settings.get('density', 10)
        for _ in range(density):
            start = current_point + QPointF(random.uniform(-size, size), 0)
            length = random.uniform(5, size * 3)
            end = start + QPointF(random.uniform(-2, 2), length)
            gradient = QLinearGradient(start, end)
            c = QColor(color)
            gradient.setColorAt(0, c)
            c_trans = QColor(color)
            c_trans.setAlpha(0)
            gradient.setColorAt(1, c_trans)
            painter.setPen(QPen(QBrush(gradient), random.uniform(1, 3)))
            painter.drawLine(start, end)
            # Капля
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(end, 2, 3)

class WindBrush:
    """Ветер — размытые горизонтальные штрихи."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 230, 255))
        size = settings.get('size', 20)
        density = settings.get('density', 15)
        for _ in range(density):
            start = current_point + QPointF(random.uniform(-size, size), random.uniform(-size/3, size/3))
            end = start + QPointF(random.uniform(10, size*2), random.uniform(-2, 2))
            c = QColor(color)
            c.setAlpha(random.randint(30, 100))
            painter.setPen(QPen(c, random.uniform(1, 3)))
            painter.drawLine(start, end)

class MagnetBrush:
    """Магнит — линии притягиваются к курсору."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 0, 0))
        size = settings.get('size', 15)
        density = settings.get('density', 20)
        center = current_point
        for _ in range(density):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(size * 0.5, size * 2)
            start = center + QPointF(math.cos(angle) * dist, math.sin(angle) * dist)
            end = center + QPointF(math.cos(angle) * dist * 0.3, math.sin(angle) * dist * 0.3)
            c = QColor(color)
            c.setAlpha(int(255 * (1 - dist / (size*2))))
            painter.setPen(QPen(c, random.uniform(0.5, 2)))
            painter.drawLine(start, end)

# custom_brushes.py
import math
import random
from PyQt6.QtCore import QPointF, Qt, QRectF, QLineF
from PyQt6.QtGui import (
    QPen, QColor, QPainterPath, QLinearGradient, QRadialGradient,
    QConicalGradient, QBrush, QPolygonF, QFont, QFontMetrics, QTransform
)

# ============================================================================
# ВСЕ ПРЕДЫДУЩИЕ КИСТИ ОСТАЮТСЯ (45 штук)
# ============================================================================
# ... (весь код из предыдущего ответа) ...

# ============================================================================
# ЗВУКОВЫЕ И ВИБРАЦИОННЫЕ
# ============================================================================

class SoundWaveBrush:
    """Звуковая волна — концентрические круги."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 150, 255))
        size = settings.get('size', 30)
        rings = settings.get('rings', 5)
        for i in range(rings):
            r = (i + 1) * (size / rings)
            c = QColor(color)
            c.setAlpha(int(255 * (1 - i/rings)))
            painter.setPen(QPen(c, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(current_point, r, r)

class SeismicBrush:
    """Сейсмическая волна — затухающая рябь."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 100, 50))
        size = settings.get('size', 40)
        waves = settings.get('waves', 8)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        angle = math.atan2(vec.y(), vec.x())
        for i in range(waves):
            t = i / waves
            r = size * t
            c = QColor(color)
            c.setAlpha(int(255 * (1 - t)))
            painter.setPen(QPen(c, 3 * (1 - t)))
            points = []
            for a in range(0, 360, 10):
                rad = math.radians(a)
                wave_r = r + math.sin(rad * 3 + t * 20) * 5
                points.append(current_point + QPointF(math.cos(rad) * wave_r, math.sin(rad) * wave_r))
            if len(points) > 2:
                polygon = QPolygonF(points)
                painter.drawPolyline(polygon)

class BassBrush:
    """Бас — низкочастотные вибрации."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 0, 255))
        size = settings.get('size', 25)
        density = settings.get('density', 10)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        for i in range(density):
            t = i / density
            pt = last_point + vec * t
            amplitude = math.sin(t * math.pi * 2) * size
            c = QColor(color)
            c.setAlpha(int(150 + 100 * abs(math.sin(t * math.pi * 2))))
            painter.setPen(QPen(c, 4))
            painter.drawLine(
                pt + QPointF(perp_x * amplitude * 0.5, perp_y * amplitude * 0.5),
                pt - QPointF(perp_x * amplitude * 0.5, perp_y * amplitude * 0.5)
            )

# ============================================================================
# БИОЛОГИЧЕСКИЕ И МЕДИЦИНСКИЕ
# ============================================================================

class CellBrush:
    """Клетки — биологические клетки с ядром."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 100, 150))
        size = settings.get('size', 20)
        density = settings.get('density', 4)
        for _ in range(density):
            center = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            r = random.uniform(5, size * 0.7)
            # Мембрана
            c = QColor(color)
            c.setAlpha(100)
            painter.setPen(QPen(c, 2))
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
            painter.drawEllipse(center, r, r)
            # Ядро
            nucleus_r = r * 0.3
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 150)))
            painter.drawEllipse(center, nucleus_r, nucleus_r)
            # Митохондрии
            for _ in range(3):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0.4, 0.8) * r
                org = center + QPointF(math.cos(angle) * dist, math.sin(angle) * dist)
                painter.setPen(QPen(color.darker(150), 1))
                painter.drawEllipse(org, 2, 1.5)

class BacteriaBrush:
    """Бактерии — палочки и кокки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 255, 100))
        size = settings.get('size', 15)
        density = settings.get('density', 10)
        for _ in range(density):
            pos = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            if random.random() > 0.5:
                # Кокк (круглая)
                r = random.uniform(2, 5)
                painter.setPen(QPen(color.darker(120), 1.5))
                painter.setBrush(QBrush(color))
                painter.drawEllipse(pos, r, r)
            else:
                # Палочка
                angle = random.uniform(0, 2 * math.pi)
                length = random.uniform(5, 10)
                width = random.uniform(1.5, 3)
                rect = QRectF(pos.x() - length/2, pos.y() - width/2, length, width)
                transform = QTransform()
                transform.translate(pos.x(), pos.y())
                transform.rotate(math.degrees(angle))
                transform.translate(-pos.x(), -pos.y())
                painter.save()
                painter.setTransform(transform)
                painter.setPen(QPen(color.darker(120), 1.5))
                painter.setBrush(QBrush(color))
                painter.drawRoundedRect(rect, width, width)
                painter.restore()

class NeuronBrush:
    """Нейроны — нервные клетки с дендритами."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 200, 100))
        size = settings.get('size', 25)
        center = current_point
        # Тело нейрона
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 100)))
        painter.drawEllipse(center, 8, 8)
        # Дендриты
        dendrites = settings.get('dendrites', 15)
        for _ in range(dendrites):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(10, size)
            end = center + QPointF(math.cos(angle) * length, math.sin(angle) * length)
            painter.setPen(QPen(color, 1.5))
            painter.drawLine(center, end)
            # Синапсы
            if random.random() > 0.7:
                painter.setPen(QPen(color.lighter(150), 3))
                painter.drawPoint(end)

class DNABrush:
    """ДНК — двойная спираль."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color1 = settings.get('color', QColor(255, 100, 100))
        color2 = QColor(100, 100, 255)
        size = settings.get('size', 20)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        steps = max(2, int(dist / 3))
        prev1 = last_point
        prev2 = last_point
        for i in range(1, steps + 1):
            t = i / steps
            pt = last_point + vec * t
            amplitude = size * math.sin(t * math.pi * 3)
            pt1 = pt + QPointF(perp_x * amplitude, perp_y * amplitude)
            pt2 = pt - QPointF(perp_x * amplitude, perp_y * amplitude)
            painter.setPen(QPen(color1, 2))
            painter.drawLine(prev1, pt1)
            painter.setPen(QPen(color2, 2))
            painter.drawLine(prev2, pt2)
            # Соединительные перекладины
            if i % 2 == 0:
                painter.setPen(QPen(QColor(200, 200, 200, 150), 1))
                painter.drawLine(pt1, pt2)
            prev1 = pt1
            prev2 = pt2

# ============================================================================
# ЖИДКОСТНЫЕ И ГАЗОВЫЕ
# ============================================================================

class WatercolorWashBrush:
    """Акварельная размывка — влажные потёки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 150, 255))
        size = settings.get('size', 30)
        density = settings.get('density', 20)
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            r = random.uniform(3, size * 0.7)
            gradient = QRadialGradient(pt, r)
            c = QColor(color)
            gradient.setColorAt(0, c)
            c_trans = QColor(color)
            c_trans.setAlpha(0)
            gradient.setColorAt(1, c_trans)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(pt, r, r)

class InkDropBrush:
    """Чернильная капля — растекающиеся кляксы."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 100))
        size = settings.get('size', 25)
        # Основная капля
        path = QPainterPath()
        center = current_point
        path.moveTo(center + QPointF(0, -size))
        # Создаём неправильную форму
        num_points = 12
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            r = size * (0.7 + random.uniform(0, 0.5))
            pt = center + QPointF(math.cos(angle) * r, math.sin(angle) * r * 0.7)
            if i == 0:
                path.lineTo(pt)
            else:
                ctrl1 = center + QPointF(math.cos(angle - 0.3) * r * 0.8, math.sin(angle - 0.3) * r * 0.8 * 0.7)
                ctrl2 = center + QPointF(math.cos(angle - 0.1) * r * 0.9, math.sin(angle - 0.1) * r * 0.9 * 0.7)
                path.cubicTo(ctrl1, ctrl2, pt)
        path.closeSubpath()
        painter.setPen(QPen(color.darker(150), 1))
        painter.setBrush(QBrush(color))
        painter.drawPath(path)
        # Блик
        highlight = center + QPointF(-size*0.2, -size*0.3)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.drawEllipse(highlight, size*0.15, size*0.12)

class SteamBrush:
    """Пар — поднимающиеся клубы."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 30)
        density = settings.get('density', 15)
        for _ in range(density):
            start = current_point + QPointF(random.uniform(-size/2, size/2), 0)
            height = random.uniform(10, size * 2)
            width = random.uniform(5, size)
            gradient = QLinearGradient(start, start - QPointF(0, height))
            gradient.setColorAt(0, QColor(255, 255, 255, 100))
            gradient.setColorAt(0.5, QColor(200, 200, 200, 50))
            gradient.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(gradient), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(start, start - QPointF(random.uniform(-3, 3), height))

# ============================================================================
# АРХИТЕКТУРНЫЕ И СТРУКТУРНЫЕ
# ============================================================================

class BrickWallBrush:
    """Кирпичная стена — кладка кирпичей."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(180, 100, 60))
        size = settings.get('size', 20)
        brick_w = size
        brick_h = size * 0.4
        gap = 2
        vec = current_point - last_point
        steps = max(1, int(vec.manhattanLength() / brick_w))
        for i in range(steps):
            t = i / steps
            pt = last_point + vec * t
            col = int(pt.x() / (brick_w + gap))
            row = int(pt.y() / (brick_h + gap))
            x = col * (brick_w + gap)
            y = row * (brick_h + gap)
            if row % 2 == 1:
                x += brick_w / 2
            rect = QRectF(x, y, brick_w, brick_h)
            c = QColor(color.red() + random.randint(-20, 20),
                      color.green() + random.randint(-20, 20),
                      color.blue() + random.randint(-20, 20))
            painter.setPen(QPen(c.darker(150), 1))
            painter.setBrush(QBrush(c))
            painter.drawRect(rect)

class ChainBrush:
    """Цепь — звенья цепи."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(150, 150, 150))
        size = settings.get('size', 10)
        link_length = size * 2
        link_width = size
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        num_links = max(1, int(dist / link_length))
        angle = math.atan2(vec.y(), vec.x())
        perp_angle = angle + math.pi / 2
        for i in range(num_links):
            t = (i + 0.5) / num_links
            pt = last_point + vec * t
            # Чередуем ориентацию звеньев
            if i % 2 == 0:
                rect = QRectF(pt.x() - link_length/2, pt.y() - link_width/2, link_length, link_width)
            else:
                rect = QRectF(pt.x() - link_width/2, pt.y() - link_length/2, link_width, link_length)
            transform = QTransform()
            transform.translate(pt.x(), pt.y())
            transform.rotate(math.degrees(angle))
            transform.translate(-pt.x(), -pt.y())
            painter.save()
            painter.setTransform(transform)
            painter.setPen(QPen(color.darker(150), 2))
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(rect, link_width/3, link_width/3)
            painter.restore()

class ScaffoldBrush:
    """Строительные леса — перекрещивающиеся балки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(180, 140, 100))
        size = settings.get('size', 30)
        spacing = size / 3
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        painter.setPen(QPen(color, 2))
        # Вертикали
        for x in range(-int(size), int(size) + 1, int(spacing)):
            pt = current_point + QPointF(perp_x * x, perp_y * x)
            painter.drawLine(pt + QPointF(-vec.x()*0.5, -vec.y()*0.5), 
                           pt + QPointF(vec.x()*0.5, vec.y()*0.5))
        # Горизонтали
        painter.setPen(QPen(color.darker(120), 1.5))
        for y in range(-int(size/2), int(size/2) + 1, int(spacing)):
            t = y / size
            pt = current_point + QPointF(-perp_x * size, -perp_y * size) * t
            painter.drawLine(pt + QPointF(perp_x * size, perp_y * size),
                           pt - QPointF(perp_x * size, perp_y * size))

# ============================================================================
# ЕДА И НАПИТКИ
# ============================================================================

class SprinklesBrush:
    """Посыпка — кондитерская обсыпка."""
    COLORS = [QColor(255, 100, 100), QColor(100, 255, 100), QColor(100, 100, 255),
              QColor(255, 255, 100), QColor(255, 150, 50), QColor(200, 100, 255)]
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        density = settings.get('density', 30)
        size = settings.get('size', 8)
        for _ in range(density):
            pos = current_point + QPointF(random.uniform(-size*2, size*2), random.uniform(-size*2, size*2))
            color = random.choice(SprinklesBrush.COLORS)
            angle = random.uniform(0, math.pi)
            length = random.uniform(3, 7)
            width = random.uniform(1, 2)
            rect = QRectF(pos.x() - length/2, pos.y() - width/2, length, width)
            transform = QTransform()
            transform.translate(pos.x(), pos.y())
            transform.rotate(math.degrees(angle))
            transform.translate(-pos.x(), -pos.y())
            painter.save()
            painter.setTransform(transform)
            painter.setPen(QPen(color.darker(120), 0.5))
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(rect, width, width)
            painter.restore()

class CoffeeBrush:
    """Кофе — следы от чашки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = QColor(139, 90, 43)
        size = settings.get('size', 20)
        # Кольцо от чашки
        painter.setPen(QPen(color, 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(current_point, size, size)
        # Пятно кофе
        for _ in range(20):
            pos = current_point + QPointF(random.uniform(-size*0.8, size*0.8), 
                                         random.uniform(-size*0.8, size*0.8))
            if math.hypot(pos.x() - current_point.x(), pos.y() - current_point.y()) < size:
                c = QColor(color)
                c.setAlpha(random.randint(50, 150))
                painter.setPen(QPen(c, 1))
                painter.drawPoint(pos)

# ============================================================================
# МУЗЫКАЛЬНЫЕ
# ============================================================================

class MusicNotesBrush:
    """Ноты — музыкальные символы."""
    NOTES = ['♪', '♫', '♩', '♬', '♭', '♯', '𝄞']
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 15)
        density = settings.get('density', 5)
        font = QFont("Segoe UI Symbol", int(size))
        painter.setFont(font)
        for _ in range(density):
            pos = current_point + QPointF(random.uniform(-size*2, size*2), random.uniform(-size*2, size*2))
            note = random.choice(MusicNotesBrush.NOTES)
            c = QColor(color)
            c.setAlpha(random.randint(150, 255))
            painter.setPen(QPen(c, 1))
            painter.drawText(pos, note)

class SoundEqualizerBrush:
    """Эквалайзер — столбики звука."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 255, 100))
        size = settings.get('size', 20)
        bars = settings.get('bars', 10)
        bar_width = (size * 2) / bars
        for i in range(bars):
            x = current_point.x() - size + i * bar_width
            height = random.uniform(5, size * 1.5)
            y = current_point.y()
            gradient = QLinearGradient(QPointF(x, y), QPointF(x, y - height))
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 50))
            painter.setPen(QPen(color, 1))
            painter.setBrush(QBrush(gradient))
            painter.drawRect(QRectF(x, y - height, bar_width - 1, height))

# ============================================================================
# ТЕХНОЛОГИЧЕСКИЕ
# ============================================================================

class QRCodeBrush:
    """QR-код — генерация случайных модулей."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 15)
        module_size = size / 7
        for row in range(7):
            for col in range(7):
                if random.random() > 0.5:
                    x = current_point.x() + col * module_size
                    y = current_point.y() + row * module_size
                    painter.fillRect(QRectF(x, y, module_size, module_size), color)

class MatrixBrush:
    """Матрица — падающие зелёные символы."""
    CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン1234567890'
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = QColor(0, 255, 0)
        size = settings.get('size', 12)
        density = settings.get('density', 15)
        font = QFont("MS Gothic", int(size))
        painter.setFont(font)
        for _ in range(density):
            pos = current_point + QPointF(random.uniform(-size*3, size*3), random.uniform(-size*5, size))
            char = random.choice(MatrixBrush.CHARS)
            c = QColor(color)
            c.setAlpha(random.randint(100, 255))
            painter.setPen(QPen(c, 1))
            painter.drawText(pos, char)

# ============================================================================
# ПРИРОДНЫЕ ЯВЛЕНИЯ
# ============================================================================

class RainbowSprayBrush:
    """Радужный спрей — спектральные брызги."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 20)
        density = settings.get('density', 40)
        for _ in range(density):
            hue = random.randint(0, 360)
            color = QColor.fromHsv(hue, 255, 255)
            offset = QPointF(random.uniform(-size, size), random.uniform(-size, size))
            painter.setPen(QPen(color, 1))
            painter.drawPoint(current_point + offset)

class AuroraBrush:
    """Северное сияние — переливающиеся занавеси."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 50)
        density = settings.get('density', 30)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        for i in range(density):
            t = i / density
            pt = last_point + vec * t
            amplitude = math.sin(t * 8) * size * (1 - abs(t - 0.5) * 2)
            hue = int(180 + t * 120) % 360
            color = QColor.fromHsv(hue, 150, 255, 100)
            painter.setPen(QPen(color, random.uniform(2, 6)))
            wave_pt = pt + QPointF(perp_x * amplitude, perp_y * amplitude)
            painter.drawLine(pt, wave_pt)

class TornadoBrush:
    """Торнадо — закрученный вихрь."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(150, 150, 150))
        size = settings.get('size', 30)
        height = size * 3
        density = settings.get('density', 30)
        for i in range(density):
            t = i / density
            y = current_point.y() - height * t
            r = size * t * 0.3
            angle = t * 20 + (i * 0.5)
            x = current_point.x() + math.cos(angle) * r
            c = QColor(color)
            c.setAlpha(int(255 * (1 - t)))
            painter.setPen(QPen(c, random.uniform(1, 3)))
            painter.drawPoint(QPointF(x, y))

# ============================================================================
# КАЛЛИГРАФИЧЕСКИЕ И ХУДОЖЕСТВЕННЫЕ
# ============================================================================

class SumiBrush:
    """Суми-э — японская тушь с сухой кистью."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = QColor(30, 30, 30)
        size = settings.get('size', 10)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        steps = max(2, int(dist))
        for i in range(steps):
            t = i / steps
            pt = last_point + vec * t
            pressure = 1 - abs(t - 0.5) * 1.5
            current_size = max(1, size * pressure)
            # Эффект сухой кисти
            if random.random() > pressure:
                continue
            c = QColor(color.red(), color.green(), color.blue(), 
                      int(200 * pressure * (0.5 + random.random() * 0.5)))
            painter.setPen(QPen(c, current_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(pt)

class CharcoalBrush:
    """Уголь — шероховатая линия с осыпанием."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = QColor(40, 40, 40)
        size = settings.get('size', 8)
        density = settings.get('density', 20)
        vec = current_point - last_point
        # Основная линия с вариацией
        steps = max(2, int(math.hypot(vec.x(), vec.y()) / 2))
        for i in range(steps):
            t = i / steps
            pt = last_point + vec * t
            offset = QPointF(random.uniform(-2, 2), random.uniform(-2, 2))
            c = QColor(color.red(), color.green(), color.blue(), random.randint(100, 200))
            painter.setPen(QPen(c, random.uniform(1, size), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(pt + offset)
        # Осыпание
        for _ in range(density):
            offset = QPointF(random.uniform(-size*2, size*2), random.uniform(-size*2, size*2))
            if random.random() > 0.5:
                c = QColor(color.red(), color.green(), color.blue(), random.randint(50, 150))
                painter.setPen(QPen(c, random.uniform(0.5, 2)))
                painter.drawPoint(current_point + offset)

# ============================================================================
# АБСТРАКТНЫЕ И СЮРРЕАЛИСТИЧЕСКИЕ
# ============================================================================

class DaliBrush:
    """Дали — плавящиеся часы и искажения."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 150, 100))
        size = settings.get('size', 15)
        path = QPainterPath()
        path.moveTo(last_point)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 2:
            return
        steps = max(3, int(dist / 2))
        for i in range(1, steps + 1):
            t = i / steps
            pt = last_point + vec * t
            # Искажение "плавления"
            droop = math.sin(t * math.pi) * size * 2
            pt = pt + QPointF(0, droop)
            if i == 1:
                path.lineTo(pt)
            else:
                ctrl = last_point + vec * (t - 0.5/steps) + QPointF(random.uniform(-5, 5), droop * 0.5)
                path.quadTo(ctrl, pt)
        painter.setPen(QPen(color, size * 0.3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

class EscherBrush:
    """Эшер — невозможные фигуры."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 20)
        # Рисуем треугольник Пенроуза
        pts = []
        for i in range(3):
            angle = 2 * math.pi / 3 * i - math.pi / 2
            pts.append(current_point + QPointF(math.cos(angle) * size, math.sin(angle) * size))
        painter.setPen(QPen(color, 2))
        for i in range(3):
            j = (i + 1) % 3
            # Искажаем линию для иллюзии
            mid = (pts[i] + pts[j]) / 2
            perp = QPointF(-(pts[j].y() - pts[i].y()), pts[j].x() - pts[i].x())
            perp_len = math.hypot(perp.x(), perp.y())
            if perp_len > 0:
                perp = perp / perp_len
            mid = mid + perp * size * 0.2
            painter.drawLine(pts[i], mid)
            painter.drawLine(mid, pts[j])

class PollockBrush:
    """Поллок — капельная живопись."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 30)
        density = settings.get('density', 50)
        for _ in range(density):
            color = QColor.fromHsv(random.randint(0, 360), random.randint(100, 255), random.randint(100, 255))
            start = current_point + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            end = start + QPointF(random.uniform(-size, size), random.uniform(-size, size))
            painter.setPen(QPen(color, random.uniform(0.5, 3)))
            # Капли и брызги
            if random.random() > 0.7:
                painter.drawLine(start, end)
            else:
                painter.drawPoint(start)
                for _ in range(random.randint(1, 5)):
                    splat = start + QPointF(random.uniform(-5, 5), random.uniform(-5, 5))
                    painter.drawPoint(splat)

# ============================================================================
# СКЕТЧИНГ И РИСОВАНИЕ КАРАНДАШОМ
# ============================================================================

class SketchingPencilBrush:
    """Скетчинг-карандаш — мягкие наброски с разной плотностью."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(50, 50, 50))
        size = settings.get('size', 3)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        steps = max(2, int(dist / 1.5))
        for i in range(steps):
            t = i / steps
            pt = last_point + vec * t
            # Имитация текстуры карандаша
            pressure = 0.5 + 0.5 * math.sin(t * math.pi)  # Нажим меняется
            if random.random() > pressure:
                continue
            # Мелкие штрихи под углом
            angle = random.uniform(-0.3, 0.3) + math.pi/4
            line_length = size * random.uniform(0.5, 2)
            end_pt = pt + QPointF(math.cos(angle) * line_length, math.sin(angle) * line_length)
            c = QColor(color)
            c.setAlpha(int(255 * pressure * (0.3 + random.random() * 0.7)))
            painter.setPen(QPen(c, random.uniform(0.3, 1.2)))
            painter.drawLine(pt, end_pt)

class HatchingBrush:
    """Штриховка — параллельные линии для тонирования."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(30, 30, 30))
        size = settings.get('size', 8)
        density = settings.get('density', 12)
        angle = settings.get('hatch_angle', 45)
        rad = math.radians(angle)
        dx = math.cos(rad) * size * 0.3
        dy = math.sin(rad) * size * 0.3
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        for i in range(density):
            offset = (i - density/2) * size * 0.4
            start = current_point + QPointF(perp_x * offset - dx, perp_y * offset - dy)
            end = current_point + QPointF(perp_x * offset + dx, perp_y * offset + dy)
            c = QColor(color)
            c.setAlpha(random.randint(100, 200))
            painter.setPen(QPen(c, random.uniform(0.5, 1.5)))
            painter.drawLine(start, end)

class GestureBrush:
    """Жестовая кисть — быстрые экспрессивные линии."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(40, 40, 40))
        size = settings.get('size', 6)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        # Основная динамическая линия
        painter.setPen(QPen(color, size * 0.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(last_point, current_point)
        # Хвосты-росчерки на концах
        angle = math.atan2(vec.y(), vec.x())
        for sign in [-1, 1]:
            tail_length = random.uniform(size * 2, size * 5)
            tail_angle = angle + sign * random.uniform(0.2, 0.5)
            tail_end = current_point + QPointF(math.cos(tail_angle) * tail_length, 
                                               math.sin(tail_angle) * tail_length)
            c = QColor(color)
            c.setAlpha(100)
            painter.setPen(QPen(c, size * 0.3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(current_point, tail_end)

# ============================================================================
# КОНЦЕПТ-АРТ И ДИЗАЙН
# ============================================================================

class ConceptSketchBrush:
    """Концепт-скетч — быстрые дизайнерские наброски."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(60, 60, 70))
        size = settings.get('size', 5)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        steps = max(3, int(dist / 2))
        for i in range(steps):
            t = i / steps
            pt = last_point + vec * t
            # Имитация быстрой линии дизайнера
            wobble = math.sin(t * 15) * size * 0.3
            offset = QPointF(
                (-vec.y() / dist) * wobble if dist > 0 else 0,
                (vec.x() / dist) * wobble if dist > 0 else 0
            )
            c = QColor(color)
            c.setAlpha(int(200 + 55 * math.sin(t * 20)))
            painter.setPen(QPen(c, size * (0.8 + 0.4 * math.sin(t * 10)), 
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(pt + offset)

class SilhouetteBrush:
    """Силуэт — заливка с рваным краем."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(20, 20, 20))
        size = settings.get('size', 20)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        # Рисуем неровную широкую линию
        path = QPainterPath()
        path.moveTo(last_point + QPointF(perp_x * size * 0.3, perp_y * size * 0.3))
        steps = max(2, int(dist / 3))
        for i in range(steps + 1):
            t = i / steps
            pt = last_point + vec * t
            roughness = size * (0.5 + 0.5 * math.sin(t * 12) * random.uniform(-1, 1))
            path.lineTo(pt + QPointF(perp_x * roughness, perp_y * roughness))
        for i in range(steps, -1, -1):
            t = i / steps
            pt = last_point + vec * t
            roughness = size * (0.3 + 0.7 * math.cos(t * 12) * random.uniform(-1, 1))
            path.lineTo(pt - QPointF(perp_x * roughness, perp_y * roughness))
        path.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPath(path)

class SpeedPaintBrush:
    """Спидпейнт — быстрая живопись широкими мазками."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(150, 100, 80))
        size = settings.get('size', 25)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        # Широкий мазок с текстурой
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        for i in range(5):
            offset = (i - 2) * size * 0.15
            start = last_point + QPointF(perp_x * offset, perp_y * offset)
            end = current_point + QPointF(perp_x * offset, perp_y * offset)
            c = QColor(color)
            c.setAlpha(random.randint(100, 200))
            painter.setPen(QPen(c, random.uniform(size*0.3, size*0.8), 
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(start, end)

# ============================================================================
# КОМИКСЫ И МАНГА
# ============================================================================

class MangaToneBrush:
    """Манга-тон — растровые точки для теней."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 15)
        density = settings.get('density', 30)
        spacing = size / 6
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if random.random() > 0.7:  # Плотность тона
                    continue
                x = current_point.x() + dx * spacing + random.uniform(-1, 1)
                y = current_point.y() + dy * spacing + random.uniform(-1, 1)
                c = QColor(color)
                c.setAlpha(random.randint(100, 255))
                painter.setPen(QPen(c, random.uniform(0.5, 1.5)))
                painter.drawPoint(QPointF(x, y))

class ComicInkBrush:
    """Комикс-инк — чистая линия с переменной толщиной."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = QColor(0, 0, 0)
        size = settings.get('size', 4)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        # Имитация пера для комиксов (G-pen)
        angle = math.atan2(vec.y(), vec.x())
        perp_angle = angle + math.pi / 2
        for i in range(3):
            t = i / 2  # 0, 0.5, 1.0
            pt = last_point + vec * t
            # Давление пера зависит от направления (вертикаль - толще)
            pressure = 0.4 + 0.6 * abs(math.sin(angle))
            current_size = size * pressure * (1.2 if i == 1 else 1.0)
            c = QColor(color)
            c.setAlpha(int(255 * pressure))
            painter.setPen(QPen(c, current_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            if i < 2:
                next_pt = last_point + vec * ((i + 1) / 2)
                painter.drawLine(pt, next_pt)

class ScreentoneBrush:
    """Скринтон — полупрозрачные паттерны."""
    PATTERNS = ['dots', 'lines', 'crosshatch', 'gradient']
    
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 20)
        pattern = settings.get('screen_pattern', 'dots')
        for x in range(-int(size), int(size) + 1, 3):
            for y in range(-int(size), int(size) + 1, 3):
                pt = QPointF(current_point.x() + x, current_point.y() + y)
                if math.hypot(x, y) > size:
                    continue
                alpha = 255 - int(math.hypot(x, y) / size * 200)
                c = QColor(color)
                c.setAlpha(alpha)
                painter.setPen(QPen(c, 1))
                if pattern == 'dots':
                    if (x + y) % 6 == 0:
                        painter.drawPoint(pt)
                elif pattern == 'lines':
                    if y % 4 == 0:
                        painter.drawPoint(pt)
                elif pattern == 'crosshatch':
                    if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                        painter.drawPoint(pt)

# ============================================================================
# ЛЕТТЕРИНГ И КАЛЛИГРАФИЯ
# ============================================================================

class CalligraphyBrush:
    """Каллиграфия — широкое перо под углом."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(20, 20, 20))
        size = settings.get('size', 12)
        angle = settings.get('nib_angle', 45)  # Угол пера
        rad = math.radians(angle)
        # Рисуем линию пером под постоянным углом
        painter.setPen(QPen(color, size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.drawLine(last_point, current_point)

class BrushPenBrush:
    """Брашпен — кистевая ручка с нажимом."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(0, 0, 0))
        size = settings.get('size', 8)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        steps = max(3, int(dist))
        for i in range(steps):
            t = i / steps
            pt = last_point + vec * t
            # Имитация нажима брашпена
            pressure = math.sin(t * math.pi)
            current_size = size * (0.3 + 0.7 * pressure)
            c = QColor(color)
            c.setAlpha(int(200 * pressure + 55))
            painter.setPen(QPen(c, current_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(pt)

class GraffitiBrush:
    """Граффити — аэрозольный баллончик."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 0, 100))
        size = settings.get('size', 25)
        density = settings.get('density', 50)
        # Внешний ореол спрея
        for _ in range(density * 2):
            offset = QPointF(random.uniform(-size*1.5, size*1.5), 
                           random.uniform(-size*1.5, size*1.5))
            distance = math.hypot(offset.x(), offset.y())
            if distance < size * 1.5:
                c = QColor(color)
                c.setAlpha(int(255 * (1 - distance/(size*1.5)) * random.uniform(0.3, 0.7)))
                painter.setPen(QPen(c, random.uniform(0.5, 2)))
                painter.drawPoint(current_point + offset)
        # Центральная линия
        painter.setPen(QPen(color, size * 0.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(last_point, current_point)

# ============================================================================
# ЦИФРОВАЯ ЖИВОПИСЬ
# ============================================================================

class DigitalOilBrush:
    """Цифровое масло — объёмные мазки с блендингом."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(200, 150, 100))
        size = settings.get('size', 20)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        # Несколько слоёв мазка
        for layer in range(3):
            offset = (layer - 1) * size * 0.2
            perp_x = -vec.y() / dist if dist > 0 else 0
            perp_y = vec.x() / dist if dist > 0 else 0
            start = last_point + QPointF(perp_x * offset, perp_y * offset)
            end = current_point + QPointF(perp_x * offset, perp_y * offset)
            c = QColor(color)
            c.setAlpha(150 - layer * 30)
            painter.setPen(QPen(c, size * (1 - layer * 0.2), 
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(start, end)

class ImpastoBrush:
    """Импасто — густые пастозные мазки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 200, 100))
        size = settings.get('size', 18)
        density = settings.get('density', 15)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        for _ in range(density):
            t = random.random()
            pt = last_point + vec * t
            offset = QPointF(random.uniform(-size*0.5, size*0.5),
                           random.uniform(-size*0.5, size*0.5))
            c = QColor(color)
            c.setAlpha(random.randint(150, 255))
            # Объёмный мазок с бликом
            painter.setPen(QPen(c.darker(120), 1))
            painter.setBrush(QBrush(c))
            r = random.uniform(2, size * 0.4)
            painter.drawEllipse(pt + offset, r, r * 0.7)
            # Блик
            highlight = pt + offset + QPointF(-r*0.3, -r*0.3)
            painter.setPen(QPen(QColor(255, 255, 255, 100), 0.5))
            painter.drawEllipse(highlight, r*0.2, r*0.15)

class PaletteKnifeBrush:
    """Мастихин — широкие плоские мазки."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 150, 200))
        size = settings.get('size', 30)
        vec = current_point - last_point
        dist = math.hypot(vec.x(), vec.y())
        if dist < 1:
            return
        perp_x = -vec.y() / dist
        perp_y = vec.x() / dist
        # Плоский прямоугольный мазок
        rect = QRectF(last_point.x() - size*0.7, last_point.y() - size*0.2,
                     dist + size*0.4, size * 0.8)
        angle = math.degrees(math.atan2(vec.y(), vec.x()))
        transform = QTransform()
        transform.translate(last_point.x(), last_point.y())
        transform.rotate(angle)
        transform.translate(-last_point.x(), -last_point.y())
        painter.save()
        painter.setTransform(transform)
        c = QColor(color)
        c.setAlpha(200)
        painter.setPen(QPen(c.darker(130), 1))
        painter.setBrush(QBrush(c))
        painter.drawRoundedRect(rect, size*0.2, size*0.2)
        painter.restore()

# ============================================================================
# ЭФФЕКТЫ И ТЕКСТУРЫ ДЛЯ ХУДОЖНИКОВ
# ============================================================================

class BlenderBrush:
    """Блендер — размытие и смешивание."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        size = settings.get('size', 25)
        # Мягкая полупрозрачная кисть для смешивания
        gradient = QRadialGradient(current_point, size)
        gradient.setColorAt(0, QColor(255, 255, 255, 30))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 15))
        gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(current_point, size, size)

class TextureStencilBrush:
    """Текстурный трафарет — наложение текстуры."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 100, 100))
        size = settings.get('size', 25)
        density = settings.get('density', 40)
        for _ in range(density):
            pt = current_point + QPointF(random.uniform(-size, size), 
                                        random.uniform(-size, size))
            # Создаём микро-текстуру из точек и коротких линий
            if random.random() > 0.5:
                angle = random.uniform(0, 2 * math.pi)
                length = random.uniform(1, 4)
                end = pt + QPointF(math.cos(angle) * length, math.sin(angle) * length)
                c = QColor(color)
                c.setAlpha(random.randint(50, 150))
                painter.setPen(QPen(c, 0.5))
                painter.drawLine(pt, end)
            else:
                c = QColor(color)
                c.setAlpha(random.randint(30, 120))
                painter.setPen(QPen(c, random.uniform(0.5, 1.5)))
                painter.drawPoint(pt)

class GlazeBrush:
    """Лессировка — тонкие прозрачные слои."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 200, 150))
        size = settings.get('size', 30)
        steps = 5
        for i in range(steps):
            t = i / steps
            pt = last_point + (current_point - last_point) * t
            gradient = QRadialGradient(pt, size * (1 - t * 0.5))
            c = QColor(color)
            c.setAlpha(int(50 * (1 - t * 0.5)))
            gradient.setColorAt(0, c)
            gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(pt, size * (1 - t * 0.5), size * (1 - t * 0.5))

# ============================================================================
# СПЕЦИАЛЬНЫЕ ХУДОЖЕСТВЕННЫЕ ИНСТРУМЕНТЫ
# ============================================================================

class PerspectiveBrush:
    """Перспектива — линии, сходящиеся в точку схода."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(100, 150, 255))
        size = settings.get('size', 2)
        rays = settings.get('rays', 12)
        vanishing_point = settings.get('vanishing_point', current_point + QPointF(200, -200))
        for i in range(rays):
            angle = (2 * math.pi / rays) * i
            # Точка на окружности вокруг текущей позиции
            circle_pt = current_point + QPointF(math.cos(angle) * 50, math.sin(angle) * 50)
            c = QColor(color)
            c.setAlpha(100)
            painter.setPen(QPen(c, size, Qt.PenStyle.DashLine))
            painter.drawLine(circle_pt, vanishing_point)

class GridPerspectiveBrush:
    """Сетка перспективы — пол с сеткой."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(150, 150, 150))
        size = settings.get('size', 50)
        grid_size = settings.get('grid_div', 10)
        # Горизонтальные линии
        for i in range(1, grid_size):
            y = current_point.y() + i * (size / grid_size)
            start_x = current_point.x() - size * (i / grid_size)
            end_x = current_point.x() + size * (i / grid_size)
            c = QColor(color)
            c.setAlpha(int(255 * (1 - i/grid_size)))
            painter.setPen(QPen(c, 0.5))
            painter.drawLine(QPointF(start_x, y), QPointF(end_x, y))
        # Вертикальные линии (радиальные)
        for i in range(grid_size * 2):
            x = current_point.x() - size + i * (size * 2) / (grid_size * 2)
            start_y = current_point.y()
            end_y = current_point.y() + size
            c = QColor(color)
            c.setAlpha(100)
            painter.setPen(QPen(c, 0.5))
            painter.drawLine(QPointF(x, start_y), 
                           QPointF(current_point.x() + (x - current_point.x()) * 2, end_y))

class LightRayBrush:
    """Световые лучи — объёмное освещение."""
    @staticmethod
    def draw(painter, last_point, current_point, settings):
        color = settings.get('color', QColor(255, 255, 200))
        size = settings.get('size', 40)
        rays = settings.get('rays', 8)
        source = current_point
        for i in range(rays):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(size * 0.5, size * 2)
            width = random.uniform(2, size * 0.3)
            end = source + QPointF(math.cos(angle) * length, math.sin(angle) * length)
            gradient = QLinearGradient(source, end)
            c = QColor(color)
            gradient.setColorAt(0, c)
            c_trans = QColor(color)
            c_trans.setAlpha(0)
            gradient.setColorAt(1, c_trans)
            painter.setPen(QPen(QBrush(gradient), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(source, end)


# ============================================================================
# ОБНОВЛЁННЫЙ СЛОВАРЬ ВСЕХ КИСТЕЙ
# ============================================================================

CUSTOM_BRUSHES = {
    # Предыдущие 45
    'splatter': 'Брызги',
    'glow': 'Свечение',
    'rainbow': 'Радужная',
    'fur': 'Мех',
    'pixel': 'Пиксельная',
    'neon': 'Неон',
    'ribbon': 'Лента',
    'engraving': 'Гравировка',
    'fire': 'Огонь',
    'smoke': 'Дым',
    'bubbles': 'Пузыри',
    'sparks': 'Искры',
    'vine': 'Лианы',
    'grass': 'Трава',
    'coral': 'Кораллы',
    'furball': 'Пушистик',
    'kaleidoscope': 'Калейдоскоп',
    'lightning': 'Молния',
    'circuit': 'Микросхема',
    'hexgrid': 'Соты',
    'fractal': 'Фрактал',
    'crumble': 'Крошка',
    'canvas': 'Холст',
    'rust': 'Ржавчина',
    'emoji': 'Эмодзи',
    'ascii': 'ASCII-арт',
    'morse': 'Морзе',
    'galaxy': 'Галактика',
    'constellation': 'Созвездие',
    'rune': 'Руны',
    'mana': 'Мана',
    'phoenix': 'Феникс',
    'opart': 'Оп-арт',
    'moire': 'Муар',
    'gravity': 'Гравитация',
    'wind': 'Ветер',
    'magnet': 'Магнит',
    
    # Новые 35
    'soundwave': 'Звуковая волна',
    'seismic': 'Сейсмическая',
    'bass': 'Бас',
    'cell': 'Клетки',
    'bacteria': 'Бактерии',
    'neuron': 'Нейроны',
    'dna': 'ДНК',
    'watercolor_wash': 'Акварель',
    'inkdrop': 'Чернила',
    'steam': 'Пар',
    'brickwall': 'Кирпичи',
    'chain': 'Цепь',
    'scaffold': 'Леса',
    'sprinkles': 'Посыпка',
    'coffee': 'Кофе',
    'musicnotes': 'Ноты',
    'equalizer': 'Эквалайзер',
    'qrcode': 'QR-код',
    'matrix': 'Матрица',
    'rainbow_spray': 'Радужный спрей',
    'aurora': 'Аврора',
    'tornado': 'Торнадо',
    'sumi': 'Суми-э',
    'charcoal': 'Уголь',
    'dali': 'Дали',
    'escher': 'Эшер',
    'pollock': 'Поллок',

        # Скетчинг
    'sketching_pencil': 'Скетч-карандаш',
    'hatching': 'Штриховка',
    'gesture': 'Жестовая',
    
    # Концепт-арт
    'concept_sketch': 'Концепт-скетч',
    'silhouette': 'Силуэт',
    'speed_paint': 'Спидпейнт',
    
    # Комиксы
    'manga_tone': 'Манга-тон',
    'comic_ink': 'Комикс-инк',
    'screentone': 'Скринтон',
    
    # Леттеринг
    'calligraphy_nib': 'Каллиграфия',
    'brush_pen': 'Брашпен',
    'graffiti': 'Граффити',
    
    # Цифровая живопись
    'digital_oil': 'Цифровое масло',
    'impasto': 'Импасто',
    'palette_knife': 'Мастихин',
    
    # Эффекты
    'blender': 'Блендер',
    'texture_stencil': 'Текстурный трафарет',
    'glaze': 'Лессировка',
    
    # Специальные
    'perspective': 'Перспектива',
    'grid_perspective': 'Сетка перспективы',
    'light_ray': 'Световые лучи',

}

def apply_brush(tool, painter, last_point, current_point, settings):
    """Вызов нужной кисти по имени инструмента."""
    brushes = {
        # Все 80 кистей
        
        'sketching_pencil': SketchingPencilBrush,
        'hatching': HatchingBrush,
        'gesture': GestureBrush,
        'concept_sketch': ConceptSketchBrush,
        'silhouette': SilhouetteBrush,
        'speed_paint': SpeedPaintBrush,
        'manga_tone': MangaToneBrush,
        'comic_ink': ComicInkBrush,
        'screentone': ScreentoneBrush,
        'calligraphy_nib': CalligraphyBrush,
        'brush_pen': BrushPenBrush,
        'graffiti': GraffitiBrush,
        'digital_oil': DigitalOilBrush,
        'impasto': ImpastoBrush,
        'palette_knife': PaletteKnifeBrush,
        'blender': BlenderBrush,
        'texture_stencil': TextureStencilBrush,
        'glaze': GlazeBrush,
        'perspective': PerspectiveBrush,
        'grid_perspective': GridPerspectiveBrush,
        'light_ray': LightRayBrush,
        'splatter': SplatterBrush,
        'glow': GlowBrush,
        'rainbow': RainbowBrush,
        'fur': FurBrush,
        'pixel': PixelBrush,
        'neon': NeonBrush,
        'ribbon': RibbonBrush,
        'engraving': EngravingBrush,
        'fire': FireBrush,
        'smoke': SmokeBrush,
        'bubbles': BubblesBrush,
        'sparks': SparksBrush,
        'vine': VineBrush,
        'grass': GrassBrush,
        'coral': CoralBrush,
        'furball': FurballBrush,
        'kaleidoscope': KaleidoscopeBrush,
        'lightning': LightningBrush,
        'circuit': CircuitBrush,
        'hexgrid': HexGridBrush,
        'fractal': FractalBrush,
        'crumble': CrumbleBrush,
        'canvas': CanvasTextureBrush,
        'rust': RustBrush,
        'emoji': EmojiBrush,
        'ascii': AsciiBrush,
        'morse': MorseBrush,
        'galaxy': GalaxyBrush,
        'constellation': ConstellationBrush,
        'rune': RuneBrush,
        'mana': ManaBrush,
        'phoenix': PhoenixBrush,
        'opart': OpArtBrush,
        'moire': MoireBrush,
        'gravity': GravityBrush,
        'wind': WindBrush,
        'magnet': MagnetBrush,
        # Новые
        'soundwave': SoundWaveBrush,
        'seismic': SeismicBrush,
        'bass': BassBrush,
        'cell': CellBrush,
        'bacteria': BacteriaBrush,
        'neuron': NeuronBrush,
        'dna': DNABrush,
        'watercolor_wash': WatercolorWashBrush,
        'inkdrop': InkDropBrush,
        'steam': SteamBrush,
        'brickwall': BrickWallBrush,
        'chain': ChainBrush,
        'scaffold': ScaffoldBrush,
        'sprinkles': SprinklesBrush,
        'coffee': CoffeeBrush,
        'musicnotes': MusicNotesBrush,
        'equalizer': SoundEqualizerBrush,
        'qrcode': QRCodeBrush,
        'matrix': MatrixBrush,
        'rainbow_spray': RainbowSprayBrush,
        'aurora': AuroraBrush,
        'tornado': TornadoBrush,
        'sumi': SumiBrush,
        'charcoal': CharcoalBrush,
        'dali': DaliBrush,
        'escher': EscherBrush,
        'pollock': PollockBrush,
    }
    brush_cls = brushes.get(tool)
    if brush_cls:
        brush_cls.draw(painter, last_point, current_point, settings)