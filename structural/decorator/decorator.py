from abc import ABC

from devices.device import Device


class DeviceDecorator(Device, ABC):

    def __init__(self, device: Device) -> None:
        super().__init__(name=device.name, brand=device.brand)
        self._device = device

    def device_type(self) -> str:
        return self._device.device_type()

    def operate(self) -> str:
        return self._device.operate()

    def clone(self) -> "DeviceDecorator":
        return self.__class__(self._device.clone())

    def visualize(self) -> str:
        wrapped_visual = self._device.visualize() if hasattr(self._device, "visualize") else str(self._device)
        return wrapped_visual


class SmartLightDecorator(DeviceDecorator):

    def device_type(self) -> str:
        return f"SmartLight({self._device.device_type()})"

    def operate(self) -> str:
        base_result = self._device.operate()
        return f"{base_result}; smart-light profile applied"

    def visualize(self) -> str:
        return f"{super().visualize()} [SmartLightDecorator]"


class EnergySavingDecorator(DeviceDecorator):

    def device_type(self) -> str:
        return f"EnergySaving({self._device.device_type()})"

    def operate(self) -> str:
        base_result = self._device.operate()
        return f"{base_result}; energy-saving mode enabled"

    def visualize(self) -> str:
        return f"{super().visualize()} [EnergySavingDecorator]"


class TemperatureControlDecorator(DeviceDecorator):

    def device_type(self) -> str:
        return f"TemperatureControl({self._device.device_type()})"

    def operate(self) -> str:
        base_result = self._device.operate()
        return f"{base_result}; temperature-control routine applied"

    def visualize(self) -> str:
        return f"{super().visualize()} [TemperatureControlDecorator]"
