from typing import List, Optional

from behavioral.observer.events import DeviceEvent
from behavioral.observer.observer import Observer
from behavioral.chain.handler import Handler


class NotificationService(Observer):
    """Concrete observer that stores user-facing notifications."""

    def __init__(self) -> None:
        self._messages: List[str] = []

    def update(self, event: DeviceEvent) -> None:
        self._messages.append("Notification: " + event.describe())

    def get_messages(self) -> List[str]:
        return list(self._messages)


class EventLogger(Observer):
    """Concrete observer that stores technical logs."""

    def __init__(self) -> None:
        self._logs: List[str] = []

    def update(self, event: DeviceEvent) -> None:
        self._logs.append("Log: " + event.describe())

    def get_logs(self) -> List[str]:
        return list(self._logs)


class ChainEventObserver(Observer):
    """Observer that forwards events into Chain of Responsibility."""

    def __init__(self, first_handler: Optional[Handler] = None) -> None:
        self._first_handler = first_handler
        self._results: List[str] = []

    def set_first_handler(self, handler: Handler) -> None:
        self._first_handler = handler

    def update(self, event: DeviceEvent) -> None:
        if self._first_handler is None:
            self._results.append("Chain not configured: " + event.describe())
            return
        result = self._first_handler.handle(event)
        self._results.append(result)

    def get_results(self) -> List[str]:
        return list(self._results)
