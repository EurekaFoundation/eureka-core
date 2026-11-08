# eureka-core

Libreria condivisa di **Eureka Suite**. Contiene tutto ciò che Viator, Libellus,
Charta e Kalendae hanno in comune, così ogni programma si concentra solo sulle
proprie funzioni.

## Cosa c'è dentro

| Modulo | Responsabilità |
|---|---|
| `eureka_core.app` | `EurekaApp`: crea la `QApplication`, applica tema e lingua, carica le impostazioni. È il punto d'ingresso di ogni programma. |
| `eureka_core.suite` | Registro dei programmi della suite (nome, colore, descrizione, repository). |
| `eureka_core.settings` | Impostazioni in JSON: un file **comune** a tutta la suite (tema, lingua, aggiornamenti) e uno **per programma**. |
| `eureka_core.theme` | Palette chiara/scura comune + colore d'accento del singolo programma. |
| `eureka_core.i18n` | Traduzioni in file JSON (`it`, `en`…), con testi comuni della suite e testi del programma. |
| `eureka_core.updater` | Controllo nuove versioni tramite GitHub Releases, in background e senza bloccare l'interfaccia. |
| `eureka_core.dialogs` | Finestre comuni: *Informazioni su…*, avviso aggiornamento. |

### Cosa **non** ci va

Tutto ciò che è specifico di un programma (il motore web di Viator, la tela di
Libellus, l'impaginazione di Charta, gli eventi di Kalendae). Regola pratica: un
pezzo di codice entra in `eureka-core` solo quando **almeno due programmi** lo usano.

## Dove vengono salvati i dati

Le cartelle seguono le convenzioni di ogni sistema operativo (tramite `platformdirs`):

```
<config>/EurekaSuite/
├── suite.json          ← impostazioni comuni (tema, lingua, aggiornamenti)
├── viator.json         ← impostazioni di Viator
├── libellus.json
└── ...
```

Su Windows `<config>` è `%APPDATA%`, su macOS `~/Library/Application Support`,
su Linux `~/.config`. Cambiare il tema in un programma lo cambia in tutta la suite.

## Come lo usa un programma

```python
# kalendae/__main__.py
import sys
from PySide6.QtWidgets import QMainWindow
from eureka_core import EurekaApp

def main() -> int:
    app = EurekaApp("kalendae", version="0.3.0")
    _ = app.tr_                    # funzione di traduzione

    window = QMainWindow()
    window.setWindowTitle(_("app.title"))
    window.menuBar().addMenu(_("menu.help")).addAction(
        _("menu.about"), lambda: app.show_about(window)
    )
    window.show()

    app.check_updates_later(window)   # controllo silenzioso dopo l'avvio
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

Un programma aggiunge i propri testi in `kalendae/locales/it.json`, e li passa a
`EurekaApp(..., locales_dir=...)`; le chiavi del programma si sommano a quelle comuni.

## Installazione per lo sviluppo

```bash
pip install -e .          # dalla cartella eureka-core
```

Nei singoli programmi la dipendenza si dichiara nel `pyproject.toml`:

```toml
dependencies = ["eureka-core >= 0.1"]
```

Finché `eureka-core` non è su PyPI, si può puntare direttamente al repository:

```toml
dependencies = ["eureka-core @ git+https://github.com/EurekaFoundation/eureka-core@v0.1.1"]
```

### Pacchetti con PyInstaller

PyInstaller non include da solo i file di traduzione del core: aggiungi
`--collect-data eureka_core` agli argomenti di build.

## Versioni

`eureka-core` segue il *semantic versioning*. I programmi fissano la versione
principale (`>=0.1,<0.2` finché si è in 0.x) così un cambiamento nel core non
rompe un programma che non è stato ancora aggiornato.

## Prossimi passi

1. Spostare in `eureka-core` il codice già duplicato nei quattro programmi
   (impostazioni, finestre "Informazioni", gestione tema).
2. Installer unico: un pacchetto per sistema operativo con scelta dei programmi
   da installare (Inno Setup su Windows, `.dmg` su macOS, Flatpak/AppImage su Linux).
3. Integrazioni tra programmi tramite formati aperti: iCalendar (Kalendae),
   PDF/SVG (Charta), apertura dei link in Viator.

## Licenza

GNU GPL v3.
