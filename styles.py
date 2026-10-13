# [file name]: styles.py
from PyQt6.QtCore import Qt


class ModernStyles:
    """Минималистичный дизайн без излишеств"""
    
    # ===== ЦВЕТА =====
    ACCENT = "#6C63FF"
    ACCENT_HOVER = "#7C73FF"
    ACCENT_LIGHT = "rgba(108, 99, 255, 0.15)"
    ACCENT_MEDIUM = "rgba(108, 99, 255, 0.25)"
    
    BG_CARD = "rgba(255, 255, 255, 0.06)"
    BG_HOVER = "rgba(255, 255, 255, 0.08)"
    BG_ACTIVE = "rgba(255, 255, 255, 0.12)"
    
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "rgba(255, 255, 255, 0.70)"
    TEXT_TERTIARY = "rgba(255, 255, 255, 0.40)"
    
    BORDER = "rgba(255, 255, 255, 0.06)"
    BORDER_HOVER = "rgba(255, 255, 255, 0.12)"
    
    RADIUS = "8px"
    RADIUS_FULL = "9999px"
    
    # ===== СТИЛИ =====
    
    PLAYLIST_PANEL = f"""
        QFrame#playlistPanel {{
            background: {BG_CARD};
            border-radius: {RADIUS};
            border: 1px solid {BORDER};
        }}
    """
    
    PANEL_TITLE = f"""
        font-size: 13px;
        font-weight: 600;
        color: {TEXT_PRIMARY};
        letter-spacing: 0.3px;
    """
    
    COUNT_LABEL = f"""
        font-size: 11px;
        color: {TEXT_TERTIARY};
        background: rgba(255,255,255,0.06);
        padding: 0px 8px;
        border-radius: {RADIUS_FULL};
        min-width: 20px;
        max-height: 20px;
    """
    
    PLAYLIST = f"""
        QListWidget {{
            background: transparent;
            border: none;
            padding: 2px 0;
            outline: none;
        }}
        QListWidget::item {{
            padding: 8px 10px;
            border-radius: 4px;
            margin: 1px 0;
            color: {TEXT_SECONDARY};
            font-size: 12px;
        }}
        QListWidget::item:hover {{
            background: {BG_HOVER};
            color: {TEXT_PRIMARY};
        }}
        QListWidget::item:selected {{
            background: {ACCENT_LIGHT};
            color: {TEXT_PRIMARY};
        }}
    """
    
    ACTION_BUTTON = f"""
        QPushButton {{
            background: rgba(255,255,255,0.06);
            border: none;
            border-radius: 4px;
            color: {TEXT_SECONDARY};
        }}
        QPushButton:hover {{
            background: rgba(255,255,255,0.12);
            color: {TEXT_PRIMARY};
        }}
        QPushButton:pressed {{
            background: rgba(255,255,255,0.18);
        }}
    """
    
    VIDEO_CONTAINER = f"""
        QFrame#videoContainer {{
            background: rgba(0,0,0,0.3);
            border-radius: {RADIUS};
            border: 1px solid {BORDER};
        }}
    """
    
    VIDEO_WIDGET = f"""
        QVideoWidget {{
            background: transparent;
            border-radius: {RADIUS};
        }}
    """
    
    PLACEHOLDER = f"""
        QWidget#placeholder {{
            background: transparent;
            border-radius: {RADIUS};
        }}
    """
    
    PLACEHOLDER_TITLE = f"""
        font-size: 18px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        letter-spacing: -0.3px;
    """
    
    PLACEHOLDER_SUBTITLE = f"""
        font-size: 12px;
        color: {TEXT_TERTIARY};
    """
    
    TRACK_INFO = f"""
        QFrame#trackInfo {{
            background: {BG_CARD};
            border-radius: {RADIUS};
            border: 1px solid {BORDER};
        }}
    """
    
    TRACK_TITLE = f"""
        font-size: 13px;
        font-weight: 600;
        color: {TEXT_PRIMARY};
    """
    
    TRACK_ARTIST = f"""
        font-size: 11px;
        color: {TEXT_TERTIARY};
    """
    
    QUALITY_LABEL = f"""
        font-size: 10px;
        color: {ACCENT};
        background: {ACCENT_LIGHT};
        padding: 1px 8px;
        border-radius: {RADIUS_FULL};
        font-weight: 500;
    """
    
    PROGRESS_PANEL = f"""
        QFrame#progressPanel {{
            background: {BG_CARD};
            border-radius: {RADIUS};
            border: 1px solid {BORDER};
        }}
    """
    
    TIME_LABEL = f"""
        font-size: 11px;
        color: {TEXT_TERTIARY};
        font-weight: 500;
        font-feature-settings: "tnum";
    """
    
    PROGRESS_SLIDER = f"""
        QSlider {{
            background: transparent;
        }}
        QSlider::groove:horizontal {{
            height: 3px;
            background: rgba(255,255,255,0.10);
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {ACCENT};
            border-radius: {RADIUS_FULL};
            width: 12px;
            height: 12px;
            margin: -4.5px 0;
        }}
        QSlider::handle:horizontal:hover {{
            width: 14px;
            height: 14px;
            margin: -5.5px 0;
        }}
        QSlider::sub-page:horizontal {{
            background: {ACCENT};
            border-radius: 2px;
        }}
    """
    
    CONTROLS_PANEL = f"""
        QFrame#controlsPanel {{
            background: {BG_CARD};
            border-radius: {RADIUS};
            border: 1px solid {BORDER};
        }}
    """
    
    CONTROL_BUTTON = f"""
        QPushButton#controlButton {{
            background: transparent;
            border: none;
            border-radius: {RADIUS_FULL};
        }}
        QPushButton#controlButton:hover {{
            background: {BG_HOVER};
        }}
        QPushButton#controlButton:pressed {{
            background: {BG_ACTIVE};
        }}
    """
    
    CONTROL_BUTTON_ACTIVE = f"""
        QPushButton#controlButton {{
            background: {ACCENT_LIGHT};
            border: none;
            border-radius: {RADIUS_FULL};
        }}
        QPushButton#controlButton:hover {{
            background: {ACCENT_MEDIUM};
        }}
    """
    
    PLAY_BUTTON = f"""
        QPushButton#playButton {{
            background: {ACCENT};
            border: none;
            border-radius: {RADIUS_FULL};
            color: white;
        }}
        QPushButton#playButton:hover {{
            background: {ACCENT_HOVER};
        }}
        QPushButton#playButton:pressed {{
            background: {ACCENT};
        }}
    """
    
    VOLUME_PANEL = f"""
        QFrame#volumePanel {{
            background: {BG_CARD};
            border-radius: {RADIUS};
            border: 1px solid {BORDER};
        }}
    """
    
    VOLUME_BUTTON = f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: {RADIUS_FULL};
        }}
        QPushButton:hover {{
            background: {BG_HOVER};
        }}
    """
    
    VOLUME_SLIDER = f"""
        QSlider {{
            background: transparent;
        }}
        QSlider::groove:horizontal {{
            height: 2px;
            background: rgba(255,255,255,0.10);
            border-radius: 1px;
        }}
        QSlider::handle:horizontal {{
            background: {TEXT_SECONDARY};
            border-radius: {RADIUS_FULL};
            width: 8px;
            height: 8px;
            margin: -3px 0;
        }}
        QSlider::handle:horizontal:hover {{
            background: {TEXT_PRIMARY};
            width: 10px;
            height: 10px;
            margin: -4px 0;
        }}
        QSlider::sub-page:horizontal {{
            background: {TEXT_SECONDARY};
            border-radius: 1px;
        }}
    """
    
    VOLUME_LABEL = f"""
        font-size: 10px;
        color: {TEXT_TERTIARY};
        font-weight: 500;
    """
    
    # ===== КНОПКА ЗАКРЫТИЯ =====
    CLOSE_BUTTON = f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background: rgba(255,70,70,0.25);
        }}
    """
    
    CONTEXT_MENU = f"""
        QMenu {{
            background: rgba(20,20,35,0.95);
            border: 1px solid {BORDER};
            border-radius: {RADIUS};
            padding: 4px;
            min-width: 160px;
        }}
        QMenu::item {{
            padding: 6px 28px 6px 14px;
            border-radius: 4px;
            color: {TEXT_SECONDARY};
            font-size: 12px;
        }}
        QMenu::item:selected {{
            background: {ACCENT_LIGHT};
            color: {TEXT_PRIMARY};
        }}
        QMenu::separator {{
            height: 1px;
            background: {BORDER};
            margin: 4px 8px;
        }}
        QMenu::icon {{
            padding-right: 6px;
        }}
    """
    
    DIALOG = f"""
        QMessageBox {{
            background: rgba(20,20,35,0.95);
            border: 1px solid {BORDER};
            border-radius: 12px;
        }}
        QMessageBox QLabel {{
            color: {TEXT_PRIMARY};
            font-size: 12px;
        }}
        QMessageBox QPushButton {{
            background: rgba(255,255,255,0.06);
            border: none;
            border-radius: 6px;
            padding: 5px 14px;
            color: {TEXT_SECONDARY};
            font-size: 12px;
            min-width: 60px;
        }}
        QMessageBox QPushButton:hover {{
            background: rgba(255,255,255,0.12);
            color: {TEXT_PRIMARY};
        }}
    """


