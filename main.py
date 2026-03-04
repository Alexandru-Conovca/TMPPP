from typing import List, Optional
from factories.smart_home_factory import SmartHomeFactory, XiaomiFactory, PhilipsFactory, SamsungFactory
from devices.device import Device
from manager.home_manager import HomeManager
from scenarios.builder import StandardScenarioBuilder, ScenarioDirector


def choose_brand() -> SmartHomeFactory:
    print("Выберите бренд:")
    print("1. Xiaomi")
    print("2. Philips")
    print("3. Samsung")
    choice = input("Ваш выбор: ")
    if choice == "2":
        return PhilipsFactory()
    if choice == "3":
        return SamsungFactory()
    return XiaomiFactory()


def create_device(factory: SmartHomeFactory) -> Optional[Device]:
    print(f"Текущий бренд: {factory.brand_name()}")
    print("Выберите тип устройства:")
    print("1. Light")
    print("2. Thermostat")
    print("3. Camera")
    print("4. Alarm")
    choice = input("Ваш выбор: ")
    name = input("Имя устройства: ")
    if choice == "1":
        return factory.create_light(name)
    if choice == "2":
        return factory.create_thermostat(name)
    if choice == "3":
        return factory.create_camera(name)
    if choice == "4":
        return factory.create_alarm(name)
    print("Неизвестный тип устройства")
    return None


def select_from_list(items: List, title: str):
    if not items:
        print("Список пуст")
        return None
    print(title)
    for idx, item in enumerate(items, start=1):
        print(f"{idx}. {item}")
    choice = input("Введите номер: ")
    if not choice.isdigit():
        print("Нужно ввести номер")
        return None
    index = int(choice) - 1
    if index < 0 or index >= len(items):
        print("Неверный номер")
        return None
    return items[index]


def create_scenario(director: ScenarioDirector):
    print("Выберите сценарий:")
    print("1. Morning")
    print("2. Evening")
    print("3. Away")
    choice = input("Ваш выбор: ")
    if choice == "1":
        return director.create_morning()
    if choice == "2":
        return director.create_evening()
    if choice == "3":
        return director.create_away()
    print("Неизвестный сценарий")
    return None


def main() -> None:
    manager = HomeManager.get_instance()
    current_factory: SmartHomeFactory = XiaomiFactory()
    created_devices: List[Device] = []
    builder = StandardScenarioBuilder()
    director = ScenarioDirector(builder)

    while True:
        print("\nМеню:")
        print("1. Создать устройство")
        print("2. Выбрать бренд")
        print("3. Добавить устройство в менеджер")
        print("4. Создать сценарий")
        print("5. Клонировать устройство или сценарий")
        print("6. Показать состояние дома")
        print("0. Выход")
        choice = input("Ваш выбор: ")

        if choice == "1":
            device = create_device(current_factory)
            if device:
                created_devices.append(device)
                print(f"Создано: {device}")
        elif choice == "2":
            current_factory = choose_brand()
            print(f"Выбран бренд: {current_factory.brand_name()}")
        elif choice == "3":
            device = select_from_list(created_devices, "Выберите устройство для добавления")
            if device:
                manager.add_device(device)
                print(f"Добавлено в менеджер: {device}")
        elif choice == "4":
            scenario = create_scenario(director)
            if scenario:
                manager.add_scenario(scenario)
                print(scenario.summary())
        elif choice == "5":
            print("1. Клонировать устройство")
            print("2. Клонировать сценарий")
            sub_choice = input("Ваш выбор: ")
            if sub_choice == "1":
                device = select_from_list(manager.devices, "Выберите устройство для клонирования")
                if device:
                    cloned_device = device.clone()
                    manager.add_device(cloned_device)
                    print(f"Клон добавлен: {cloned_device}")
            elif sub_choice == "2":
                scenario = select_from_list(manager.scenarios, "Выберите сценарий для клонирования")
                if scenario:
                    cloned_scenario = scenario.clone()
                    manager.add_scenario(cloned_scenario)
                    print(cloned_scenario.summary())
            else:
                print("Неизвестный тип клонирования")
        elif choice == "6":
            print(manager.describe())
        elif choice == "0":
            print("Выход")
            break
        else:
            print("Неизвестная команда")


if __name__ == "__main__":
    main()
