from behavioral.command.commands import TurnOffDeviceCommand, TurnOnDeviceCommand
from behavioral.command.invoker import RemoteControl
from devices.device import Light


def run_example() -> str:
    light = Light(name="Office Light", brand="Xiaomi")
    remote = RemoteControl()

    on_result = remote.press(TurnOnDeviceCommand(light))
    off_result = remote.press(TurnOffDeviceCommand(light))
    undo_result = remote.undo_last()

    return "\n".join([on_result, off_result, undo_result])


if __name__ == "__main__":
    print(run_example())
