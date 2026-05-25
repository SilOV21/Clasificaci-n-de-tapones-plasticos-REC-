"""Tema oscuro industrial SCADA — paleta y QSS global del HMI."""
from __future__ import annotations

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication


BG_BASE        = "#15171c"
BG_PANEL       = "#1b1d22"
BG_RAISED      = "#23262d"
BG_INPUT       = "#11131a"
BORDER         = "#2c3038"
BORDER_STRONG  = "#3a3f4a"

TEXT_PRIMARY   = "#e6e6e6"
TEXT_SECONDARY = "#8b9098"
TEXT_MUTED     = "#5a6068"

ACCENT         = "#00b4ff"
ACCENT_HOVER   = "#33c2ff"
ACCENT_PRESSED = "#0090d0"

WARN           = "#ffb000"
DANGER         = "#e84a3b"
DANGER_HOVER   = "#ff6655"
DANGER_PRESSED = "#c0382b"
OK             = "#2ecc71"
OK_HOVER       = "#3ddf85"
OK_PRESSED     = "#1e8449"

FONT_FAMILY    = "'Inter', 'Segoe UI', 'Ubuntu', sans-serif"
FONT_MONO      = "'JetBrains Mono', 'Source Code Pro', 'DejaVu Sans Mono', monospace"


