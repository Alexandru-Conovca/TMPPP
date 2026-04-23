from typing import Optional

from behavioral.strategy.concrete_strategies import AutoStrategy
from behavioral.strategy.strategy import EnergyStrategy
from devices.device import Device


class EnergyManager:
    """Context class selecting strategy dynamically."""

    def __init__(self, strategy: Optional[EnergyStrategy] = None) -> None:
        self._strategy = strategy if strategy is not None else AutoStrategy()

    def set_strategy(self, strategy: EnergyStrategy) -> None:
        self._strategy = strategy

    def execute(self, device: Device) -> str:
        return self._strategy.execute(device)

    def describe(self) -> str:
        return "EnergyManager strategy: " + self._strategy.strategy_name()


class StrategyControlledDevice(Device):
    """Device-compatible context wrapper for Strategy pattern."""

    def __init__(self, wrapped_device: Device, strategy: Optional[EnergyStrategy] = None) -> None:
        super().__init__(name=wrapped_device.name, brand=wrapped_device.brand)
        self._wrapped_device = wrapped_device
        self._manager = EnergyManager(strategy)

    def set_strategy(self, strategy: EnergyStrategy) -> None:
        self._manager.set_strategy(strategy)

    def device_type(self) -> str:
        return "StrategyControlled(" + self._wrapped_device.device_type() + ")"

    def operate(self) -> str:
        return self._manager.execute(self._wrapped_device)

    def clone(self) -> "StrategyControlledDevice":
        cloned_wrapped = self._wrapped_device.clone()
        return StrategyControlledDevice(cloned_wrapped)

    def visualize(self) -> str:
        wrapped_visual = self._wrapped_device.visualize() if hasattr(self._wrapped_device, "visualize") else str(self)
        return wrapped_visual + " [StrategyControlledDevice]"
