"""Registro dei programmi che fanno parte di Eureka Suite."""

from dataclasses import dataclass

SUITE_NAME = "Eureka Suite"
ORG = "EurekaFoundation"


@dataclass(frozen=True)
class SuiteApp:
    id: str            # identificativo tecnico (nomi file, impostazioni)
    name: str          # nome mostrato all'utente
    accent: str        # colore d'accento del programma
    description: str   # chiave di traduzione della descrizione

    @property
    def repo(self) -> str:
        return f"{ORG}/{self.id}"

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"


APPS: dict[str, SuiteApp] = {
    a.id: a
    for a in (
        SuiteApp("viator", "Viator", "#2563EB", "suite.viator"),
        SuiteApp("libellus", "Libellus", "#16A34A", "suite.libellus"),
        SuiteApp("charta", "Charta", "#EA580C", "suite.charta"),
        SuiteApp("kalendae", "Kalendae", "#DC2626", "suite.kalendae"),
    )
}


def get_app(app_id: str) -> SuiteApp:
    try:
        return APPS[app_id]
    except KeyError:
        raise ValueError(
            f"'{app_id}' non è un programma di {SUITE_NAME}. "
            f"Programmi noti: {', '.join(APPS)}"
        ) from None
