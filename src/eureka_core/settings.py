"""Impostazioni in JSON: un file comune alla suite e uno per programma.

    settings = Settings("kalendae")
    settings.suite["theme"]          # comune a tutti i programmi
    settings.app["week_starts_on"]   # solo di Kalendae
    settings.save()
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from platformdirs import user_config_dir

SUITE_DEFAULTS = {
    "theme": "system",          # "system" | "light" | "dark"
    "language": "system",       # "system" | "it" | "en" ...
    "check_updates": True,
    "skipped_versions": {},     # {app_id: "1.2.0"}
}


def config_dir() -> Path:
    override = os.environ.get("EUREKA_CONFIG_DIR")   # utile per i test
    path = Path(override) if override else Path(user_config_dir("EurekaSuite", appauthor=False))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load(path: Path, defaults: dict) -> dict:
    data = dict(defaults)
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(stored, dict):
            data.update(stored)
    except FileNotFoundError:
        pass
    except (json.JSONDecodeError, OSError):
        # File rovinato: teniamo una copia e ripartiamo dai valori predefiniti.
        try:
            path.replace(path.with_suffix(".json.bak"))
        except OSError:
            pass
    return data


def _save(path: Path, data: dict) -> None:
    # Scrittura atomica: se il programma si chiude a metà, il file resta integro.
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.stem, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


class Settings:
    def __init__(self, app_id: str, app_defaults: dict | None = None):
        self.app_id = app_id
        self._dir = config_dir()
        self._suite_path = self._dir / "suite.json"
        self._app_path = self._dir / f"{app_id}.json"
        self.suite: dict = _load(self._suite_path, SUITE_DEFAULTS)
        self.app: dict = _load(self._app_path, app_defaults or {})

    def reload_suite(self) -> None:
        """Rilegge le impostazioni comuni (es. dopo che un altro programma le ha cambiate)."""
        self.suite = _load(self._suite_path, SUITE_DEFAULTS)

    def save(self) -> None:
        _save(self._suite_path, self.suite)
        _save(self._app_path, self.app)
