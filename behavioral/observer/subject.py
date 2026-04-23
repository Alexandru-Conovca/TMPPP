from abc import ABC, abstractmethod
from behavioral.observer.observer import Observer
from behavioral.observer.events import DeviceEvent


class Subject(ABC):

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self, event: DeviceEvent) -> None:
        pass
