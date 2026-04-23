from behavioral.command.command import Command
from behavioral.observer.events import DeviceEvent
from behavioral.observer.observer import Observer
from devices.device import Device


class TurnOnDeviceCommand(Command):

    def __init__(self, receiver: Device) -> None:
        self._receiver = receiver

    def execute(self) -> str:
        return self._receiver.operate()

    def undo(self) -> str:
        if hasattr(self._receiver, "is_on"):
            self._receiver.is_on = False
            if hasattr(self._receiver, "brightness"):
                self._receiver.brightness = 0
            return self._receiver.name + " switched off"
        if hasattr(self._receiver, "recording"):
            self._receiver.recording = False
            return self._receiver.name + " recording stopped"
        if hasattr(self._receiver, "armed"):
            self._receiver.armed = False
            return self._receiver.name + " disarmed"
        return "Undo fallback: no explicit OFF state for " + self._receiver.name


class TurnOffDeviceCommand(Command):

    def __init__(self, receiver: Device) -> None:
        self._receiver = receiver

    def execute(self) -> str:
        if hasattr(self._receiver, "is_on"):
            self._receiver.is_on = False
            if hasattr(self._receiver, "brightness"):
                self._receiver.brightness = 0
            return self._receiver.name + " switched off"
        if hasattr(self._receiver, "recording"):
            self._receiver.recording = False
            return self._receiver.name + " recording stopped"
        if hasattr(self._receiver, "armed"):
            self._receiver.armed = False
            return self._receiver.name + " disarmed"
        return "TurnOff fallback: no explicit OFF state for " + self._receiver.name


class NotifyCommand(Command):

    def __init__(self, observer: Observer, event: DeviceEvent) -> None:
        self._observer = observer
        self._event = event

    def execute(self) -> str:
        self._observer.update(self._event)
        return "NotifyCommand executed: " + self._event.describe()
