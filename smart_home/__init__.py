"""
Smart Home System - Main Package

Comprehensive package for smart home management including:
- Device management (extended_devices.py)
- Automation and scheduling (automation.py)
- Remote access and monitoring (remote_access.py)
- Central management (manager.py)
"""

from smart_home.manager import SmartHomeSystem
from smart_home.automation import (
    NotificationManager, ScheduleManager, AutomationManager, SceneManager
)
from smart_home.remote_access import RemoteAccessManager, SystemMonitor, APIGateway

__all__ = [
    "SmartHomeSystem",
    "NotificationManager",
    "ScheduleManager",
    "AutomationManager",
    "SceneManager",
    "RemoteAccessManager",
    "SystemMonitor",
    "APIGateway"
]
