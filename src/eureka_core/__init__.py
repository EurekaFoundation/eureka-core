"""eureka-core: libreria condivisa di Eureka Suite."""

__version__ = "0.1.1"

from .suite import SUITE_NAME, SuiteApp, get_app, APPS  # noqa: F401
from .settings import Settings  # noqa: F401
from .i18n import Translator  # noqa: F401


def __getattr__(name):
    # EurekaApp importa PySide6: lo carichiamo solo se serve,
    # così i moduli senza interfaccia restano usabili (e testabili) da soli.
    if name == "EurekaApp":
        from .app import EurekaApp
        return EurekaApp
    raise AttributeError(name)
