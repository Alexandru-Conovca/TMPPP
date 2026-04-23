from behavioral.chain.handlers import MotionHandler, SecurityHandler, TemperatureHandler
from behavioral.observer.events import DeviceEvent
from devices.device import Camera, Thermostat


def run_example() -> str:
    motion = MotionHandler()
    temperature = TemperatureHandler()
    security = SecurityHandler()
    motion.set_next(temperature).set_next(security)

    camera_event = DeviceEvent("motion", Camera(name="Hall Camera", brand="Samsung"), "movement")
    temp_event = DeviceEvent("temperature", Thermostat(name="Hall Thermostat", brand="Xiaomi"), "new value 23.0C")

    return "\n".join([motion.handle(camera_event), motion.handle(temp_event)])


if __name__ == "__main__":
    print(run_example())
