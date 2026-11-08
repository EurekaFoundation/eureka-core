"""Tema comune della suite: palette chiara/scura + accento del programma.

Tutti i ruoli della palette sono definiti (anche Light/Midlight/Mid/Dark), così
i widget disegnati a mano, come le griglie di Kalendae, hanno i colori giusti in
entrambi i temi.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication

MODES = ("system", "light", "dark")

LIGHT = {
    "window": "#F7F7F5", "base": "#FFFFFF", "alt": "#F1F1EE", "button": "#EFEFEC",
    "text": "#1C1C1A", "muted": "#6B6B66", "disabled": "#A3A39E",
    "light": "#FFFFFF", "midlight": "#E3E3DF", "mid": "#B8B8B2", "dark": "#8A8A85",
    "shadow": "#000000", "bright": "#C62828", "visited": "#7B3FBF",
}
DARK = {
    "window": "#1E1E1C", "base": "#191918", "alt": "#242422", "button": "#2C2C2A",
    "text": "#ECECE8", "muted": "#9A9A94", "disabled": "#64645F",
    "light": "#45453F", "midlight": "#363633", "mid": "#4A4A46", "dark": "#121211",
    "shadow": "#000000", "bright": "#FF6E6E", "visited": "#C58AF9",
}


def system_is_dark() -> bool:
    try:
        return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except AttributeError:   # Qt < 6.5
        return False


def is_dark(mode: str) -> bool:
    return mode == "dark" or (mode == "system" and system_is_dark())


def build_palette(dark: bool, accent: str) -> QPalette:
    c = DARK if dark else LIGHT
    accent_color = QColor(accent)
    link = accent_color.lighter(140) if dark else accent_color
    roles = {
        QPalette.Window: c["window"], QPalette.WindowText: c["text"],
        QPalette.Base: c["base"], QPalette.AlternateBase: c["alt"],
        QPalette.Text: c["text"], QPalette.Button: c["button"],
        QPalette.ButtonText: c["text"], QPalette.BrightText: c["bright"],
        QPalette.ToolTipBase: c["button"], QPalette.ToolTipText: c["text"],
        QPalette.PlaceholderText: c["muted"],
        QPalette.Light: c["light"], QPalette.Midlight: c["midlight"],
        QPalette.Mid: c["mid"], QPalette.Dark: c["dark"], QPalette.Shadow: c["shadow"],
        QPalette.Highlight: accent_color, QPalette.HighlightedText: "#FFFFFF",
        QPalette.Link: link, QPalette.LinkVisited: c["visited"],
    }
    p = QPalette()
    for role, color in roles.items():
        p.setColor(role, QColor(color))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, QColor(c["disabled"]))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(c["mid"]))
    return p


def apply_theme(app: QApplication, mode: str, accent: str) -> None:
    app.setStyle("Fusion")   # stesso aspetto su Windows, macOS e Linux
    app.setPalette(build_palette(is_dark(mode), accent))
    hover = QColor(accent).lighter(115).name()
    # Solo regole mirate: un foglio di stile generico cambierebbe l'aspetto
    # dei widget dei singoli programmi.
    app.setStyleSheet(
        f'QPushButton[accent="true"] {{ background: {accent}; color: white; border: none;'
        f' border-radius: 6px; padding: 6px 14px; }}'
        f'QPushButton[accent="true"]:hover {{ background: {hover}; }}'
    )
    for w in app.allWidgets():   # i widget disegnati a mano si ridisegnano
        w.update()
