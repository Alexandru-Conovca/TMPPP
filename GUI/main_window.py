"""
PyQt5 main window for the Smart Home demo.
Connects GUI controls with design-pattern-based domain model.
"""
import sys
from typing import Dict, Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from factories.smart_home_factory import SmartHomeFactory, XiaomiFactory, PhilipsFactory, SamsungFactory
from manager.home_manager import HomeManager
from scenarios.builder import StandardScenarioBuilder, ScenarioDirector
from GUI.device_view import DeviceView
from GUI.scenario_view import ScenarioView
from GUI.styles import apply_palette, base_stylesheet


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Smart Home")
        self.resize(1100, 720)

        self.manager = HomeManager.get_instance()
        self.factories: Dict[str, SmartHomeFactory] = {
            "Xiaomi": XiaomiFactory(),
            "Philips": PhilipsFactory(),
            "Samsung": SamsungFactory(),
        }
        self.current_factory: SmartHomeFactory = self.factories["Xiaomi"]

        self.builder = StandardScenarioBuilder()
        self.director = ScenarioDirector(self.builder)

        central = QWidget()
        main_layout = QHBoxLayout()

        main_layout.addLayout(self._build_controls())

        self.device_view = DeviceView(self.manager)
        self.device_view.devices_changed.connect(self._refresh_views)
        main_layout.addWidget(self.device_view, 2)

        self.scenario_view = ScenarioView(self.manager)
        self.scenario_view.scenarios_changed.connect(self._refresh_views)
        main_layout.addWidget(self.scenario_view, 2)

        central.setLayout(main_layout)
        self.setCentralWidget(central)
        self.setStyleSheet(base_stylesheet())

        self._refresh_views()

    def _build_controls(self) -> QVBoxLayout:
        panel = QVBoxLayout()

        panel.addWidget(self._build_device_box())
        panel.addWidget(self._build_filters_box())
        panel.addWidget(self._build_scenario_box())
        panel.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return panel

    def _build_device_box(self) -> QGroupBox:
        box = QGroupBox("Create Device")
        layout = QVBoxLayout()

        self.device_name_input = QLineEdit()
        self.device_name_input.setPlaceholderText("Device name")

        self.brand_combo_create = QComboBox()
        self.brand_combo_create.addItems(self.factories.keys())
        self.brand_combo_create.currentTextChanged.connect(self._update_factory)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Light", "Thermostat", "Camera", "Alarm"])

        self.create_button = QPushButton("Create + Add")
        self.create_button.clicked.connect(self._create_device)

        layout.addWidget(QLabel("Brand"))
        layout.addWidget(self.brand_combo_create)
        layout.addWidget(QLabel("Device type"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.device_name_input)
        layout.addWidget(self.create_button)
        box.setLayout(layout)
        return box

    def _build_filters_box(self) -> QGroupBox:
        box = QGroupBox("Filters")
        layout = QVBoxLayout()

        self.brand_filter_combo = QComboBox()
        self.brand_filter_combo.addItems(["All brands", *self.factories.keys()])
        self.brand_filter_combo.currentTextChanged.connect(self._refresh_views)

        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItems(["All types", "Light", "Thermostat", "Camera", "Alarm"])
        self.type_filter_combo.currentTextChanged.connect(self._refresh_views)

        layout.addWidget(QLabel("Brand filter"))
        layout.addWidget(self.brand_filter_combo)
        layout.addWidget(QLabel("Device type filter"))
        layout.addWidget(self.type_filter_combo)
        box.setLayout(layout)
        return box

    def _build_scenario_box(self) -> QGroupBox:
        box = QGroupBox("Scenarios")
        layout = QVBoxLayout()

        self.morning_button = QPushButton("Add Morning")
        self.evening_button = QPushButton("Add Evening")
        self.away_button = QPushButton("Add Away")

        self.morning_button.clicked.connect(lambda: self._create_scenario("morning"))
        self.evening_button.clicked.connect(lambda: self._create_scenario("evening"))
        self.away_button.clicked.connect(lambda: self._create_scenario("away"))

        layout.addWidget(QLabel("Preset scenarios"))
        layout.addWidget(self.morning_button)
        layout.addWidget(self.evening_button)
        layout.addWidget(self.away_button)
        box.setLayout(layout)
        return box

    def _update_factory(self, brand: str) -> None:
        self.current_factory = self.factories.get(brand, self.current_factory)

    def _create_device(self) -> None:
        name = self.device_name_input.text().strip() or "New device"
        device_type = self.type_combo.currentText()
        creator = {
            "Light": self.current_factory.create_light,
            "Thermostat": self.current_factory.create_thermostat,
            "Camera": self.current_factory.create_camera,
            "Alarm": self.current_factory.create_alarm,
        }.get(device_type)
        if creator is None:
            return
        device = creator(name)
        self.manager.add_device(device)
        self.device_name_input.clear()
        self._refresh_views()

    def _create_scenario(self, preset: str) -> None:
        scenario = None
        if preset == "morning":
            scenario = self.director.create_morning()
        elif preset == "evening":
            scenario = self.director.create_evening()
        elif preset == "away":
            scenario = self.director.create_away()
        if scenario:
            self.manager.add_scenario(scenario)
            self._refresh_views()

    def _refresh_views(self) -> None:
        brand_filter = self.brand_filter_combo.currentText()
        brand_filter_value: Optional[str] = None if brand_filter == "All brands" else brand_filter
        type_filter = self.type_filter_combo.currentText()
        type_filter_value: Optional[str] = None if type_filter == "All types" else type_filter
        self.device_view.set_filters(brand_filter_value, type_filter_value)
        self.device_view.refresh()
        self.scenario_view.refresh()


def launch() -> None:
    app = QApplication(sys.argv)
    apply_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch()
