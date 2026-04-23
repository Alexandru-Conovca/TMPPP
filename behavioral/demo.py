"""Demonstration of behavioral GoF patterns integrated with Smart Home system."""
from typing import List

from behavioral.chain.handlers import MotionHandler, SecurityHandler, TemperatureHandler
from behavioral.command.commands import NotifyCommand, TurnOnDeviceCommand
from behavioral.command.invoker import RemoteControl
from behavioral.observer.concrete_observers import ChainEventObserver, EventLogger, NotificationService
from behavioral.observer.events import DeviceEvent
from behavioral.observer.observable_devices import DoorSensor, ObservableCamera, ObservableThermostat
from behavioral.strategy.concrete_strategies import CustomStrategy, NightStrategy
from behavioral.strategy.context import StrategyControlledDevice
from behavioral.template.routines import AwayRoutine, EveningRoutine, MorningRoutine
from devices.device import Light
from manager.home_manager import HomeManager


def run_behavioral_demo() -> str:
    manager = HomeManager.get_instance()

    camera = ObservableCamera(name="Entry Camera", brand="Samsung")
    thermostat = ObservableThermostat(name="Hall Thermostat", brand="Xiaomi")
    door = DoorSensor(name="Front Door", brand="Philips")

    manager.add_device(camera)
    manager.add_device(thermostat)
    manager.add_device(door)

    notification = NotificationService()
    logger = EventLogger()

    motion_handler = MotionHandler()
    temperature_handler = TemperatureHandler()
    security_handler = SecurityHandler()
    motion_handler.set_next(temperature_handler).set_next(security_handler)
    chain_observer = ChainEventObserver(first_handler=motion_handler)

    camera.attach(notification)
    camera.attach(logger)
    camera.attach(chain_observer)
    thermostat.attach(notification)
    thermostat.attach(chain_observer)
    door.attach(notification)
    door.attach(chain_observer)

    observer_results: List[str] = [camera.operate(), thermostat.operate(), door.open_door()]

    strategic_light = StrategyControlledDevice(Light(name="Living Light", brand="Xiaomi"))
    strategic_light.set_strategy(NightStrategy())
    strategy_result_1 = strategic_light.operate()
    strategic_light.set_strategy(CustomStrategy(profile_name="Cinema", intensity=35))
    strategy_result_2 = strategic_light.operate()

    remote = RemoteControl()
    command_results: List[str] = [remote.press(TurnOnDeviceCommand(strategic_light))]
    synthetic_event = DeviceEvent(event_type="motion", source=camera, payload="manual command notification")
    command_results.append(remote.press(NotifyCommand(notification, synthetic_event)))

    template_results = [MorningRoutine().run(), EveningRoutine().run(), AwayRoutine().run()]

    lines = [
        "=== Observer + Chain ===",
        *observer_results,
        *chain_observer.get_results(),
        "=== Strategy ===",
        strategy_result_1,
        strategy_result_2,
        "=== Command ===",
        *command_results,
        "=== Template Method ===",
        *template_results,
        "=== Notifications ===",
        *notification.get_messages(),
        "=== Logs ===",
        *logger.get_logs(),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(run_behavioral_demo())
