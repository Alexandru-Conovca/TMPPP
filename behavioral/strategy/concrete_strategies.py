from devices.device import Device
from behavioral.strategy.strategy import EnergyStrategy


class AutoStrategy(EnergyStrategy):

    def execute(self, device: Device) -> str:
        return "[AutoStrategy] " + device.operate()

    def strategy_name(self) -> str:
        return "Auto"

    def clone(self) -> "AutoStrategy":
        return AutoStrategy()


class NightStrategy(EnergyStrategy):

    def execute(self, device: Device) -> str:
        return "[NightStrategy] low-power mode; " + device.operate()

    def strategy_name(self) -> str:
        return "Night"

    def clone(self) -> "NightStrategy":
        return NightStrategy()


class CustomStrategy(EnergyStrategy):

    def __init__(self, profile_name: str, intensity: int) -> None:
        self.profile_name = profile_name
        self.intensity = intensity

    def execute(self, device: Device) -> str:
        return (
            "[CustomStrategy "
            + self.profile_name
            + "] intensity "
            + str(self.intensity)
            + "; "
            + device.operate()
        )

    def strategy_name(self) -> str:
        return "Custom(" + self.profile_name + ")"

    def clone(self) -> "CustomStrategy":
        return CustomStrategy(profile_name=self.profile_name, intensity=self.intensity)
