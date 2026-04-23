from behavioral.observer.concrete_observers import EventLogger, NotificationService
from behavioral.observer.observable_devices import ObservableCamera, ObservableThermostat


def run_example() -> str:
    camera = ObservableCamera(name="Garage Camera", brand="Samsung")
    thermostat = ObservableThermostat(name="Kitchen Thermostat", brand="Xiaomi")

    notification = NotificationService()
    logger = EventLogger()

    camera.attach(notification)
    camera.attach(logger)
    thermostat.attach(notification)

    camera.operate()
    thermostat.operate()

    return "\n".join(notification.get_messages() + logger.get_logs())


if __name__ == "__main__":
    print(run_example())
