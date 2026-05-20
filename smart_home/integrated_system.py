"""
Integrated Smart Home System using GoF patterns.
Combines all behavioral and structural patterns for a unified architecture.

- Facade: Main entry point (SmartHomeFacade)
- Command: All operations are commands via RemoteControl
- Observer: Device state changes trigger UI updates
- Strategy: Device behavior modes (night, day, energy-saving, cinema)
- Composite: Device grouping by rooms and functional groups
- Decorator: Enhanced device capabilities
- Proxy: Logging and security for operations
- Template Method: Standard routines (morning, evening, away)
- Chain of Responsibility: Event processing pipeline
- Adapter: External system integration
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from smart_home.manager import SmartHomeSystem
from smart_home.database import SmartHomeDB
from structural.facade.facade import SmartHomeFacade
from behavioral.command.invoker import RemoteControl
from behavioral.command.commands import TurnOnDeviceCommand, TurnOffDeviceCommand
from behavioral.observer.observer import Observer
from behavioral.observer.events import DeviceEvent
from behavioral.strategy.context import StrategyControlledDevice
from behavioral.strategy.concrete_strategies import NightStrategy, AutoStrategy, CustomStrategy
from structural.composite.composite import DeviceGroup
from structural.decorator.decorator import EnergySavingDecorator, SmartLightDecorator
from structural.proxy.proxy import LoggingProxy, SecurityProxy
from devices.extended_devices import SmartLight, SmartThermostat, SmartCamera, SmartDoorLock


class UIObserver(Observer):
    """Observer that notifies UI of device state changes."""

    def __init__(self, on_update: Callable[[Dict[str, Any]], None]):
        self.on_update = on_update

    def update(self, event: DeviceEvent) -> None:
        payload = {
            "event_type": event.event_type,
            "source_id": event.source.device_id if hasattr(event.source, "device_id") else str(event.source),
            "timestamp": datetime.now().isoformat(),
            "data": event.payload,
        }
        self.on_update(payload)


class IntegratedSmartHome:
    """
    Main entry point integrating all GoF patterns with database persistence.
    
    Provides:
    - Persistent device/scene storage
    - Command-based operations for UI
    - Observer pattern for UI updates
    - Strategy support for device modes
    - Composite grouping by rooms
    - Decorator for device enhancements
    - Proxy for logging/security
    """

    def __init__(self, db_path: str = "data/smarthome.db"):
        """Initialize system with database persistence."""
        self.system = SmartHomeSystem()
        self.facade = SmartHomeFacade(self.system)
        self.remote_control = RemoteControl()
        self.db = SmartHomeDB(db_path)
        
        self._device_strategies: Dict[str, StrategyControlledDevice] = {}
        self._device_groups: Dict[str, DeviceGroup] = {}
        self._ui_observers: List[UIObserver] = []
        self._room_groups: Dict[str, "RoomGroup"] = {}
        
        # Load persisted devices on startup
        self._load_persisted_devices()
    
    def _load_persisted_devices(self) -> None:
        """Load devices from database on startup."""
        try:
            devices = self.db.load_devices()
            for dev_data in devices:
                device_id = dev_data["id"]
                device_type = dev_data["type"].lower()
                
                # Skip if already exists
                if self.system.get_device(device_id):
                    continue
                
                # Recreate device
                device = self._create_device_by_type(
                    device_id, dev_data["name"], dev_data["brand"],
                    dev_data["room"], device_type, dev_data.get("metadata", {})
                )
                
                if device:
                    self.system.devices[device_id] = device
        except Exception:
            pass
    
    def _create_device_by_type(self, device_id: str, name: str, brand: str,
                              room: str, device_type: str, metadata: Dict) -> Any:
        """Create device instance based on type."""
        if device_type == "light":
            dev = SmartLight(name, brand, room, metadata.get("brightness", 100))
        elif device_type == "thermostat":
            dev = SmartThermostat(name, brand, room, metadata.get("target_temp", 21))
        elif device_type == "camera":
            dev = SmartCamera(name, brand, room, metadata.get("resolution", "1080p"))
        elif device_type == "door_lock":
            dev = SmartDoorLock(name, brand, room)
        else:
            return None
        
        dev.device_id = device_id
        return dev
    
    # =====================================================================
    # DATABASE OPERATIONS
    # =====================================================================
    
    def add_device_to_db(self, device_id: str, name: str, device_type: str,
                        brand: str = "generic", room: str = "Unassigned") -> bool:
        """Add device to system and persist to database."""
        # Create device
        device = self._create_device_by_type(device_id, name, brand, room, device_type, {})
        if not device:
            return False
        
        # Add to system
        self.system.devices[device_id] = device
        
        # Persist to database
        return self.db.save_device(device_id, name, device_type, brand, room)
    
    def remove_device_from_db(self, device_id: str) -> bool:
        """Remove device from system and database."""
        if device_id in self.system.devices:
            del self.system.devices[device_id]
        return self.db.delete_device(device_id)
    
    def get_device_history(self, device_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get device state history from database."""
        return self.db.get_device_history(device_id, hours)
    
    def export_system(self, filepath: str) -> bool:
        """Export entire system to JSON file."""
        return self.db.export_to_json(filepath)
    
    def backup_database(self) -> bool:
        """Create database backup."""
        return self.db.backup()
    
    def get_system_stats(self) -> Dict[str, int]:
        """Get system statistics from database."""
        return self.db.get_stats()

    def turn_all_devices_on(self) -> str:
        """Facade: Turn all devices on."""
        return self.facade.turn_all_on()

    def turn_all_devices_off(self) -> str:
        """Facade: Turn all devices off."""
        return self.facade.turn_all_off()

    def activate_security_mode(self) -> str:
        """Facade: Activate security mode with proxies."""
        return self.facade.activate_security_mode()

    def run_morning_scenario(self) -> str:
        """Facade: Run morning scenario with decorators."""
        return self.facade.run_morning_scenario()

    # =====================================================================
    # COMMAND-BASED OPERATIONS (for UI)
    # =====================================================================

    def execute_device_command(self, device_id: str, command_type: str) -> str:
        """
        Execute a device operation via Command pattern.
        
        Args:
            device_id: ID of the device
            command_type: "on", "off", "toggle", or custom action
        
        Returns:
            Result string
        """
        device = self.system.get_device(device_id)
        if device is None:
            return f"Device {device_id} not found"

        try:
            if command_type == "on":
                cmd = TurnOnDeviceCommand(device)
            elif command_type == "off":
                cmd = TurnOffDeviceCommand(device)
            elif command_type == "toggle":
                if hasattr(device, "status") and "on" in str(getattr(device, "status", "")).lower():
                    cmd = TurnOffDeviceCommand(device)
                else:
                    cmd = TurnOnDeviceCommand(device)
            else:
                return f"Unknown command: {command_type}"

            result = self.remote_control.press(cmd)
            self._notify_ui_observers(DeviceEvent("command_executed", device, {"cmd": command_type}))
            return result
        except Exception as e:
            return f"Command failed: {e}"

    # =====================================================================
    # STRATEGY PATTERN (Device modes)
    # =====================================================================

    def set_device_strategy(self, device_id: str, strategy_name: str, **kwargs) -> str:
        """
        Set a device behavior strategy.
        
        Args:
            device_id: ID of the device
            strategy_name: "night", "day", "auto", "custom"
            **kwargs: Additional strategy parameters
        
        Returns:
            Result string
        """
        device = self.system.get_device(device_id)
        if device is None:
            return f"Device {device_id} not found"

        if device_id not in self._device_strategies:
            self._device_strategies[device_id] = StrategyControlledDevice(device)

        strategy_obj = self._device_strategies[device_id]

        if strategy_name == "night":
            strategy_obj.set_strategy(NightStrategy())
            result = strategy_obj.operate()
        elif strategy_name == "auto":
            strategy_obj.set_strategy(AutoStrategy())
            result = strategy_obj.operate()
        elif strategy_name == "custom":
            profile = kwargs.get("profile", "custom")
            intensity = kwargs.get("intensity", 50)
            strategy_obj.set_strategy(CustomStrategy(profile_name=profile, intensity=intensity))
            result = strategy_obj.operate()
        else:
            return f"Unknown strategy: {strategy_name}"

        self._notify_ui_observers(DeviceEvent("strategy_changed", device, {"strategy": strategy_name}))
        return result

    # =====================================================================
    # COMPOSITE PATTERN (Device grouping)
    # =====================================================================

    def create_room_group(self, room_name: str) -> str:
        """Create a device group for a room."""
        if room_name in self._device_groups:
            return f"Room '{room_name}' already exists"

        group = DeviceGroup(name=room_name)
        self._device_groups[room_name] = group
        return f"Room '{room_name}' created"

    def add_device_to_room(self, device_id: str, room_name: str) -> str:
        """Add a device to a room group."""
        device = self.system.get_device(device_id)
        if device is None:
            return f"Device {device_id} not found"

        if room_name not in self._device_groups:
            self.create_room_group(room_name)

        group = self._device_groups[room_name]
        group.add(device)
        
        if hasattr(device, "room"):
            device.room = room_name

        self._notify_ui_observers(DeviceEvent("device_assigned_room", device, {"room": room_name}))
        return f"Device {device_id} added to room '{room_name}'"

    def operate_room_group(self, room_name: str) -> str:
        """Operate all devices in a room (Composite)."""
        if room_name not in self._device_groups:
            return f"Room '{room_name}' not found"

        group = self._device_groups[room_name]
        return group.operate()

    def get_room_devices(self, room_name: str) -> List[str]:
        """Get list of device IDs in a room."""
        if room_name not in self._device_groups:
            return []

        group = self._device_groups[room_name]
        devices = group.get_children()
        return [d.device_id if hasattr(d, "device_id") else str(d) for d in devices]

    # =====================================================================
    # OBSERVER PATTERN (UI updates)
    # =====================================================================

    def subscribe_to_updates(self, callback: Callable[[Dict[str, Any]], None]) -> UIObserver:
        """
        Subscribe UI to device state changes.
        
        Args:
            callback: Function to call when device state changes
        
        Returns:
            UIObserver instance for later unsubscription
        """
        observer = UIObserver(callback)
        self._ui_observers.append(observer)
        
        # Attach observer to all observable devices
        for device in self.system.get_all_devices():
            if hasattr(device, "attach"):
                device.attach(observer)

        return observer

    def unsubscribe_from_updates(self, observer: UIObserver) -> None:
        """Unsubscribe observer from updates."""
        if observer in self._ui_observers:
            self._ui_observers.remove(observer)

    def _notify_ui_observers(self, event: DeviceEvent) -> None:
        """Notify all UI observers of an event."""
        for observer in self._ui_observers:
            observer.update(event)

    # =====================================================================
    # DECORATOR PATTERN (Device enhancements)
    # =====================================================================

    def enhance_device_with_energy_saving(self, device_id: str) -> str:
        """Decorate a device with energy-saving capabilities."""
        device = self.system.get_device(device_id)
        if device is None:
            return f"Device {device_id} not found"

        enhanced = EnergySavingDecorator(device)
        # In real app, would replace device in system
        return enhanced.operate()

    def enhance_light_with_smart_features(self, device_id: str) -> str:
        """Decorate a light device with smart features."""
        device = self.system.get_device(device_id)
        if device is None or not isinstance(device, SmartLight):
            return f"Device {device_id} is not a light"

        enhanced = SmartLightDecorator(device)
        return enhanced.operate()

    # =====================================================================
    # PROXY PATTERN (Logging and security)
    # =====================================================================

    def secure_device_access(self, device_id: str, user_role: str = "admin") -> str:
        """
        Create a secure proxy for a device.
        Logs all access and checks user role.
        """
        device = self.system.get_device(device_id)
        if device is None:
            return f"Device {device_id} not found"

        logged = LoggingProxy(device)
        secured = SecurityProxy(real_device=logged, user_role=user_role)
        return secured.operate()

    # =====================================================================
    # TEMPLATE METHOD PATTERN (Standard routines)
    # =====================================================================

    def activate_routine(self, routine_name: str) -> str:
        """
        Activate a predefined routine.
        
        Args:
            routine_name: "morning", "evening", "away"
        
        Returns:
            Result string
        """
        result = self.system.activate_scene(routine_name.lower())
        self._notify_ui_observers(DeviceEvent("routine_activated", None, {"routine": routine_name}))
        return str(result)

    # =====================================================================
    # SYSTEM STATE AND STATISTICS
    # =====================================================================

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        status = self.system.get_system_status()
        status["rooms"] = len(self._device_groups)
        status["strategies_active"] = len(self._device_strategies)
        status["ui_observers"] = len(self._ui_observers)
        return status

    def get_device_list(self) -> List[Dict[str, Any]]:
        """Get list of all devices with their states."""
        devices = []
        for device in self.system.get_all_devices():
            state = device.get_state() if hasattr(device, "get_state") else {}
            device_dict = {
                "id": state.get("id", str(device)),
                "name": state.get("name", type(device).__name__),
                "type": type(device).__name__,
                "status": state.get("status", "unknown"),
                "room": state.get("room", "Unassigned"),
            }
            devices.append(device_dict)
        return devices

    # =====================================================================
    # UTILITY METHODS
    # =====================================================================

    def reset(self) -> None:
        """Reset the integrated system."""
        self.system = SmartHomeSystem()
        self.facade = SmartHomeFacade(self.system)
        self._device_strategies.clear()
        self._device_groups.clear()
        self._ui_observers.clear()
