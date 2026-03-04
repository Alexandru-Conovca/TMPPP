"""
DeviceView widget: shows devices, allows operate and clone actions.
Uses HomeManager (Singleton) data. Double-click or button triggers operate().
"""
from typing import Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from manager.home_manager import HomeManager
from devices.device import Device


class DeviceView(QWidget):
    devices_changed = pyqtSignal()

    def __init__(self, manager: HomeManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._manager = manager
        self._brand_filter: Optional[str] = None
        self._type_filter: Optional[str] = None

        self.title = QLabel("Devices")
        self.title.setStyleSheet("font-weight: 700; font-size: 14px;")

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._handle_operate)

        self.status_label = QLabel("Double-click to operate. Select and press Clone to duplicate.")
        self.status_label.setObjectName("status")
        self.status_label.setProperty("class", "hint")
        self.status_label.setStyleSheet("color: #6b7280;")

        self.operate_button = QPushButton("Operate")
        self.clone_button = QPushButton("Clone")
        self.operate_button.clicked.connect(self._handle_operate)
        self.clone_button.clicked.connect(self._handle_clone)

        buttons = QHBoxLayout()
        buttons.addWidget(self.operate_button)
        buttons.addWidget(self.clone_button)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.list_widget)
        layout.addLayout(buttons)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def set_filters(self, brand: Optional[str], device_type: Optional[str]) -> None:
        self._brand_filter = brand
        self._type_filter = device_type

    def refresh(self) -> None:
        self.list_widget.clear()
        for device in self._manager.devices:
            if self._brand_filter and device.brand != self._brand_filter:
                continue
            if self._type_filter and device.device_type() != self._type_filter:
                continue
            item = QListWidgetItem(f"{device.device_type()} · {device.name} · {device.brand}")
            item.setData(Qt.UserRole, device)
            self.list_widget.addItem(item)

    def _current_device(self) -> Optional[Device]:
        item = self.list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.UserRole)

    def _handle_operate(self) -> None:
        device = self._current_device()
        if device is None:
            return
        result = device.operate()
        self.status_label.setText(result)
        self.refresh()
        self.devices_changed.emit()

    def _handle_clone(self) -> None:
        device = self._current_device()
        if device is None:
            return
        cloned = device.clone()
        self._manager.add_device(cloned)
        self.status_label.setText(f"Cloned: {cloned}")
        self.refresh()
        self.devices_changed.emit()

    def show_message(self, title: str, text: str) -> None:
        QMessageBox.information(self, title, text)
