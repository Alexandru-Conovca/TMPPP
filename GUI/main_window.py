"""Compatibility window module for legacy launch mode."""

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from GUI.smart_home_gui import MainWindow


def launch() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch()
