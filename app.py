"""EurekaApp: il punto d'ingresso comune a tutti i programmi della suite."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from . import theme
from .dialogs import AboutDialog, ask_update
from .i18n import Translator
from .settings import Settings
from .suite import SUITE_NAME, get_app
from .updater import UpdateChecker


class EurekaApp(QApplication):
    def __init__(
        self,
        app_id: str,
        version: str,
        argv: list[str] | None = None,
        app_defaults: dict | None = None,
        locales_dir: Path | None = None,
    ):
        super().__init__(argv if argv is not None else sys.argv)
        self.info = get_app(app_id)
        self.version = version
        self._locales_dir = locales_dir

        self.setApplicationName(self.info.name)
        self.setApplicationVersion(version)
        self.setOrganizationName(SUITE_NAME)

        self.settings = Settings(app_id, app_defaults)
        self.tr_ = Translator(self.settings.suite["language"], locales_dir)
        self.apply_theme()

        self.aboutToQuit.connect(self.settings.save)
        self._checker = None

    # --- aspetto e lingua ----------------------------------------------------

    def apply_theme(self, mode: str | None = None) -> None:
        if mode:
            self.settings.suite["theme"] = mode
        theme.apply_theme(self, self.settings.suite["theme"], self.info.accent)

    def set_language(self, language: str) -> None:
        """Cambia lingua. I testi già mostrati si aggiornano al riavvio."""
        self.settings.suite["language"] = language
        self.tr_ = Translator(language, self._locales_dir)

    # --- finestre comuni -----------------------------------------------------

    def show_about(self, parent=None) -> None:
        AboutDialog(self.info, self.version, self.tr_, parent).exec()

    # --- aggiornamenti -------------------------------------------------------

    def check_updates(self, parent=None, silent: bool = False) -> None:
        """silent=True: avvisa solo se c'è una novità (uso all'avvio)."""
        if silent and not self.settings.suite["check_updates"]:
            return
        _ = self.tr_
        checker = UpdateChecker(self.info.repo, self.version, self)
        self._checker = checker   # evita che venga distrutto prima della fine

        def on_available(rel):
            skipped = self.settings.suite["skipped_versions"].get(self.info.id)
            if silent and skipped == rel.version:
                return
            if ask_update(rel, self.info, self.version, _, parent) == "skip":
                self.settings.suite["skipped_versions"][self.info.id] = rel.version
                self.settings.save()

        checker.available.connect(on_available)
        if not silent:
            checker.up_to_date.connect(lambda: QMessageBox.information(
                parent, self.info.name, _("update.none", app=self.info.name)))
            checker.failed.connect(lambda _msg: QMessageBox.warning(
                parent, self.info.name, _("update.error")))
        checker.start()

    def check_updates_later(self, parent=None, delay_ms: int = 5000) -> None:
        """Controllo silenzioso qualche secondo dopo l'avvio, per non rallentarlo."""
        QTimer.singleShot(delay_ms, lambda: self.check_updates(parent, silent=True))
