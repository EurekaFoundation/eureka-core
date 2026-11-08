"""Programma di prova: mostra tema, traduzioni e finestre comuni.

    python examples/demo.py kalendae
"""

import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from eureka_core import EurekaApp


def main() -> int:
    app_id = sys.argv[1] if len(sys.argv) > 1 else "kalendae"
    app = EurekaApp(app_id, version="0.1.0")
    _ = app.tr_

    win = QMainWindow()
    win.setWindowTitle(app.info.name)
    win.resize(520, 320)

    view = win.menuBar().addMenu(_("menu.view"))
    for mode in ("system", "light", "dark"):
        act = QAction(_(f"theme.{mode}"), win)
        act.triggered.connect(lambda _c=False, m=mode: app.apply_theme(m))
        view.addAction(act)

    help_menu = win.menuBar().addMenu(_("menu.help"))
    help_menu.addAction(_("menu.check_updates"), lambda: app.check_updates(win))
    help_menu.addAction(_("menu.about", app=app.info.name), lambda: app.show_about(win))

    body = QWidget()
    layout = QVBoxLayout(body)
    layout.addWidget(QLabel(f"<h2>{app.info.name}</h2><p>{_(app.info.description)}</p>"))
    btn = QPushButton(_("menu.about", app=app.info.name))
    btn.setProperty("accent", True)
    btn.clicked.connect(lambda: app.show_about(win))
    layout.addWidget(btn)
    layout.addStretch()
    win.setCentralWidget(body)

    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
