from abc import ABC, abstractmethod
from typing import Optional

from behavioral.observer.events import DeviceEvent


class Handler(ABC):

    def __init__(self) -> None:
        self._next_handler: Optional["Handler"] = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next_handler = handler
        return handler

    def handle(self, event: DeviceEvent) -> str:
        handled = self._process(event)
        if handled is not None:
            return handled
        if self._next_handler is not None:
            return self._next_handler.handle(event)
        return "Unhandled event: " + event.describe()

    @abstractmethod
    def _process(self, event: DeviceEvent) -> Optional[str]:
        pass
