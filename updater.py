"""Controllo aggiornamenti tramite GitHub Releases.

La parte di rete (latest_release) non dipende da Qt, così si testa da sola.
UpdateChecker la esegue in un thread separato per non bloccare l'interfaccia.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass

API = "https://api.github.com/repos/{repo}/releases/latest"


@dataclass
class Release:
    version: str
    url: str        # pagina della release, dove l'utente scarica l'installer
    notes: str


def parse_version(v: str) -> tuple[int, ...]:
    """'v1.10.2' -> (1, 10, 2). Le parti non numeriche (es. '-beta') vengono ignorate."""
    nums = re.findall(r"\d+", v.split("-")[0])
    return tuple(int(n) for n in nums) or (0,)


def is_newer(candidate: str, current: str) -> bool:
    return parse_version(candidate) > parse_version(current)


def latest_release(repo: str, timeout: float = 8) -> Release:
    req = urllib.request.Request(
        API.format(repo=repo),
        headers={"Accept": "application/vnd.github+json", "User-Agent": "EurekaSuite-updater"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    return Release(
        version=data["tag_name"].lstrip("v"),
        url=data["html_url"],
        notes=data.get("body") or "",
    )


# --- parte Qt ---------------------------------------------------------------

from PySide6.QtCore import QObject, QThread, Signal  # noqa: E402


class _Worker(QObject):
    done = Signal(object)    # Release | None
    failed = Signal(str)

    def __init__(self, repo: str, current: str):
        super().__init__()
        self.repo, self.current = repo, current

    def run(self):
        try:
            rel = latest_release(self.repo)
            self.done.emit(rel if is_newer(rel.version, self.current) else None)
        except Exception as e:  # rete assente, repo senza release, limite API...
            self.failed.emit(str(e))


class UpdateChecker(QObject):
    """Emette `available(Release)`, `up_to_date()` oppure `failed(str)`."""

    available = Signal(object)
    up_to_date = Signal()
    failed = Signal(str)

    def __init__(self, repo: str, current: str, parent=None):
        super().__init__(parent)
        self._thread = QThread(self)
        self._worker = _Worker(repo, current)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.done.connect(self._finish)
        self._worker.failed.connect(self._fail)

    def start(self):
        self._thread.start()

    def _finish(self, rel):
        self._thread.quit()
        if rel:
            self.available.emit(rel)
        else:
            self.up_to_date.emit()

    def _fail(self, msg):
        self._thread.quit()
        self.failed.emit(msg)
