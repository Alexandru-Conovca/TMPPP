from typing import Optional

from behavioral.chain.handler import Handler
from behavioral.observer.events import DeviceEvent


class MotionHandler(Handler):

    def _process(self, event: DeviceEvent) -> Optional[str]:
        if event.event_type != "motion":
            return None
        return "MotionHandler processed: " + event.describe()


class TemperatureHandler(Handler):

    def _process(self, event: DeviceEvent) -> Optional[str]:
        if event.event_type != "temperature":
            return None
        return "TemperatureHandler processed: " + event.describe()


class SecurityHandler(Handler):

    def _process(self, event: DeviceEvent) -> Optional[str]:
        if event.event_type not in ["door", "motion"]:
            return None
        return "SecurityHandler processed: " + event.describe()
