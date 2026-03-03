"""
Abstract Factory pattern for brand-specific device families.
- SmartHomeFactory: abstract factory
- XiaomiFactory, PhilipsFactory, SamsungFactory: concrete factories producing full device families
"""
from abc import ABC, abstractmethod
from devices.device import Device, LightCreator, ThermostatCreator, CameraCreator, AlarmCreator


class SmartHomeFactory(ABC):
    """Abstract factory declaring creation of each family member."""

    @abstractmethod
    def create_light(self, name: str) -> Device:
        pass

    @abstractmethod
    def create_thermostat(self, name: str) -> Device:
        pass

    @abstractmethod
    def create_camera(self, name: str) -> Device:
        pass

    @abstractmethod
    def create_alarm(self, name: str) -> Device:
        pass

    @abstractmethod
    def brand_name(self) -> str:
        pass


class BaseBrandFactory(SmartHomeFactory):
    """Shared helper storing concrete creators to stress Factory Method usage."""

    def __init__(self, brand: str) -> None:
        self._brand = brand
        self._light_creator = LightCreator()
        self._thermostat_creator = ThermostatCreator()
        self._camera_creator = CameraCreator()
        self._alarm_creator = AlarmCreator()

    def brand_name(self) -> str:
        return self._brand

    def create_light(self, name: str) -> Device:
        return self._light_creator.create_device(name, self._brand)

    def create_thermostat(self, name: str) -> Device:
        return self._thermostat_creator.create_device(name, self._brand)

    def create_camera(self, name: str) -> Device:
        return self._camera_creator.create_device(name, self._brand)

    def create_alarm(self, name: str) -> Device:
        return self._alarm_creator.create_device(name, self._brand)


class XiaomiFactory(BaseBrandFactory):
    def __init__(self) -> None:
        super().__init__(brand="Xiaomi")


class PhilipsFactory(BaseBrandFactory):
    def __init__(self) -> None:
        super().__init__(brand="Philips")


class SamsungFactory(BaseBrandFactory):
    def __init__(self) -> None:
        super().__init__(brand="Samsung")
