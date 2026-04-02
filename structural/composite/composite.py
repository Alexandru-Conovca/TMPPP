from abc import ABC, abstractmethod
from typing import List

from devices.device import Device


class DeviceComponent(Device, ABC):

    @abstractmethod
    def add(self, device: Device) -> None:
        pass

    @abstractmethod
    def remove(self, device: Device) -> None:
        pass

    @abstractmethod
    def get_children(self) -> List[Device]:
        pass


class DeviceGroup(DeviceComponent):

    def __init__(self, name: str = "Device Group", brand: str = "Group") -> None:
        super().__init__(name=name, brand=brand)
        self._children: List[Device] = []

    def device_type(self) -> str:
        return "DeviceGroup"

    def add(self, device: Device) -> None:
        self._children.append(device)

    def remove(self, device: Device) -> None:
        self._children.remove(device)

    def get_children(self) -> List[Device]:
        return list(self._children)

    def operate(self) -> str:
        if not self._children:
            return f"Group '{self.name}' has no devices"
        results = [child.operate() for child in self._children]
        return f"Group '{self.name}' executed: " + " | ".join(results)

    def clone(self) -> "DeviceGroup":
        cloned_group = self.__class__(name=f"{self.name} (clone)", brand=self.brand)
        for child in self._children:
            cloned_group.add(child.clone())
        return cloned_group

    def visualize(self) -> str:
        return f"[Composite] {self.device_type()} '{self.name}' with {len(self._children)} item(s)"


class FloorGroup(DeviceGroup):

    def __init__(self, floor_number: int, brand: str = "Group") -> None:
        self.floor_number = floor_number
        super().__init__(name=f"Floor {floor_number}", brand=brand)

    def device_type(self) -> str:
        return "FloorGroup"

    def clone(self) -> "FloorGroup":
        cloned_group = FloorGroup(floor_number=self.floor_number, brand=self.brand)
        cloned_group.name = f"{self.name} (clone)"
        for child in self._children:
            cloned_group.add(child.clone())
        return cloned_group


class SecurityGroup(DeviceGroup):

    def __init__(self, name: str = "Security Group", brand: str = "Group") -> None:
        super().__init__(name=name, brand=brand)

    def device_type(self) -> str:
        return "SecurityGroup"
