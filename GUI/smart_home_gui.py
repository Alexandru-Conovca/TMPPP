"""
Rebuilt Smart Home GUI focused on direct operation needs:
- Home page: all devices list + add device + navigation
- Scenarios page: preset/custom scenes + per-device overrides
- Rooms page: room management + assign/remove/control devices
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import (
    QEasingCurve,
    QPoint,
    QParallelAnimationGroup,
    QPauseAnimation,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QFormLayout,
    QGraphicsOpacityEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Allow running this file directly from GUI/.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from devices.extended_devices import (
    SmartAC,
    SmartAppliance,
    SmartCamera,
    SmartDoorLock,
    SmartLight,
    SmartSensor,
    SmartSpeaker,
    SmartTV,
    SmartThermostat,
)
from smart_home.integrated_system import IntegratedSmartHome
from smart_home.network_scanner import NetworkScanner, scan_local_network


class AddDeviceDialog(QDialog):
    """Dialog for adding devices after Wi-Fi scan and selection."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Add New Device")
        self.resize(800, 420)
        self.setObjectName("dialogRoot")

        self.discovered: List[Dict[str, str]] = []

        layout = QVBoxLayout(self)

        form_group = QGroupBox("Device Data")
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.room_input = QLineEdit()

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "light",
            "thermostat",
            "camera",
            "door_lock",
            "ac",
            "appliance",
            "speaker",
            "tv",
        ])

        form.addRow("Name:", self.name_input)
        form.addRow("Brand:", self.brand_input)
        form.addRow("Room:", self.room_input)
        form.addRow("Type:", self.type_combo)
        form_group.setLayout(form)
        layout.addWidget(form_group)

        scan_row = QHBoxLayout()
        self.scan_btn = QPushButton("Scan Wi-Fi Devices")
        self.scan_btn.clicked.connect(self.scan_wifi)
        scan_row.addWidget(self.scan_btn)

        self.selected_hint = QLabel("Select discovered device below")
        scan_row.addWidget(self.selected_hint)
        scan_row.addStretch()
        layout.addLayout(scan_row)

        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(5)
        self.scan_table.setHorizontalHeaderLabels(["Hostname/IP", "Type (Confidence)", "Brand", "IP Address", "MAC Address"])
        self.scan_table.verticalHeader().setVisible(False)
        self.scan_table.horizontalHeader().setStretchLastSection(True)
        self.scan_table.setShowGrid(False)
        self.scan_table.setAlternatingRowColors(True)
        self.scan_table.itemSelectionChanged.connect(self.apply_selected_discovery)
        layout.addWidget(self.scan_table)

        actions = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.cancel_btn = QPushButton("Cancel")
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        actions.addStretch()
        actions.addWidget(self.add_btn)
        actions.addWidget(self.cancel_btn)
        layout.addLayout(actions)

    def scan_wifi(self) -> None:
        """Scan local network and detect smart devices using real ARP/ping."""
        self.scan_btn.setText("Scanning...")
        self.scan_btn.setEnabled(False)
        self.scan_table.setRowCount(0)
        
        try:
            # Real network scanning
            devices = scan_local_network()
            
            self.discovered = [
                {
                    "ssid": device.hostname if device.hostname != "unknown" else device.ip,
                    "type": device.device_type,
                    "brand": device.brand,
                    "ip": device.ip,
                    "mac": device.mac,
                    "confidence": device.confidence,
                }
                for device in devices
            ]
            
            # Display in table
            self.scan_table.setRowCount(len(self.discovered))
            for row, item in enumerate(self.discovered):
                # Confidence indicator
                conf_text = f"{item['type']} ({item['confidence']}%)" if item['confidence'] > 0 else item['type']
                
                self.scan_table.setItem(row, 0, QTableWidgetItem(item["ssid"]))
                self.scan_table.setItem(row, 1, QTableWidgetItem(conf_text))
                self.scan_table.setItem(row, 2, QTableWidgetItem(item["brand"]))
                self.scan_table.setItem(row, 3, QTableWidgetItem(item["ip"]))
                self.scan_table.setItem(row, 4, QTableWidgetItem(item["mac"]))
            
            if self.discovered:
                self.scan_table.selectRow(0)
                self.selected_hint.setText(f"Found {len(self.discovered)} device(s) on network")
            else:
                self.selected_hint.setText("No devices found on network. Add manually or ensure devices are connected.")
        
        except Exception as e:
            QMessageBox.warning(self, "Scan failed", f"Network scan failed: {e}\n\nYou can still add devices manually.")
            self.selected_hint.setText("Scan failed - manual entry only")
        
        finally:
            self.scan_btn.setText("Scan Network")
            self.scan_btn.setEnabled(True)

    def apply_selected_discovery(self) -> None:
        row = self.scan_table.currentRow()
        if row < 0 or row >= len(self.discovered):
            return

        device = self.discovered[row]
        
        # Auto-fill with detected type if confident
        if device.get("confidence", 0) >= 70 and device.get("type") != "unknown":
            self.type_combo.setCurrentText(device["type"])
        
        self.brand_input.setText(device["brand"] if device["brand"] != "unknown" else "")
        if not self.name_input.text().strip():
            self.name_input.setText(device["ssid"])

    def get_payload(self) -> Optional[Dict[str, str]]:
        row = self.scan_table.currentRow()
        
        name = self.name_input.text().strip()
        brand = self.brand_input.text().strip()
        room = self.room_input.text().strip() or "Unassigned"
        dev_type = self.type_combo.currentText().strip()

        if not name or not brand:
            QMessageBox.warning(self, "Invalid data", "Name and brand are required.")
            return None
        
        # If device was selected from scan, include metadata
        if row >= 0 and row < len(self.discovered):
            metadata = self.discovered[row]
            # Could store IP, MAC, confidence for future use

        return {
            "name": name,
            "brand": brand,
            "room": room,
            "type": dev_type,
        }


