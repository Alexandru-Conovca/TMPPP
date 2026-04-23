from devices.device import Device


class DeviceEvent:
    """Event object used by Observer and Chain of Responsibility."""

    def __init__(self, event_type: str, source: Device, payload: str) -> None:
        self.event_type = event_type
        self.source = source
        self.payload = payload

    def describe(self) -> str:
        return f"[{self.event_type}] {self.source.name}: {self.payload}"