GLOBAL_QSS = f"""
QWidget {{
    background:{BG_BASE};
    color:{TEXT_PRIMARY};
    font-family:{FONT_FAMILY};
    font-size:10pt;
}}
QMainWindow, QDialog {{ background:{BG_BASE}; }}

QGroupBox {{
    background:{BG_PANEL};
    border:1px solid {BORDER};
    border-radius:6px;
    margin-top:18px;
    padding:14px 12px 12px 12px;
    font-weight:600;
}}
QGroupBox::title {{
    subcontrol-origin:margin;
    subcontrol-position:top left;
    left:10px;
    padding:2px 8px;
    color:{ACCENT};
    letter-spacing:1px;
}}

QTabWidget::pane {{
    border:1px solid {BORDER};
    background:{BG_PANEL};
    top:-1px;
}}
QTabBar::tab {{
    background:{BG_BASE};
    color:{TEXT_SECONDARY};
    padding:8px 18px;
    font-weight:600;
    letter-spacing:0.5px;
    border:1px solid transparent;
    border-bottom:none;
}}
QTabBar::tab:selected {{
    background:{BG_PANEL};
    color:{ACCENT};
    border-color:{BORDER};
    border-bottom:2px solid {WARN};
}}
QTabBar::tab:hover:!selected {{ color:{TEXT_PRIMARY}; }}

QPushButton {{
    background:{BG_RAISED};
    color:{TEXT_PRIMARY};
    border:1px solid {BORDER_STRONG};
    border-radius:4px;
    padding:6px 14px;
    font-weight:600;
}}
QPushButton:hover  {{ background:{ACCENT}; color:{BG_BASE}; border-color:{ACCENT}; }}
QPushButton:pressed{{ background:{ACCENT_PRESSED}; color:{BG_BASE}; }}
QPushButton:disabled {{ color:{TEXT_MUTED}; background:{BG_PANEL}; }}

QPushButton#estopBtn {{
    background:{DANGER};
    color:white;
    border:2px solid {DANGER_PRESSED};
    font-size:11pt;
    letter-spacing:1px;
    border-radius:6px;
}}
QPushButton#estopBtn:hover   {{ background:{DANGER_HOVER}; }}
QPushButton#estopBtn:pressed {{ background:{DANGER_PRESSED}; }}

QPushButton#rehabBtn {{
    background:{OK};
    color:{BG_BASE};
    border:2px solid {OK_PRESSED};
    font-size:11pt;
    letter-spacing:1px;
    border-radius:6px;
}}
QPushButton#rehabBtn:hover   {{ background:{OK_HOVER}; }}
QPushButton#rehabBtn:pressed {{ background:{OK_PRESSED}; color:white; }}

QPushButton#startBtn {{ background:{OK};     color:{BG_BASE}; border-color:{OK_PRESSED}; }}
QPushButton#startBtn:hover   {{ background:{OK_HOVER}; }}
QPushButton#stopBtn  {{ background:{DANGER}; color:white;     border-color:{DANGER_PRESSED}; }}
QPushButton#stopBtn:hover    {{ background:{DANGER_HOVER}; }}
QPushButton#applyBtn {{ background:{ACCENT}; color:{BG_BASE}; border-color:{ACCENT_PRESSED}; }}
QPushButton#applyBtn:hover   {{ background:{ACCENT_HOVER}; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
    background:{BG_INPUT};
    color:{TEXT_PRIMARY};
    border:1px solid {BORDER};
    border-radius:3px;
    padding:4px 6px;
    selection-background-color:{ACCENT};
    selection-color:{BG_BASE};
}}
QPlainTextEdit#logView, QTextEdit#logView {{
    font-family:{FONT_MONO};
    font-size:10pt;
    background:#0d0e12;
    color:#cfd2d6;
}}

QLabel#topBarTitle {{
    font-size:16pt;
    font-weight:800;
    color:{ACCENT};
    letter-spacing:2px;
}}
QLabel#ipLabel {{
    color:{TEXT_SECONDARY};
    font-family:{FONT_MONO};
}}
QLabel#sectionLabel {{
    color:{ACCENT};
    font-weight:700;
    letter-spacing:1px;
}}
QLabel#numericReadout {{
    font-family:{FONT_MONO};
    font-size:14pt;
    color:{WARN};
    font-weight:700;
}}
QLabel#numericReadoutBig {{
    font-family:{FONT_MONO};
    font-size:24pt;
    color:{WARN};
    font-weight:800;
}}
QLabel#monoLabel {{
    font-family:{FONT_MONO};
    color:{TEXT_PRIMARY};
}}
QLabel#mutedLabel {{
    color:{TEXT_SECONDARY};
}}

QLabel#aboutTitle {{
    font-size:24pt;
    font-weight:800;
    color:{ACCENT};
    letter-spacing:2px;
}}
QLabel#aboutSubtitle {{
    font-size:11pt;
    color:{TEXT_SECONDARY};
}}
QLabel#aboutSection {{
    font-size:12pt;
    color:{WARN};
    font-weight:700;
    letter-spacing:2px;
    margin-top:14px;
}}
QLabel#aboutAuthor {{
    font-size:13pt;
    color:{TEXT_PRIMARY};
    padding:4px;
}}
QLabel#aboutFooter {{
    font-size:9pt;
    color:{TEXT_MUTED};
    margin-top:24px;
}}
QFrame#aboutSep {{
    color:{BORDER_STRONG};
    background:{BORDER_STRONG};
    max-height:1px;
    margin:14px 60px;
}}

QStatusBar {{
    background:{BG_PANEL};
    color:{TEXT_SECONDARY};
    border-top:1px solid {BORDER};
}}
QMenuBar {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; }}
QMenuBar::item:selected {{ background:{ACCENT}; color:{BG_BASE}; }}
QMenu {{
    background:{BG_PANEL};
    border:1px solid {BORDER};
    color:{TEXT_PRIMARY};
}}
QMenu::item:selected {{ background:{ACCENT}; color:{BG_BASE}; }}

QCheckBox {{ spacing:6px; }}
QCheckBox::indicator {{ width:14px; height:14px; }}
QCheckBox::indicator:unchecked {{ background:{BG_INPUT}; border:1px solid {BORDER_STRONG}; border-radius:2px; }}
QCheckBox::indicator:checked   {{ background:{ACCENT};   border:1px solid {ACCENT};        border-radius:2px; }}

QScrollBar:vertical   {{ background:{BG_BASE}; width:12px; margin:0; }}
QScrollBar::handle:vertical {{ background:{BORDER_STRONG}; border-radius:6px; min-height:24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar:horizontal {{ background:{BG_BASE}; height:12px; margin:0; }}
QScrollBar::handle:horizontal {{ background:{BORDER_STRONG}; border-radius:6px; min-width:24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}

QToolTip {{
    background:{BG_PANEL};
    color:{TEXT_PRIMARY};
    border:1px solid {ACCENT};
    padding:4px 6px;
}}
"""


def apply_theme(app: QApplication) -> None:
    """Install the dark SCADA palette + global QSS on a QApplication."""
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(BG_BASE))
    pal.setColor(QPalette.Base,            QColor(BG_INPUT))
    pal.setColor(QPalette.AlternateBase,   QColor(BG_PANEL))
    pal.setColor(QPalette.Text,            QColor(TEXT_PRIMARY))
    pal.setColor(QPalette.WindowText,      QColor(TEXT_PRIMARY))
    pal.setColor(QPalette.Button,          QColor(BG_RAISED))
    pal.setColor(QPalette.ButtonText,      QColor(TEXT_PRIMARY))
    pal.setColor(QPalette.Highlight,       QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor(BG_BASE))
    pal.setColor(QPalette.ToolTipBase,     QColor(BG_PANEL))
    pal.setColor(QPalette.ToolTipText,     QColor(TEXT_PRIMARY))
    app.setPalette(pal)
    app.setStyleSheet(GLOBAL_QSS)
