"""Traduzioni in JSON.

Ogni lingua è un file piatto {"chiave": "testo"}. I testi comuni stanno in
eureka_core/locales, quelli del programma nella sua cartella locales: le chiavi
del programma hanno la precedenza. Le chiavi mancanti ricadono sull'italiano,
poi sulla chiave stessa (così un testo non tradotto si nota subito).

    _ = Translator("en", app_locales=Path("kalendae/locales"))
    _("menu.about", app="Kalendae")   # "About Kalendae"
"""

from __future__ import annotations

import json
import locale
from pathlib import Path

CORE_LOCALES = Path(__file__).parent / "locales"
FALLBACK = "it"


def system_language() -> str:
    try:
        code = locale.getlocale()[0] or ""
    except ValueError:
        code = ""
    return (code.split("_")[0] or FALLBACK).lower()


def _read(folder: Path | None, lang: str) -> dict:
    if folder is None:
        return {}
    try:
        return json.loads((folder / f"{lang}.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class Translator:
    def __init__(self, language: str = "system", app_locales: Path | None = None):
        self.language = system_language() if language == "system" else language
        self._fallback = {**_read(CORE_LOCALES, FALLBACK), **_read(app_locales, FALLBACK)}
        self._texts = {**_read(CORE_LOCALES, self.language), **_read(app_locales, self.language)}

    def __call__(self, key: str, **values) -> str:
        text = self._texts.get(key) or self._fallback.get(key) or key
        try:
            return text.format(**values) if values else text
        except (KeyError, IndexError):
            return text

    @staticmethod
    def available(app_locales: Path | None = None) -> list[str]:
        langs = {p.stem for p in CORE_LOCALES.glob("*.json")}
        if app_locales:
            langs |= {p.stem for p in app_locales.glob("*.json")}
        return sorted(langs)
