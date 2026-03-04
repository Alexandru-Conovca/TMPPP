"""
Palette and basic styles for the Smart Home PyQt5 UI.
Colors inspired by VK light theme: white base, blue primary, subtle grays.
"""
from PyQt5.QtGui import QColor, QPalette


COLORS = {
    "background": "#f5f6f8",
    "surface": "#ffffff",
    "primary": "#2787f5",
    "primary_dark": "#1f6cd6",
    "border": "#dfe3e8",
    "text": "#1f2933",
    "muted": "#6b7280",
    "accent": "#4b5563",
}


def apply_palette(app) -> None:
    """Apply a light Fusion palette to keep a clean look."""
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(COLORS["background"]))
    palette.setColor(QPalette.Base, QColor(COLORS["surface"]))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS["background"]))
    palette.setColor(QPalette.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.Button, QColor(COLORS["surface"]))
    palette.setColor(QPalette.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.Highlight, QColor(COLORS["primary"]))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def base_stylesheet() -> str:
    """QSS with flat cards, rounded corners, and subtle borders."""
    return f"""
        QWidget {{
            font-family: 'Segoe UI', sans-serif;
            color: {COLORS['text']};
        }}
        QMainWindow {{
            background: {COLORS['background']};
        }}
        QGroupBox {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding: 10px;
            font-weight: 600;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 2px 4px;
            color: {COLORS['accent']};
        }}
        QPushButton {{
            background: {COLORS['primary']};
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background: {COLORS['border']};
            color: {COLORS['muted']};
        }}
        QLineEdit, QComboBox, QListWidget {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 6px;
        }}
        QListWidget::item {{
            padding: 8px;
        }}
        QListWidget::item:selected {{
            background: {COLORS['primary']};
            color: #ffffff;
        }}
        QLabel.hint {{
            color: {COLORS['muted']};
        }}
    """
