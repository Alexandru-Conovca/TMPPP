from typing import List

from devices.device import Alarm, Camera, Device
from manager.home_manager import HomeManager
from scenarios.builder import Scenario
from structural.composite.composite import DeviceGroup, SecurityGroup
from structural.decorator.decorator import EnergySavingDecorator, SmartLightDecorator
from structural.proxy.proxy import LoggingProxy, SecurityProxy


class SmartHomeFacade:

    def __init__(self, manager: HomeManager | None = None) -> None:
        self._manager = manager if manager is not None else HomeManager.get_instance()

    def _all_devices_group(self) -> DeviceGroup:
        group = DeviceGroup(name="All Devices")
        for device in self._manager.get_all_devices():
            group.add(device)
        return group

    def turn_all_on(self) -> str:
        return self._all_devices_group().operate()

    def turn_all_off(self) -> str:
        devices = self._manager.get_all_devices()
        if not devices:
            return "No devices available"
        return "All devices turned off (simulated): " + " | ".join([f"{device.name}: OFF" for device in devices])

    def activate_security_mode(self) -> str:
        security_group = SecurityGroup()
        for device in self._manager.get_all_devices():
            if isinstance(device, (Alarm, Camera)):
                secured = SecurityProxy(real_device=LoggingProxy(device), user_role="admin")
                security_group.add(secured)
        if not security_group.get_children():
            return "No security devices configured"
        return security_group.operate()

    def run_morning_scenario(self) -> str:
        scenario = self._find_scenario_by_keyword("morning")
        scenario_text = scenario.summary() if scenario is not None else "Morning scenario not found"

        decorated_results: List[str] = []
        for device in self._manager.get_all_devices():
            candidate: Device = device
            if device.device_type() == "Light":
                candidate = SmartLightDecorator(device)
            else:
                candidate = EnergySavingDecorator(device)
            decorated_results.append(candidate.operate())

        return scenario_text + " | Executed: " + " | ".join(decorated_results)

    def _find_scenario_by_keyword(self, keyword: str) -> Scenario | None:
        lowered = keyword.lower()
        for scenario in self._manager.get_all_scenarios():
            if lowered in scenario.name.lower():
                return scenario
        return None

    def visualize(self) -> str:
        return "[Facade] SmartHomeFacade"
