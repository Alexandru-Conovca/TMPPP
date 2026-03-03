# TMPPP — учебная «Система умного дома»

Проект демонстрирует классические паттерны GoF на Python (в стиле Java) без сторонних библиотек:

- Factory Method — создание конкретных устройств через `DeviceCreator`.
- Abstract Factory — брендовые фабрики `XiaomiFactory`, `PhilipsFactory`, `SamsungFactory`.
- Singleton — `HomeManager` хранит состояние дома.
- Builder — конструктор сценариев автоматизации через `ScenarioDirector` и `ScenarioBuilder`.
- Prototype — клонирование устройств и сценариев методом `clone()`.

## Структура
- `devices/` — абстрактный `Device`, конкретные устройства и создатели.
- `factories/` — абстрактная фабрика брендов и реализации.
- `manager/` — Singleton `HomeManager`.
- `scenarios/` — Builder и сценарии (также Prototype).
- `main.py` — консольное меню для демонстрации.

## Запуск

```bash
python main.py
```

В меню можно выбирать бренд, создавать устройства, добавлять их в менеджер, собирать сценарии, клонировать экземпляры и выводить состояние дома.
