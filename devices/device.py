"""
Device hierarchy and Factory Method pattern implementations.
- Device: abstract product
- Concrete devices: Light, Thermostat, Camera, Alarm
- DeviceCreator: abstract creator
- Concrete creators: LightCreator, ThermostatCreator, CameraCreator, AlarmCreator
"""
from abc import ABC, abstractmethod


class Device(ABC):
    """Abstract product for any smart home device."""

    def __init__(self, name: str, brand: str) -> None:
        self.name = name
        self.brand = brand

    @abstractmethod
    def device_type(self) -> str:
        """Return device type name."""

    @abstractmethod
    def operate(self) -> str:
        """Simulate device operation for visualization."""

    @abstractmethod
    def clone(self) -> "Device":
        """Prototype: return a deep manual copy of the device."""

    def __str__(self) -> str:
        return f"{self.device_type()} '{self.name}' ({self.brand})"


class Light(Device):
    def __init__(self, name: str, brand: str, brightness: int = 0, is_on: bool = False) -> None:
        super().__init__(name, brand)
        self.brightness = brightness
        self.is_on = is_on

    def device_type(self) -> str:
        return "Light"

    def operate(self) -> str:
        self.is_on = not self.is_on
        self.brightness = 70 if self.is_on else 0
        return f"Light toggled {'on' if self.is_on else 'off'}, brightness {self.brightness}%"

    def clone(self) -> "Light":
        return Light(name=f"{self.name} (clone)", brand=self.brand, brightness=self.brightness, is_on=self.is_on)


class Thermostat(Device):
    def __init__(self, name: str, brand: str, temperature: float = 22.0) -> None:
        super().__init__(name, brand)
        self.temperature = temperature

    def device_type(self) -> str:
        return "Thermostat"

    def operate(self) -> str:
        self.temperature += 0.5
        return f"Thermostat adjusted to {self.temperature:.1f}C"

    def clone(self) -> "Thermostat":
        return Thermostat(name=f"{self.name} (clone)", brand=self.brand, temperature=self.temperature)


class Camera(Device):
    def __init__(self, name: str, brand: str, recording: bool = False) -> None:
        super().__init__(name, brand)
        self.recording = recording

    def device_type(self) -> str:
        return "Camera"

    def operate(self) -> str:
        self.recording = not self.recording
        return f"Camera recording {'started' if self.recording else 'stopped'}"

    def clone(self) -> "Camera":
        return Camera(name=f"{self.name} (clone)", brand=self.brand, recording=self.recording)


class Alarm(Device):
    def __init__(self, name: str, brand: str, armed: bool = False) -> None:
        super().__init__(name, brand)
        self.armed = armed

    def device_type(self) -> str:
        return "Alarm"

    def operate(self) -> str:
        self.armed = not self.armed
        return f"Alarm {'armed' if self.armed else 'disarmed'}"

    def clone(self) -> "Alarm":
        return Alarm(name=f"{self.name} (clone)", brand=self.brand, armed=self.armed)


class DeviceCreator(ABC):
    """Abstract creator declaring Factory Method."""

    @abstractmethod
    def create_device(self, name: str, brand: str) -> Device:
        """Factory Method that creates concrete devices."""


class LightCreator(DeviceCreator):
    def create_device(self, name: str, brand: str) -> Device:
        return Light(name=name, brand=brand)


class ThermostatCreator(DeviceCreator):
    def create_device(self, name: str, brand: str) -> Device:
        return Thermostat(name=name, brand=brand)


class CameraCreator(DeviceCreator):
    def create_device(self, name: str, brand: str) -> Device:
        return Camera(name=name, brand=brand)


class AlarmCreator(DeviceCreator):
    def create_device(self, name: str, brand: str) -> Device:
        return Alarm(name=name, brand=brand)
