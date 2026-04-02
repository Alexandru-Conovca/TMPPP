"""Decorator pattern package for smart home devices."""

from .decorator import (
    DeviceDecorator,
    SmartLightDecorator,
    EnergySavingDecorator,
    TemperatureControlDecorator,
)

__all__ = [
    "DeviceDecorator",
    "SmartLightDecorator",
    "EnergySavingDecorator",
    "TemperatureControlDecorator",
]
