from typing import List

from behavioral.observer.events import DeviceEvent
from behavioral.observer.observer import Observer
from behavioral.observer.subject import Subject
from devices.device import Camera, Device, Thermostat


class ObservableDeviceSubject(Subject):
    """Reusable Subject implementation for observable devices."""

    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: DeviceEvent) -> None:
        for observer in self._observers:
            observer.update(event)


class ObservableCamera(Camera, ObservableDeviceSubject):
    """Camera as ConcreteSubject: notifies when motion is detected."""

    def __init__(self, name: str, brand: str, recording: bool = False) -> None:
        Camera.__init__(self, name=name, brand=brand, recording=recording)
        ObservableDeviceSubject.__init__(self)

    def detect_motion(self, details: str = "motion detected") -> str:
        event = DeviceEvent(event_type="motion", source=self, payload=details)
        self.notify(event)
        return event.describe()

    def operate(self) -> str:
        base_result = super().operate()
        motion_result = self.detect_motion("movement near camera zone")
        return base_result + " | " + motion_result

    def clone(self) -> "ObservableCamera":
        return ObservableCamera(name=f"{self.name} (clone)", brand=self.brand, recording=self.recording)


class ObservableThermostat(Thermostat, ObservableDeviceSubject):
    """Thermostat as ConcreteSubject: notifies when temperature changes."""

    def __init__(self, name: str, brand: str, temperature: float = 22.0) -> None:
        Thermostat.__init__(self, name=name, brand=brand, temperature=temperature)
        ObservableDeviceSubject.__init__(self)

    def set_temperature(self, value: float) -> str:
        self.temperature = value
        event = DeviceEvent(event_type="temperature", source=self, payload=f"new value {value:.1f}C")
        self.notify(event)
        return event.describe()

    def operate(self) -> str:
        base_result = super().operate()
        temp_event = DeviceEvent(
            event_type="temperature",
            source=self,
            payload=f"adjusted to {self.temperature:.1f}C",
        )
        self.notify(temp_event)
        return base_result + " | " + temp_event.describe()

    def clone(self) -> "ObservableThermostat":
        return ObservableThermostat(name=f"{self.name} (clone)", brand=self.brand, temperature=self.temperature)


class DoorSensor(Device, ObservableDeviceSubject):
    """Simple observable door sensor for security events."""

    def __init__(self, name: str, brand: str, opened: bool = False) -> None:
        Device.__init__(self, name=name, brand=brand)
        ObservableDeviceSubject.__init__(self)
        self.opened = opened

    def device_type(self) -> str:
        return "DoorSensor"

    def open_door(self) -> str:
        self.opened = True
        event = DeviceEvent(event_type="door", source=self, payload="door opened")
        self.notify(event)
        return event.describe()

    def operate(self) -> str:
        if self.opened:
            self.opened = False
            event = DeviceEvent(event_type="door", source=self, payload="door closed")
        else:
            self.opened = True
            event = DeviceEvent(event_type="door", source=self, payload="door opened")
        self.notify(event)
        return event.describe()

    def clone(self) -> "DoorSensor":
        return DoorSensor(name=f"{self.name} (clone)", brand=self.brand, opened=self.opened)
