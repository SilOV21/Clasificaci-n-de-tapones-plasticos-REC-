"""Acerca de — créditos del proyecto."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


AUTHORS = [
    "Asil Arnous",
    "Delia Martínez Fernández",
    "Silvia Ochando Valero",
    "Ruth Alejandra Bastidas Alva",
]


class AboutPanel(QWidget):
    """Static credits tab. All visual styling is delegated to theme.py via objectName."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        title = QLabel("REC · Clasificación de Tapones Plásticos")
        title.setObjectName("aboutTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "Laboratorio de Automática y Robótica · Curso 2025 / 2026<br>"
            "Máster Universitario en Automática y Robótica"
        )
        subtitle.setObjectName("aboutSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setTextFormat(Qt.RichText)
        layout.addWidget(subtitle)

        sep = QFrame()
        sep.setObjectName("aboutSep")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        header = QLabel("Equipo de desarrollo")
        header.setObjectName("aboutSection")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        for name in AUTHORS:
            row = QLabel(name)
            row.setObjectName("aboutAuthor")
            row.setAlignment(Qt.AlignCenter)
            layout.addWidget(row)

        layout.addStretch(1)
