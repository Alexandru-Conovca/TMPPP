"""
Singleton HomeManager keeps global state of devices and scenarios.
"""
from typing import List
from devices.device import Device
from scenarios.builder import Scenario


class HomeManager:
    _instance = None

    def __init__(self) -> None:
        if HomeManager._instance is not None:
            raise RuntimeError("Use get_instance() to access HomeManager")
        self.devices: List[Device] = []
        self.scenarios: List[Scenario] = []

    @classmethod
    def get_instance(cls) -> "HomeManager":
        if cls._instance is None:
            cls._instance = HomeManager()
        return cls._instance

    def add_device(self, device: Device) -> None:
        self.devices.append(device)

    def add_scenario(self, scenario: Scenario) -> None:
        self.scenarios.append(scenario)

    def describe(self) -> str:
        lines = ["Devices:"]
        if not self.devices:
            lines.append("  (none)")
        else:
            for idx, device in enumerate(self.devices, start=1):
                lines.append(f"  {idx}. {device}")
        lines.append("Scenarios:")
        if not self.scenarios:
            lines.append("  (none)")
        else:
            for idx, scenario in enumerate(self.scenarios, start=1):
                lines.append(f"  {idx}. {scenario.summary()}")
        return "\n".join(lines)