# ===== КЛАСС ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ =====
class GlassmorphismStyles:
    """
    Класс-заглушка для обратной совместимости.
    """
    
    ACCENT = ModernStyles.ACCENT
    ACCENT_LIGHT = ModernStyles.ACCENT_LIGHT
    BG_CARD = ModernStyles.BG_CARD
    BG_HOVER = ModernStyles.BG_HOVER
    BG_ACTIVE = ModernStyles.BG_ACTIVE
    TEXT_PRIMARY = ModernStyles.TEXT_PRIMARY
    TEXT_SECONDARY = ModernStyles.TEXT_SECONDARY
    TEXT_TERTIARY = ModernStyles.TEXT_TERTIARY
    RADIUS = ModernStyles.RADIUS
    RADIUS_FULL = ModernStyles.RADIUS_FULL
    BORDER = ModernStyles.BORDER
    
    # Стили
    PLAYLIST_STYLE = ModernStyles.PLAYLIST
    GLASS_BUTTON = ModernStyles.ACTION_BUTTON
    CONTROL_BUTTON = ModernStyles.CONTROL_BUTTON
    TITLE_LABEL = ModernStyles.TRACK_TITLE
    LABEL_STYLE = ModernStyles.TRACK_ARTIST
    GLASS_SLIDER = ModernStyles.PROGRESS_SLIDER
    CLOSE_BUTTON = ModernStyles.CLOSE_BUTTON