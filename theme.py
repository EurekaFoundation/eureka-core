"""Tema comune della suite: palette chiara/scura + accento del programma."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

LIGHT = {
    "window": "#F7F7F5", "base": "#FFFFFF", "alt": "#EFEFEC",
    "text": "#1C1C1A", "muted": "#6B6B66", "border": "#D9D9D4",
}
DARK = {
    "window": "#1E1E1C", "base": "#262624", "alt": "#2E2E2B",
    "text": "#ECECE8", "muted": "#9A9A94", "border": "#3A3A37",
}


def is_dark(mode: str) -> bool:
    if mode == "dark":
        return True
    if mode == "light":
        return False
    hints = QApplication.styleHints()
    return hasattr(hints, "colorScheme") and hints.colorScheme() == Qt.ColorScheme.Dark


def apply_theme(app: QApplication, mode: str, accent: str) -> None:
    c = DARK if is_dark(mode) else LIGHT
    app.setStyle("Fusion")   # stesso aspetto su Windows, macOS e Linux

    p = QPalette()
    roles = {
        QPalette.Window: c["window"], QPalette.WindowText: c["text"],
        QPalette.Base: c["base"], QPalette.AlternateBase: c["alt"],
        QPalette.Text: c["text"], QPalette.Button: c["alt"],
        QPalette.ButtonText: c["text"], QPalette.ToolTipBase: c["base"],
        QPalette.ToolTipText: c["text"], QPalette.PlaceholderText: c["muted"],
        QPalette.Highlight: accent, QPalette.HighlightedText: "#FFFFFF",
        QPalette.Link: accent,
    }
    for role, color in roles.items():
        p.setColor(role, QColor(color))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, QColor(c["muted"]))
    app.setPalette(p)

    app.setStyleSheet(f"""
        QToolBar {{ border: none; spacing: 4px; padding: 4px; }}
        QPushButton[accent="true"] {{
            background: {accent}; color: white; border: none;
            border-radius: 6px; padding: 6px 14px;
        }}
        QPushButton[accent="true"]:hover {{ background: {QColor(accent).lighter(115).name()}; }}
        QMenu {{ border: 1px solid {c['border']}; }}
    """)
