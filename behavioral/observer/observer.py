from abc import ABC, abstractmethod
from behavioral.observer.events import DeviceEvent


class Observer(ABC):

    @abstractmethod
    def update(self, event: DeviceEvent) -> None:
        pass
