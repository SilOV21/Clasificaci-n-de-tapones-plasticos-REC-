"""Tabbed log viewer: one tab per subsystem + an aggregate tab."""
from __future__ import annotations

import time
from typing import Dict

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


MAX_BLOCKS = 5000


class LogPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(False)
        self._views: Dict[str, QPlainTextEdit] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        btn_clear = QPushButton("Clear current tab")
        btn_clear.clicked.connect(self._clear_current)
        toolbar.addWidget(btn_clear)
        btn_clear_all = QPushButton("Clear all")
        btn_clear_all.clicked.connect(self._clear_all)
        toolbar.addWidget(btn_clear_all)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        layout.addWidget(self._tabs, 1)

        self._ensure_tab("all", "All")
        self._ensure_tab("ros", "ROS bridge")

    def append(self, source: str, line: str) -> None:
        ts = time.strftime("%H:%M:%S")
        formatted = f"[{ts}] {line}"

        view = self._ensure_tab(source, self._label_for(source))
        self._append_line(view, formatted)

        agg = self._views["all"]
        self._append_line(agg, f"[{source}] {formatted}")

    def _ensure_tab(self, key: str, label: str) -> QPlainTextEdit:
        if key in self._views:
            return self._views[key]
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setMaximumBlockCount(MAX_BLOCKS)
        view.setStyleSheet(
            "QPlainTextEdit { background:#1e1e1e; color:#d4d4d4; "
            "font-family:monospace; font-size:11px; }"
        )
        self._views[key] = view
        self._tabs.addTab(view, label)
        return view

    @staticmethod
    def _label_for(source: str) -> str:
        return {
            "driver": "UR Driver",
            "tf": "TF Publisher",
            "vision": "Vision",
            "ros": "ROS bridge",
            "system": "System",
            "all": "All",
        }.get(source, source)

    def _append_line(self, view: QPlainTextEdit, text: str) -> None:
        sb = view.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 4
        view.appendPlainText(text)
        if at_bottom:
            view.moveCursor(QTextCursor.End)

    def _clear_current(self) -> None:
        idx = self._tabs.currentIndex()
        if idx < 0:
            return
        widget = self._tabs.widget(idx)
        if isinstance(widget, QPlainTextEdit):
            widget.clear()

    def _clear_all(self) -> None:
        for v in self._views.values():
            v.clear()
