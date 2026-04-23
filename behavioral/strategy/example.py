from behavioral.strategy.concrete_strategies import AutoStrategy, NightStrategy
from behavioral.strategy.context import StrategyControlledDevice
from devices.device import Light


def run_example() -> str:
    controlled = StrategyControlledDevice(Light(name="Bedroom Light", brand="Philips"), AutoStrategy())
    first = controlled.operate()
    controlled.set_strategy(NightStrategy())
    second = controlled.operate()
    return first + "\n" + second


if __name__ == "__main__":
    print(run_example())
