"""
ScenarioView widget: shows scenarios, allows clone and run (visualize) actions.
"""
from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from manager.home_manager import HomeManager
from scenarios.builder import Scenario


class ScenarioView(QWidget):
    scenarios_changed = pyqtSignal()

    def __init__(self, manager: HomeManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._manager = manager

        self.title = QLabel("Scenarios")
        self.title.setStyleSheet("font-weight: 700; font-size: 14px;")

        self.list_widget = QListWidget()

        self.status_label = QLabel("Select a scenario to run or clone.")
        self.status_label.setStyleSheet("color: #6b7280;")

        self.run_button = QPushButton("Run")
        self.clone_button = QPushButton("Clone")
        self.run_button.clicked.connect(self._handle_run)
        self.clone_button.clicked.connect(self._handle_clone)

        buttons = QHBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.clone_button)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.list_widget)
        layout.addLayout(buttons)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def refresh(self) -> None:
        self.list_widget.clear()
        for scenario in self._manager.scenarios:
            item = QListWidgetItem(scenario.summary())
            item.setData(Qt.UserRole, scenario)
            self.list_widget.addItem(item)

    def _current_scenario(self) -> Optional[Scenario]:
        item = self.list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.UserRole)

    def _handle_run(self) -> None:
        scenario = self._current_scenario()
        if scenario is None:
            return
        steps = "\n".join(f"- {s}" for s in scenario.steps)
        text = steps if steps else "No steps in this scenario."
        QMessageBox.information(self, scenario.name, text)
        self.status_label.setText(f"Ran: {scenario.name}")

    def _handle_clone(self) -> None:
        scenario = self._current_scenario()
        if scenario is None:
            return
        cloned = scenario.clone()
        self._manager.add_scenario(cloned)
        self.status_label.setText(f"Cloned: {cloned.name}")
        self.refresh()
        self.scenarios_changed.emit()