class SmartHomeGUI(QMainWindow):
    """Smart home UI with Home, Scenarios, and Rooms pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Smart Home")
        self.resize(1300, 820)

        self.system = IntegratedSmartHome()
        self.custom_rooms = set()
        self.scene_overrides: Dict[str, List[Dict[str, str]]] = {}
        self.scene_id_by_name: Dict[str, str] = {}
        self._page_fade_anim: Optional[QPropertyAnimation] = None
        self._page_slide_anim: Optional[QPropertyAnimation] = None
        self._page_group_anim: Optional[QParallelAnimationGroup] = None
        self._button_anims: List[QPropertyAnimation] = []
        self._card_anims: List[Any] = []

        self._seed_demo_devices()
        self._seed_base_scenes()
        self._subscribe_to_updates()

        self._build_ui()
        self._apply_modern_theme()
        self._style_tables()
        self._enable_button_micro_animations()
        self._wire_timers()
        self.refresh_all()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _subscribe_to_updates(self) -> None:
        """Subscribe GUI to device state changes (Observer pattern)."""
        def on_device_update(event_data: Dict[str, Any]) -> None:
            self.refresh_all()

        self.system.subscribe_to_updates(on_device_update)

    def _seed_demo_devices(self) -> None:
        self.system.system.add_light("Living Main", "Philips", "Living Room", 70)
        self.system.system.add_light("Bedroom Lamp", "Xiaomi", "Bedroom", 40)
        self.system.system.add_thermostat("Main Thermostat", "Nest", "Hall", 21)
        self.system.system.add_camera("Front Door Cam", "Ring", "Entrance", "1080p")
        self.system.system.add_door_lock("Main Lock", "Yale", "Entrance")
        self.system.system.add_speaker("Kitchen Speaker", "Amazon", "Kitchen")

    def _seed_base_scenes(self) -> None:
        morning_id = self.system.system.create_morning_scene()

        day = self.system.system.scene_manager.create_scene("Day", "Day mode: active lights and comfort")
        day.add_action(lambda: self.system.system.turn_on_lights())
        day.add_action(lambda: self.system.system.set_temperature(22))
        day_id = day.scene_id

        evening_id = self.system.system.create_evening_scene()

        night = self.system.system.scene_manager.create_scene("Night", "Night mode: lights off, lock doors")
        night.add_action(lambda: self.system.system.turn_off_lights())
        night.add_action(lambda: self.system.system.lock_all_doors())
        night_id = night.scene_id

        self.scene_id_by_name = {
            "Morning": morning_id,
            "Day": day_id,
            "Evening": evening_id,
            "Night": night_id,
        }

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        top = QHBoxLayout()
        top_panel = QWidget()
        top_panel.setObjectName("topPanel")
        top_panel_layout = QHBoxLayout(top_panel)
        top_panel_layout.setContentsMargins(14, 10, 14, 10)
        top_panel_layout.setSpacing(12)

        self.system_status = QLabel("System: online")
        self.system_status.setObjectName("statusChip")
        top_panel_layout.addWidget(self.system_status)
        top_panel_layout.addStretch()

        self.page_title = QLabel("Smart Home Control")
        self.page_title.setObjectName("heroTitle")
        top_panel_layout.addWidget(self.page_title)
        top_panel_layout.addStretch()

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("clockChip")
        top_panel_layout.addWidget(self.clock_label)

        top.addWidget(top_panel)
        root_layout.addLayout(top)

        self.stack = QStackedWidget()
        self.stack.setObjectName("pageStack")
        self.home_page = self._build_home_page()
        self.scenes_page = self._build_scenarios_page()
        self.rooms_page = self._build_rooms_page()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.scenes_page)
        self.stack.addWidget(self.rooms_page)

        root_layout.addWidget(self.stack)

    def _wire_timers(self) -> None:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(1500)

    # ------------------------------------------------------------------
    # Home page
    # ------------------------------------------------------------------

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("homePage")
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        nav = QHBoxLayout()
        home_label = QLabel("Home")
        home_label.setObjectName("sectionTitle")
        nav.addWidget(home_label)
        nav.addStretch()

        add_btn = QPushButton("Add Device")
        add_btn.clicked.connect(self.open_add_device_dialog)
        nav.addWidget(add_btn)

        to_scenes_btn = QPushButton("Go to Scenarios")
        to_scenes_btn.clicked.connect(lambda: self._switch_page(self.scenes_page, "Scenarios"))
        nav.addWidget(to_scenes_btn)

        to_rooms_btn = QPushButton("Go to Rooms")
        to_rooms_btn.clicked.connect(lambda: self._switch_page(self.rooms_page, "Rooms"))
        nav.addWidget(to_rooms_btn)

        layout.addLayout(nav)

        cards_group = QGroupBox("Quick Device Cards")
        cards_group.setObjectName("cardGroup")
        self.cards_grid = QGridLayout(cards_group)
        self.cards_grid.setSpacing(10)
        layout.addWidget(cards_group)

        self.devices_table = QTableWidget()
        self.devices_table.setObjectName("dataTable")
        self.devices_table.setColumnCount(6)
        self.devices_table.setHorizontalHeaderLabels(["Name", "State", "Room", "Type", "Brand", "ID"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.devices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.devices_table)

        return page

    def open_add_device_dialog(self) -> None:
        dlg = AddDeviceDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return

        payload = dlg.get_payload()
        if not payload:
            return

        dev_type = payload["type"]
        name = payload["name"]
        brand = payload["brand"]
        room = payload["room"]

        try:
            # Generate unique device ID
            device_count = len(self.system.system.devices)
            device_id = f"{dev_type}_{device_count + 1:03d}"
            
            # Add device using integrated system with database
            success = self.system.add_device_to_db(device_id, name, dev_type, brand, room)
            
            if success:
                QMessageBox.information(self, "Success", f"Device '{name}' added successfully!")
                self.refresh_device_cards()
            else:
                QMessageBox.critical(self, "Error", f"Failed to add device '{name}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding device: {e}")

    # ------------------------------------------------------------------
    # Scenarios page
    # ------------------------------------------------------------------

    def _build_scenarios_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("scenesPage")
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Scenarios")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(lambda: self._switch_page(self.home_page, "Smart Home Control"))
        header.addWidget(back_btn)

        layout.addLayout(header)

        self.scenes_table = QTableWidget()
        self.scenes_table.setObjectName("dataTable")
        self.scenes_table.setColumnCount(4)
        self.scenes_table.setHorizontalHeaderLabels(["Name", "Description", "Actions", "Scene ID"])
        self.scenes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.scenes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.scenes_table)

        actions_row = QHBoxLayout()
        activate_btn = QPushButton("Activate Selected")
        activate_btn.clicked.connect(self.activate_selected_scene)
        actions_row.addWidget(activate_btn)

        add_scene_btn = QPushButton("Add Custom Scenario")
        add_scene_btn.clicked.connect(self.add_custom_scene)
        actions_row.addWidget(add_scene_btn)

        actions_row.addStretch()
        layout.addLayout(actions_row)

        edit_group = QGroupBox("Per-Device Scenario Overrides")
        edit_group.setObjectName("cardGroup")
        edit_layout = QGridLayout(edit_group)

        self.override_scene_combo = QComboBox()
        self.override_device_combo = QComboBox()
        self.override_action_combo = QComboBox()
        self.override_action_combo.addItems([
            "on",
            "off",
            "toggle",
            "set_brightness",
            "set_temp",
            "lock",
            "unlock",
            "record_on",
            "record_off",
            "set_volume",
            "play",
            "launch_app",
        ])
        self.override_value_input = QLineEdit()
        self.override_value_input.setPlaceholderText("Optional value (e.g. 75, 22.5, Spotify)")

        add_override_btn = QPushButton("Add/Update Rule")
        add_override_btn.clicked.connect(self.add_override_rule)
        remove_override_btn = QPushButton("Remove Selected Rule")
        remove_override_btn.clicked.connect(self.remove_override_rule)

        self.overrides_list = QListWidget()

        edit_layout.addWidget(QLabel("Scenario:"), 0, 0)
        edit_layout.addWidget(self.override_scene_combo, 0, 1)
        edit_layout.addWidget(QLabel("Device:"), 1, 0)
        edit_layout.addWidget(self.override_device_combo, 1, 1)
        edit_layout.addWidget(QLabel("Action:"), 2, 0)
        edit_layout.addWidget(self.override_action_combo, 2, 1)
        edit_layout.addWidget(QLabel("Value:"), 3, 0)
        edit_layout.addWidget(self.override_value_input, 3, 1)
        edit_layout.addWidget(add_override_btn, 4, 0)
        edit_layout.addWidget(remove_override_btn, 4, 1)
        edit_layout.addWidget(self.overrides_list, 5, 0, 1, 2)

        self.override_scene_combo.currentTextChanged.connect(self.refresh_overrides_list)

        layout.addWidget(edit_group)
        return page

    def add_custom_scene(self) -> None:
        name, ok = QInputDialog.getText(self, "Custom scenario", "Scenario name:")
        if not ok or not name.strip():
            return

        desc, _ = QInputDialog.getText(self, "Custom scenario", "Description:")
        scene = self.system.scene_manager.create_scene(name.strip(), desc.strip())
        self.scene_overrides.setdefault(scene.scene_id, [])
        self.refresh_all()

    def activate_selected_scene(self) -> None:
        row = self.scenes_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select scene", "Select a scenario first.")
            return

        scene_id_item = self.scenes_table.item(row, 3)
        if scene_id_item is None:
            return

        scene_id = scene_id_item.text()
        result = self.system.system.activate_scene(scene_id)
        override_count, errors = self._apply_scene_overrides(scene_id)

        message = (
            f"Scene: {result.get('scene', scene_id)}\n"
            f"Base actions: {result.get('actions_executed', 0)}\n"
            f"Override actions: {override_count}"
        )
        if errors:
            message += "\nErrors:\n" + "\n".join(errors[:5])

        QMessageBox.information(self, "Scenario executed", message)
        self.refresh_all()

    def add_override_rule(self) -> None:
        scene_id = self.override_scene_combo.currentData()
        device_id = self.override_device_combo.currentData()
        action = self.override_action_combo.currentText()
        value = self.override_value_input.text().strip()

        if not scene_id or not device_id:
            QMessageBox.warning(self, "Missing data", "Select a scenario and a device.")
            return

        rules = self.scene_overrides.setdefault(scene_id, [])

        # Replace existing rule for same device with new one.
        rules = [r for r in rules if r["device_id"] != device_id]
        rules.append({"device_id": device_id, "action": action, "value": value})
        self.scene_overrides[scene_id] = rules

        self.refresh_overrides_list()

    def remove_override_rule(self) -> None:
        scene_id = self.override_scene_combo.currentData()
        row = self.overrides_list.currentRow()
        if not scene_id or row < 0:
            return

        rules = self.scene_overrides.get(scene_id, [])
        if row >= len(rules):
            return

        rules.pop(row)
        self.scene_overrides[scene_id] = rules
        self.refresh_overrides_list()

    def refresh_overrides_list(self) -> None:
        self.overrides_list.clear()
        scene_id = self.override_scene_combo.currentData()
        if not scene_id:
            return

        rules = self.scene_overrides.get(scene_id, [])
        for r in rules:
            self.overrides_list.addItem(f"{r['device_id']} -> {r['action']}({r['value']})")

    def _apply_scene_overrides(self, scene_id: str) -> tuple[int, List[str]]:
        applied = 0
        errors: List[str] = []

        for rule in self.scene_overrides.get(scene_id, []):
            device = self.system.system.get_device(rule["device_id"])
            if device is None:
                errors.append(f"Device not found: {rule['device_id']}")
                continue

            try:
                self._execute_device_action(device, rule["action"], rule["value"])
                applied += 1
            except Exception as exc:
                errors.append(f"{rule['device_id']}: {exc}")

        return applied, errors

    # ------------------------------------------------------------------
    # Rooms page
    # ------------------------------------------------------------------

    def _build_rooms_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("roomsPage")
        layout = QHBoxLayout(page)
        layout.setSpacing(12)

        left = QVBoxLayout()
        title = QLabel("Rooms")
        title.setObjectName("sectionTitle")
        left.addWidget(title)

        self.rooms_list = QListWidget()
        self.rooms_list.setObjectName("roomList")
        self.rooms_list.currentTextChanged.connect(self.refresh_room_devices_table)
        left.addWidget(self.rooms_list)

        room_actions = QHBoxLayout()
        add_room_btn = QPushButton("Add Room")
        add_room_btn.clicked.connect(self.add_room)
        remove_room_btn = QPushButton("Remove Room")
        remove_room_btn.clicked.connect(self.remove_room)
        room_actions.addWidget(add_room_btn)
        room_actions.addWidget(remove_room_btn)
        left.addLayout(room_actions)

        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(lambda: self._switch_page(self.home_page, "Smart Home Control"))
        left.addWidget(back_btn)
        left.addStretch()

        right = QVBoxLayout()
        self.room_devices_table = QTableWidget()
        self.room_devices_table.setObjectName("dataTable")
        self.room_devices_table.setColumnCount(5)
        self.room_devices_table.setHorizontalHeaderLabels(["Name", "State", "Type", "Brand", "ID"])
        self.room_devices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.room_devices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right.addWidget(self.room_devices_table)

        device_actions = QHBoxLayout()
        add_to_room_btn = QPushButton("Add Device to Room")
        add_to_room_btn.clicked.connect(self.add_existing_device_to_room)
        remove_from_room_btn = QPushButton("Remove Device from Room")
        remove_from_room_btn.clicked.connect(self.remove_device_from_room)
        toggle_btn = QPushButton("Toggle Selected Device")
        toggle_btn.clicked.connect(self.toggle_selected_room_device)

        device_actions.addWidget(add_to_room_btn)
        device_actions.addWidget(remove_from_room_btn)
        device_actions.addWidget(toggle_btn)
        right.addLayout(device_actions)

        layout.addLayout(left, 1)
        layout.addLayout(right, 3)
        return page

    def _apply_modern_theme(self) -> None:
        """Apply a modern, colorful visual style for the whole app."""
        self.setStyleSheet(
            """
            * {
                font-family: "Segoe UI Variable", "Poppins", "Bahnschrift", sans-serif;
                font-size: 13px;
                color: #e6edf5;
            }

            QMainWindow {
                background: #0e1726;
            }

            QWidget#appRoot {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111b2e,
                    stop:0.45 #0f2238,
                    stop:1 #13304a);
            }

            QWidget#topPanel {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.13);
                border-radius: 14px;
            }

            QLabel#heroTitle {
                font-size: 21px;
                font-weight: 700;
                color: #f2f6ff;
                letter-spacing: 0.5px;
            }

            QLabel#statusChip {
                background: rgba(46, 204, 113, 0.24);
                border: 1px solid rgba(46, 204, 113, 0.55);
                border-radius: 12px;
                padding: 6px 10px;
                font-weight: 600;
            }

            QLabel#clockChip {
                background: rgba(88, 166, 255, 0.21);
                border: 1px solid rgba(88, 166, 255, 0.5);
                border-radius: 12px;
                padding: 6px 10px;
                font-weight: 600;
            }

            QStackedWidget#pageStack,
            QWidget#homePage,
            QWidget#scenesPage,
            QWidget#roomsPage,
            QDialog#dialogRoot {
                background: rgba(3, 9, 20, 0.45);
                border-radius: 16px;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: #f1f5ff;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5a3,
                    stop:1 #0f9d88);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #19b4b1,
                    stop:1 #17af97);
            }

            QPushButton:pressed {
                background: #0a7c6d;
            }

            QGroupBox#cardGroup,
            QGroupBox {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 12px;
                margin-top: 8px;
                padding-top: 10px;
                font-weight: 700;
            }

            QGroupBox::title {
                left: 10px;
                padding: 0 4px;
                color: #d9e5ff;
            }

            QFrame#deviceCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 35, 58, 0.94),
                    stop:1 rgba(16, 58, 74, 0.88));
                border: 1px solid rgba(20, 184, 166, 0.24);
                border-radius: 12px;
            }

            QLabel#cardTitle {
                font-size: 14px;
                font-weight: 700;
                color: #f1f5ff;
            }

            QLabel#cardMeta {
                color: #b7c4dd;
                font-size: 12px;
            }

            QLabel#cardBadge {
                border-radius: 9px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
            }

            QLabel[badgeKind="online"] {
                background: rgba(46, 204, 113, 0.20);
                border: 1px solid rgba(46, 204, 113, 0.55);
                color: #c8ffd9;
            }

            QLabel[badgeKind="offline"] {
                background: rgba(239, 68, 68, 0.20);
                border: 1px solid rgba(239, 68, 68, 0.55);
                color: #ffd0d0;
            }

            QLabel[badgeKind="neutral"] {
                background: rgba(88, 166, 255, 0.20);
                border: 1px solid rgba(88, 166, 255, 0.55);
                color: #d8e9ff;
            }

            QLineEdit,
            QComboBox,
            QListWidget,
            QTableWidget {
                background: rgba(8, 16, 30, 0.82);
                alternate-background-color: rgba(12, 24, 42, 0.90);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 10px;
                padding: 6px;
                selection-background-color: rgba(20, 184, 166, 0.45);
                selection-color: #ffffff;
            }

            QTableWidget::item {
                background: rgba(8, 16, 30, 0.82);
            }

            QTableWidget::item:alternate {
                background: rgba(12, 24, 42, 0.90);
            }

            QHeaderView {
                background: rgba(13, 26, 46, 0.96);
                border: none;
            }

            QHeaderView::section {
                background: rgba(18, 33, 58, 0.98);
                color: #dfe9ff;
                border: none;
                border-right: 1px solid rgba(20, 184, 166, 0.28);
                border-bottom: 1px solid rgba(20, 184, 166, 0.34);
                padding: 8px;
                font-weight: 700;
            }

            QHeaderView::section:horizontal:last {
                border-right: none;
            }

            QTableCornerButton::section,
            QAbstractScrollArea::corner {
                background: rgba(255, 255, 255, 0.08);
                border: none;
            }

            QScrollBar:vertical,
            QScrollBar:horizontal {
                background: transparent;
                border: none;
            }

            QScrollBar::handle:vertical,
            QScrollBar::handle:horizontal {
                background: rgba(120, 170, 230, 0.65);
                border-radius: 5px;
                min-height: 24px;
                min-width: 24px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
                width: 0px;
                height: 0px;
            }
            """
        )

    def _style_tables(self) -> None:
        """Tune table behavior for a polished app feel."""
        tables = [self.devices_table, self.scenes_table, self.room_devices_table]
        for table in tables:
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setShowGrid(False)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def add_room(self) -> None:
        room, ok = QInputDialog.getText(self, "Add room", "Room name:")
        if not ok or not room.strip():
            return
        self.custom_rooms.add(room.strip())
        self.refresh_rooms_list()

    def remove_room(self) -> None:
        room = self.rooms_list.currentItem().text() if self.rooms_list.currentItem() else ""
        if not room:
            return

        devices_in_room = [did for did, dev, state in self._device_triplets() if self._device_room(dev, state) == room]
        if devices_in_room:
            QMessageBox.warning(self, "Room not empty", "Remove or reassign devices before deleting this room.")
            return

        if room in self.custom_rooms:
            self.custom_rooms.remove(room)

        self.refresh_rooms_list()

    def add_existing_device_to_room(self) -> None:
        room = self.rooms_list.currentItem().text() if self.rooms_list.currentItem() else ""
        if not room:
            QMessageBox.information(self, "Select room", "Select a room first.")
            return

        options = [f"{did} | {state.get('name', did)}" for did, dev, state in self._device_triplets()]
        if not options:
            return

        selected, ok = QInputDialog.getItem(self, "Assign device", "Choose device:", options, 0, False)
        if not ok or not selected:
            return

        device_id = selected.split(" | ", 1)[0]
        device = self.system.system.get_device(device_id)
        if device is None:
            return

        self._set_device_room(device, room)
        self.custom_rooms.add(room)
        self.refresh_all()

    def remove_device_from_room(self) -> None:
        row = self.room_devices_table.currentRow()
        if row < 0:
            return

        device_id_item = self.room_devices_table.item(row, 4)
        if device_id_item is None:
            return

        device = self.system.system.get_device(device_id_item.text())
        if device is None:
            return

        self._set_device_room(device, "Unassigned")
        self.custom_rooms.add("Unassigned")
        self.refresh_all()

    def toggle_selected_room_device(self) -> None:
        row = self.room_devices_table.currentRow()
        if row < 0:
            return

        device_id_item = self.room_devices_table.item(row, 4)
        if device_id_item is None:
            return

        device = self.system.system.get_device(device_id_item.text())
        if device is None:
            return

        self._toggle_device(device)
        self.refresh_all()

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh_all(self) -> None:
        self.clock_label.setText(__import__("datetime").datetime.now().strftime("%H:%M:%S"))
        self.refresh_devices_table()
        self.refresh_device_cards()
        self.refresh_scenes_table()
        self.refresh_override_selectors()
        self.refresh_rooms_list()
        self.refresh_room_devices_table()

    def refresh_devices_table(self) -> None:
        items = self._device_triplets()
        self.devices_table.setRowCount(len(items))

        for row, (device_id, device, state) in enumerate(items):
            name = state.get("name", device_id)
            status = self._device_status(device, state)
            room = self._device_room(device, state)
            dev_type = type(device).__name__
            brand = state.get("brand", getattr(device, "brand", "-"))
            icon = self._device_icon(device)

            self.devices_table.setItem(row, 0, QTableWidgetItem(f"{icon}  {str(name)}"))
            status_item = QTableWidgetItem(str(status))
            self._style_status_item(status_item, status)
            self.devices_table.setItem(row, 1, status_item)
            self.devices_table.setItem(row, 2, QTableWidgetItem(str(room)))
            self.devices_table.setItem(row, 3, QTableWidgetItem(dev_type))
            self.devices_table.setItem(row, 4, QTableWidgetItem(str(brand)))
            self.devices_table.setItem(row, 5, QTableWidgetItem(device_id))

    def refresh_scenes_table(self) -> None:
        scenes = self.system.system.scene_manager.get_all_scenes()
        self.scenes_table.setRowCount(len(scenes))

        for row, scene in enumerate(scenes):
            scene_name = scene.get("name", "")
            self.scenes_table.setItem(row, 0, QTableWidgetItem(f"{self._scene_icon(scene_name)}  {scene_name}"))
            self.scenes_table.setItem(row, 1, QTableWidgetItem(scene.get("description", "")))
            self.scenes_table.setItem(row, 2, QTableWidgetItem(str(scene.get("actions_count", 0))))
            self.scenes_table.setItem(row, 3, QTableWidgetItem(scene.get("id", "")))

    def refresh_device_cards(self) -> None:
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        items = self._device_triplets()
        for index, (device_id, device, state) in enumerate(items):
            card = QFrame()
            card.setObjectName("deviceCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(6)

            name = state.get("name", device_id)
            status = self._device_status(device, state)
            room = self._device_room(device, state)

            title = QLabel(f"{self._device_icon(device)}  {name}")
            title.setObjectName("cardTitle")
            card_layout.addWidget(title)

            meta = QLabel(f"{type(device).__name__} • {room}")
            meta.setObjectName("cardMeta")
            card_layout.addWidget(meta)

            badge = QLabel(status.upper())
            badge.setObjectName("cardBadge")
            badge.setProperty("badgeKind", self._status_kind(status))
            badge.style().unpolish(badge)
            badge.style().polish(badge)
            card_layout.addWidget(badge)

            quick_btn = QPushButton("Toggle")
            quick_btn.clicked.connect(lambda _=False, did=device_id: self._toggle_device_by_id(did))
            card_layout.addWidget(quick_btn)

            row = index // 4
            col = index % 4
            self.cards_grid.addWidget(card, row, col)
            self._animate_card_appearance(card, index * 45)

        self._enable_button_micro_animations()

    def _animate_card_appearance(self, card: QWidget, delay_ms: int) -> None:
        effect = QGraphicsOpacityEffect(card)
        effect.setOpacity(0.0)
        card.setGraphicsEffect(effect)

        group = QSequentialAnimationGroup(card)
        pause = QPauseAnimation(max(0, delay_ms), group)
        fade = QPropertyAnimation(effect, b"opacity", group)
        fade.setDuration(240)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)

        group.addAnimation(pause)
        group.addAnimation(fade)

        def _cleanup() -> None:
            if card is not None:
                card.setGraphicsEffect(None)
            if group in self._card_anims:
                self._card_anims.remove(group)

        group.finished.connect(_cleanup)
        self._card_anims.append(group)
        group.start()

    def refresh_override_selectors(self) -> None:
        current_scene_id = self.override_scene_combo.currentData()

        self.override_scene_combo.blockSignals(True)
        self.override_scene_combo.clear()
        for scene in self.system.system.scene_manager.get_all_scenes():
            self.override_scene_combo.addItem(f"{scene['name']} ({scene['id']})", scene["id"])

        if current_scene_id:
            idx = self.override_scene_combo.findData(current_scene_id)
            if idx >= 0:
                self.override_scene_combo.setCurrentIndex(idx)

        self.override_scene_combo.blockSignals(False)

        current_device_id = self.override_device_combo.currentData()
        self.override_device_combo.clear()
        for did, dev, state in self._device_triplets():
            self.override_device_combo.addItem(f"{state.get('name', did)} ({did})", did)

        if current_device_id:
            idx = self.override_device_combo.findData(current_device_id)
            if idx >= 0:
                self.override_device_combo.setCurrentIndex(idx)

        self.refresh_overrides_list()

    def refresh_rooms_list(self) -> None:
        selected = self.rooms_list.currentItem().text() if self.rooms_list.currentItem() else ""

        rooms = set(self.custom_rooms)
        for did, device, state in self._device_triplets():
            rooms.add(self._device_room(device, state))

        cleaned = sorted(r for r in rooms if r)

        self.rooms_list.clear()
        self.rooms_list.addItems(cleaned)

        if selected:
            for i in range(self.rooms_list.count()):
                if self.rooms_list.item(i).text() == selected:
                    self.rooms_list.setCurrentRow(i)
                    break
        elif self.rooms_list.count() > 0:
            self.rooms_list.setCurrentRow(0)

    def refresh_room_devices_table(self) -> None:
        room = self.rooms_list.currentItem().text() if self.rooms_list.currentItem() else ""
        items = [triplet for triplet in self._device_triplets() if self._device_room(triplet[1], triplet[2]) == room]

        self.room_devices_table.setRowCount(len(items))
        for row, (device_id, device, state) in enumerate(items):
            self.room_devices_table.setItem(row, 0, QTableWidgetItem(state.get("name", device_id)))
            self.room_devices_table.setItem(row, 1, QTableWidgetItem(self._device_status(device, state)))
            self.room_devices_table.setItem(row, 2, QTableWidgetItem(type(device).__name__))
            self.room_devices_table.setItem(row, 3, QTableWidgetItem(state.get("brand", getattr(device, "brand", "-"))))
            self.room_devices_table.setItem(row, 4, QTableWidgetItem(device_id))

    # ------------------------------------------------------------------
    # Device helpers
    # ------------------------------------------------------------------

    def _device_triplets(self) -> List[tuple[str, Any, Dict[str, Any]]]:
        result: List[tuple[str, Any, Dict[str, Any]]] = []
        for device_id, device in self.system.system.devices.items():
            state = device.get_state() if hasattr(device, "get_state") else {}
            result.append((device_id, device, state))
        return result

    def _device_room(self, device: Any, state: Dict[str, Any]) -> str:
        return (
            str(state.get("room") or state.get("location") or getattr(device, "room", None) or getattr(device, "location", None) or "Unassigned")
        )

    def _set_device_room(self, device: Any, room: str) -> None:
        if hasattr(device, "room"):
            device.room = room
        elif hasattr(device, "location"):
            device.location = room

    def _device_status(self, device: Any, state: Dict[str, Any]) -> str:
        if "status" in state:
            return str(state["status"])
        if "locked" in state:
            return "locked" if bool(state.get("locked")) else "unlocked"
        return "unknown"

    def _status_kind(self, status: str) -> str:
        normalized = status.lower()
        if any(token in normalized for token in ["on", "active", "playing", "recording", "auto", "locked"]):
            return "online"
        if any(token in normalized for token in ["off", "inactive", "paused", "stopped", "error"]):
            return "offline"
        return "neutral"

    def _style_status_item(self, item: QTableWidgetItem, status: str) -> None:
        kind = self._status_kind(status)
        if kind == "online":
            item.setBackground(QColor(24, 84, 56, 170))
            item.setForeground(QColor(201, 255, 222))
        elif kind == "offline":
            item.setBackground(QColor(106, 38, 38, 170))
            item.setForeground(QColor(255, 213, 213))
        else:
            item.setBackground(QColor(38, 61, 100, 150))
            item.setForeground(QColor(219, 232, 255))

    def _device_icon(self, device: Any) -> str:
        if isinstance(device, SmartLight):
            return "💡"
        if isinstance(device, SmartThermostat):
            return "🌡️"
        if isinstance(device, SmartCamera):
            return "📷"
        if isinstance(device, SmartDoorLock):
            return "🔐"
        if isinstance(device, SmartSpeaker):
            return "🔊"
        if isinstance(device, SmartTV):
            return "📺"
        if isinstance(device, SmartAC):
            return "❄️"
        if isinstance(device, SmartAppliance):
            return "🔌"
        if isinstance(device, SmartSensor):
            return "📡"
        return "⚙️"

    def _scene_icon(self, scene_name: str) -> str:
        normalized = scene_name.strip().lower()
        if "morning" in normalized:
            return "🌅"
        if "day" in normalized:
            return "☀️"
        if "evening" in normalized:
            return "🌇"
        if "night" in normalized:
            return "🌙"
        return "🎬"

    def _switch_page(self, page: QWidget, title: str) -> None:
        if self.stack.currentWidget() is page:
            self.page_title.setText(title)
            return

        self.page_title.setText(title)
        self.stack.setCurrentWidget(page)

        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        page.raise_()

        fade_anim = QPropertyAnimation(effect, b"opacity", self)
        fade_anim.setDuration(220)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(QEasingCurve.OutCubic)

        final_pos = page.pos()
        start_pos = QPoint(final_pos.x() + 34, final_pos.y())
        page.move(start_pos)

        slide_anim = QPropertyAnimation(page, b"pos", self)
        slide_anim.setDuration(220)
        slide_anim.setStartValue(start_pos)
        slide_anim.setEndValue(final_pos)
        slide_anim.setEasingCurve(QEasingCurve.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade_anim)
        group.addAnimation(slide_anim)

        def clear_effect() -> None:
            page.setGraphicsEffect(None)
            page.move(final_pos)

        group.finished.connect(clear_effect)

        self._page_fade_anim = fade_anim
        self._page_slide_anim = slide_anim
        self._page_group_anim = group
        group.start()

    def _toggle_device_by_id(self, device_id: str) -> None:
        """Toggle device using Command pattern via IntegratedSmartHome."""
        device = self.system.system.get_device(device_id)
        if device is None:
            return

        status = str(device.get_state().get("status", "unknown")).lower()
        cmd_type = "off" if "on" in status or "active" in status else "on"
        self.system.execute_device_command(device_id, cmd_type)

    def _enable_button_micro_animations(self) -> None:
        for button in self.findChildren(QPushButton):
            if bool(button.property("pulseConnected")):
                continue

            button.setProperty("pulseConnected", True)
            button.clicked.connect(lambda _=False, b=button: self._pulse_button(b))

    def _pulse_button(self, button: QPushButton) -> None:
        effect = button.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(button)
            effect.setOpacity(1.0)
            button.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(170)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.setKeyValueAt(0.0, 1.0)
        anim.setKeyValueAt(0.5, 0.72)
        anim.setKeyValueAt(1.0, 1.0)

        def _cleanup() -> None:
            if anim in self._button_anims:
                self._button_anims.remove(anim)

        anim.finished.connect(_cleanup)
        self._button_anims.append(anim)
        anim.start()

    def _toggle_device(self, device: Any) -> None:
        # Ordered checks avoid calling wrong methods for specific classes.
        if isinstance(device, SmartDoorLock):
            if device.locked:
                device.unlock("ui")
            else:
                device.lock("ui")
            return

        if isinstance(device, SmartCamera):
            if device.recording:
                device.stop_recording()
            else:
                device.start_recording()
            return

        if isinstance(device, SmartSpeaker):
            if device.playing:
                device.pause()
            else:
                device.play("Radio")
            return

        if isinstance(device, SmartThermostat):
            device.set_mode("off" if device.mode != "off" else "auto")
            return

        # Generic on/off handling.
        if hasattr(device, "status") and getattr(device, "status").value in ["on", "active"] and hasattr(device, "turn_off"):
            device.turn_off()
            return

        if hasattr(device, "turn_on"):
            device.turn_on()

    def _execute_device_action(self, device: Any, action: str, raw_value: str) -> None:
        value = raw_value.strip()

        if action == "toggle":
            self._toggle_device(device)
            return
        if action == "on":
            if hasattr(device, "turn_on"):
                device.turn_on()
            return
        if action == "off":
            if hasattr(device, "turn_off"):
                device.turn_off()
            elif isinstance(device, SmartThermostat):
                device.set_mode("off")
            return
        if action == "set_brightness" and isinstance(device, SmartLight):
            device.set_brightness(int(value or "100"))
            return
        if action == "set_temp" and isinstance(device, SmartThermostat):
            device.set_target_temperature(float(value or "21"))
            return
        if action == "lock" and isinstance(device, SmartDoorLock):
            device.lock("scene")
            return
        if action == "unlock" and isinstance(device, SmartDoorLock):
            device.unlock("scene")
            return
        if action == "record_on" and isinstance(device, SmartCamera):
            device.start_recording()
            return
        if action == "record_off" and isinstance(device, SmartCamera):
            device.stop_recording()
            return
        if action == "set_volume" and isinstance(device, SmartSpeaker):
            device.set_volume(int(value or "50"))
            return
        if action == "play" and isinstance(device, SmartSpeaker):
            device.play(value or "Playlist")
            return
        if action == "launch_app" and isinstance(device, SmartTV):
            device.launch_app(value or "YouTube")
            return


class MainWindow(SmartHomeGUI):
    """Compatibility class for legacy launcher path."""



def main() -> None:
    app = QApplication(sys.argv)
    window = SmartHomeGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
