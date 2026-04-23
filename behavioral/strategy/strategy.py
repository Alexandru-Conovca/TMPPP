from abc import ABC, abstractmethod

from devices.device import Device


class EnergyStrategy(ABC):
    """Strategy interface for device energy behavior."""

    @abstractmethod
    def execute(self, device: Device) -> str:
        pass

    @abstractmethod
    def strategy_name(self) -> str:
        pass

    @abstractmethod
    def clone(self) -> "EnergyStrategy":
        pass
