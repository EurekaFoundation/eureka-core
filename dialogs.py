"""Finestre comuni a tutta la suite."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QMessageBox, QPushButton, QVBoxLayout,
)

from .suite import SUITE_NAME, SuiteApp


class AboutDialog(QDialog):
    def __init__(self, info: SuiteApp, version: str, tr, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("menu.about", app=info.name).replace("&", ""))
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        title = QLabel(f"<span style='font-size:22pt; font-weight:600; color:{info.accent}'>{info.name}</span>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        for text in (
            tr(info.description),
            tr("about.version", version=version),
            tr("about.part_of", suite=f"<b>{SUITE_NAME}</b>"),
            f"<i>{tr('suite.tagline')}</i>",
            tr("about.license"),
            f"<a href='{info.url}'>{tr('about.website')}</a>",
        ):
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setOpenExternalLinks(True)
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


def ask_update(release, info: SuiteApp, current: str, tr, parent=None) -> str:
    """Mostra l'avviso di aggiornamento. Restituisce 'download', 'skip' o 'later'."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(tr("update.title"))
    box.setText(tr("update.text", app=info.name, new=release.version, current=current))
    if release.notes:
        box.setDetailedText(release.notes)

    download = QPushButton(tr("update.download"))
    download.setProperty("accent", True)
    box.addButton(download, QMessageBox.AcceptRole)
    skip = box.addButton(tr("update.skip"), QMessageBox.RejectRole)
    box.addButton(tr("update.later"), QMessageBox.RejectRole)
    box.exec()

    clicked = box.clickedButton()
    if clicked is download:
        QDesktopServices.openUrl(QUrl(release.url))
        return "download"
    return "skip" if clicked is skip else "later"
