"""Test dei moduli senza interfaccia: python -m pytest tests"""

import json

import pytest

from eureka_core import Settings, Translator, get_app


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    monkeypatch.setenv("EUREKA_CONFIG_DIR", str(tmp_path))
    return tmp_path


def test_suite_shared_between_apps(tmp_config):
    a = Settings("kalendae", {"week_starts_on": 1})
    a.suite["theme"] = "dark"
    a.app["week_starts_on"] = 0
    a.save()

    b = Settings("charta")
    assert b.suite["theme"] == "dark"          # impostazione comune condivisa
    assert "week_starts_on" not in b.app       # quella di Kalendae no
    assert Settings("kalendae").app["week_starts_on"] == 0


def test_corrupted_file_is_backed_up(tmp_config):
    (tmp_config / "suite.json").write_text("{ non è json", encoding="utf-8")
    s = Settings("viator")
    assert s.suite["theme"] == "system"
    assert (tmp_config / "suite.json.bak").exists()


def test_translations_with_app_override(tmp_path):
    (tmp_path / "en.json").write_text(json.dumps({"app.title": "My calendar"}))
    _ = Translator("en", app_locales=tmp_path)
    assert _("app.title") == "My calendar"
    assert _("menu.about", app="Kalendae") == "About Kalendae"


def test_translation_fallbacks():
    _ = Translator("de")                       # lingua non presente
    assert _("theme.dark") == "Scuro"          # ricade sull'italiano
    assert _("chiave.inesistente") == "chiave.inesistente"


def test_unknown_app():
    with pytest.raises(ValueError):
        get_app("calamus")


def test_version_compare():
    from eureka_core.updater import is_newer
    assert is_newer("v1.10.0", "1.9.3")
    assert not is_newer("1.2.0", "1.2.0")
    assert is_newer("0.2.0", "0.1.9-beta")
