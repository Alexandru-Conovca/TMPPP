"""
Comprehensive Smart Home Manager - Integration point for entire system.

Integrates:
- Extended devices (lights, climate, appliances, sensors, cameras, etc.)
- Notifications and alerts
- Scheduling and automation
- Remote access and monitoring
- Scene management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, time
from enum import Enum
from devices.extended_devices import (
    SmartLight, SmartThermostat, SmartAC, SmartVentilation,
    SmartAppliance, SmartCamera, SmartDoorLock, SmartSensor,
    SmartSpeaker, SmartTV, EnergyMonitor, SensorType
)
from smart_home.automation import (
    NotificationManager, NotificationType, NotificationChannel,
    ScheduleManager, ScheduleType, AutomationManager, SceneManager
)
from smart_home.remote_access import (
    RemoteAccessManager, SystemMonitor, APIGateway
)


class SmartHomeSystem:
    """
    Central management system for entire smart home.
    
    Manages:
    - All device types (lights, climate, appliances, sensors, etc.)
    - Notifications and alerts
    - Schedules and automation
    - Remote access and monitoring
    - Scenes and scenarios
    - Energy consumption
    """
    
    def __init__(self):
        """Initialize smart home system."""
        # Core components
        self.name = "Smart Home System"
        self.created_at = datetime.now()
        
        # Device storage
        self.devices: Dict[str, Any] = {}
        self.device_counter = 0
        
        # Subsystems
        self.notification_manager = NotificationManager()
        self.schedule_manager = ScheduleManager(self.notification_manager)
        self.automation_manager = AutomationManager(self.notification_manager)
        self.scene_manager = SceneManager()
        self.access_manager = RemoteAccessManager()
        self.monitor = SystemMonitor()
        self.api_gateway = APIGateway(self.access_manager, self.monitor)
        
        # Energy management
        self.energy_monitor = EnergyMonitor("Main Energy Monitor")
        
    # ========================================================================
    # DEVICE MANAGEMENT
    # ========================================================================
    
    def add_light(self, name: str, brand: str, room: str, brightness: int = 100) -> SmartLight:
        """Add smart light."""
        light = SmartLight(name, brand, room, brightness)
        device_id = f"light_{self._get_next_device_id()}"
        self.devices[device_id] = light
        self.monitor.register_device(device_id, name)
        
        self.notification_manager.notify(
            title="Device Added",
            message=f"Smart light '{name}' added to {room}",
            notification_type=NotificationType.INFO
        )
        return light
    
    def add_thermostat(self, name: str, brand: str, room: str, target_temp: float = 21) -> SmartThermostat:
        """Add smart thermostat."""
        thermostat = SmartThermostat(name, brand, room, target_temp)
        device_id = f"thermostat_{self._get_next_device_id()}"
        self.devices[device_id] = thermostat
        self.monitor.register_device(device_id, name)
        return thermostat
    
    def add_ac(self, name: str, brand: str, room: str) -> SmartAC:
        """Add smart AC unit."""
        ac = SmartAC(name, brand, room)
        device_id = f"ac_{self._get_next_device_id()}"
        self.devices[device_id] = ac
        self.monitor.register_device(device_id, name)
        return ac
    
    def add_ventilation(self, name: str, brand: str, room: str) -> SmartVentilation:
        """Add smart ventilation."""
        vent = SmartVentilation(name, brand, room)
        device_id = f"ventilation_{self._get_next_device_id()}"
        self.devices[device_id] = vent
        self.monitor.register_device(device_id, name)
        return vent
    
    def add_appliance(self, name: str, brand: str, appliance_type: str) -> SmartAppliance:
        """Add smart appliance."""
        appliance = SmartAppliance(name, brand, appliance_type)
        device_id = f"appliance_{self._get_next_device_id()}"
        self.devices[device_id] = appliance
        self.monitor.register_device(device_id, name)
        return appliance
    
    def add_camera(self, name: str, brand: str, location: str, resolution: str = "1080p") -> SmartCamera:
        """Add smart camera."""
        camera = SmartCamera(name, brand, location, resolution)
        device_id = f"camera_{self._get_next_device_id()}"
        self.devices[device_id] = camera
        self.monitor.register_device(device_id, name)
        return camera
    
    def add_door_lock(self, name: str, brand: str, location: str) -> SmartDoorLock:
        """Add smart door lock."""
        lock = SmartDoorLock(name, brand, location)
        device_id = f"lock_{self._get_next_device_id()}"
        self.devices[device_id] = lock
        self.monitor.register_device(device_id, name)
        return lock
    
    def add_sensor(self, name: str, brand: str, sensor_type: SensorType, location: str) -> SmartSensor:
        """Add smart sensor."""
        sensor = SmartSensor(name, brand, sensor_type, location)
        device_id = f"sensor_{self._get_next_device_id()}"
        self.devices[device_id] = sensor
        self.monitor.register_device(device_id, name)
        return sensor
    
    def add_speaker(self, name: str, brand: str, room: str) -> SmartSpeaker:
        """Add smart speaker."""
        speaker = SmartSpeaker(name, brand, room)
        device_id = f"speaker_{self._get_next_device_id()}"
        self.devices[device_id] = speaker
        self.monitor.register_device(device_id, name)
        return speaker
    
    def add_tv(self, name: str, brand: str, room: str, screen_size: int = 55) -> SmartTV:
        """Add smart TV."""
        tv = SmartTV(name, brand, room, screen_size)
        device_id = f"tv_{self._get_next_device_id()}"
        self.devices[device_id] = tv
        self.monitor.register_device(device_id, name)
        return tv
    
    def _get_next_device_id(self) -> int:
        """Get next device ID."""
        self.device_counter += 1
        return self.device_counter
    
    def get_device(self, device_id: str) -> Optional[Any]:
        """Get device by ID."""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all devices with state."""
        devices = []
        for device_id, device in self.devices.items():
            if hasattr(device, 'get_state'):
                state = device.get_state()
                state['device_id'] = device_id
                devices.append(state)
        return devices
    
    def get_devices_by_type(self, device_type: str) -> List[Dict[str, Any]]:
        """Get devices by type (light, thermostat, etc.)."""
        return [d for d in self.get_all_devices() if device_type in d.get('device_id', '')]
    
    def get_devices_by_room(self, room: str) -> List[Dict[str, Any]]:
        """Get devices in specific room."""
        all_devices = self.get_all_devices()
        return [d for d in all_devices if d.get('room') == room]
    
    # ========================================================================
    # CONTROL OPERATIONS
    # ========================================================================
    
    def turn_on_lights(self, room: str = None) -> List[Dict[str, Any]]:
        """Turn on all lights in room or entire home."""
        results = []
        for device_id, device in self.devices.items():
            if isinstance(device, SmartLight):
                if room is None or device.room == room:
                    result = device.turn_on()
                    self.monitor.record_command(device_id, "on")
                    results.append(result)
        
        self.notification_manager.notify(
            title="Lights Turned On",
            message=f"Lights turned on in {room or 'home'}",
            notification_type=NotificationType.INFO
        )
        return results
    
    def turn_off_lights(self, room: str = None) -> List[Dict[str, Any]]:
        """Turn off all lights in room or entire home."""
        results = []
        for device_id, device in self.devices.items():
            if isinstance(device, SmartLight):
                if room is None or device.room == room:
                    result = device.turn_off()
                    self.monitor.record_command(device_id, "off")
                    results.append(result)
        
        self.notification_manager.notify(
            title="Lights Turned Off",
            message=f"Lights turned off in {room or 'home'}",
            notification_type=NotificationType.INFO
        )
        return results
    
    def set_temperature(self, target_temp: float) -> List[Dict[str, Any]]:
        """Set temperature for all thermostats."""
        results = []
        for device_id, device in self.devices.items():
            if isinstance(device, SmartThermostat):
                result = device.set_target_temperature(target_temp)
                results.append(result)
        
        return results
    
    # ========================================================================
    # SECURITY OPERATIONS
    # ========================================================================
    
    def lock_all_doors(self) -> List[Dict[str, Any]]:
        """Lock all doors."""
        results = []
        for device_id, device in self.devices.items():
            if isinstance(device, SmartDoorLock):
                result = device.lock()
                results.append(result)
        
        self.notification_manager.notify(
            title="Security",
            message="All doors have been locked",
            notification_type=NotificationType.INFO,
            priority=3
        )
        return results
    
    def unlock_door(self, location: str) -> Optional[Dict[str, Any]]:
        """Unlock specific door."""
        for device_id, device in self.devices.items():
            if isinstance(device, SmartDoorLock) and device.location == location:
                result = device.unlock()
                self.notification_manager.notify(
                    title="Door Unlocked",
                    message=f"Door at {location} unlocked",
                    notification_type=NotificationType.WARNING,
                    priority=2
                )
                return result
        return None
    
    def start_security_cameras(self) -> List[Dict[str, Any]]:
        """Start all security cameras."""
        results = []
        for device_id, device in self.devices.items():
            if isinstance(device, SmartCamera):
                result = device.start_recording()
                results.append(result)
        
        return results
    
    # ========================================================================
    # MONITORING AND ALERTS
    # ========================================================================
    
    def check_sensor_alerts(self) -> List[Dict[str, Any]]:
        """Check all sensors for alerts."""
        alerts = []
        for device_id, device in self.devices.items():
            if isinstance(device, SmartSensor):
                if device.alert_active:
                    alert = {
                        "device": device.name,
                        "type": device.sensor_type.value,
                        "value": device.value,
                        "unit": device.unit,
                        "location": device.location
                    }
                    alerts.append(alert)
                    
                    self.notification_manager.notify(
                        title=f"{device.sensor_type.value.replace('_', ' ').title()} Alert",
                        message=f"Alert from {device.name}: {device.value}{device.unit}",
                        notification_type=NotificationType.ALERT,
                        channels=[NotificationChannel.PUSH, NotificationChannel.SPEAKER],
                        priority=4
                    )
        
        return alerts
    
    def get_energy_stats(self) -> Dict[str, Any]:
        """Get energy consumption statistics."""
        return self.energy_monitor.get_consumption_stats()
    
    # ========================================================================
    # SCENES AND AUTOMATION
    # ========================================================================
    
    def create_scene(self, name: str, description: str = "") -> str:
        """Create new scene."""
        scene = self.scene_manager.create_scene(name, description)
        return scene.scene_id
    
    def activate_scene(self, scene_id: str) -> Dict[str, Any]:
        """Activate a scene."""
        return self.scene_manager.activate_scene(scene_id)
    
    def create_morning_scene(self) -> str:
        """Create predefined morning scene."""
        scene = self.scene_manager.create_scene(
            "Morning",
            "Morning routine: lights on, AC on, coffee"
        )
        
        # Add actions
        scene.add_action(lambda: self.turn_on_lights())
        scene.add_action(lambda: self.set_temperature(22))
        
        return scene.scene_id
    
    def create_evening_scene(self) -> str:
        """Create predefined evening scene."""
        scene = self.scene_manager.create_scene(
            "Evening",
            "Evening routine: lights dimmed, doors locked, security on"
        )
        
        scene.add_action(lambda: self.turn_off_lights())
        scene.add_action(lambda: self.lock_all_doors())
        scene.add_action(lambda: self.start_security_cameras())
        
        return scene.scene_id
    
    def create_away_scene(self) -> str:
        """Create predefined away scene."""
        scene = self.scene_manager.create_scene(
            "Away",
            "Away mode: all lights off, doors locked, security on"
        )
        
        scene.add_action(lambda: self.turn_off_lights())
        scene.add_action(lambda: self.lock_all_doors())
        scene.add_action(lambda: self.start_security_cameras())
        
        return scene.scene_id
    
    # ========================================================================
    # SYSTEM STATUS AND REPORTING
    # ========================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "system": self.name,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "devices_count": len(self.devices),
            "notifications": len(self.notification_manager.notifications),
            "active_sessions": len(self.access_manager.get_active_sessions()),
            "system_stats": self.monitor.get_system_stats()
        }
    
    def get_full_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_status(),
            "devices": self.get_all_devices(),
            "notifications": self.notification_manager.get_notifications(),
            "energy": self.get_energy_stats(),
            "scenes": self.scene_manager.get_all_scenes(),
            "schedules": self.schedule_manager.get_all_schedules(),
            "automations": self.automation_manager.get_all_rules()
        }
    
    def export_report(self, filename: str = "smart_home_report.json") -> str:
        """Export comprehensive report to JSON."""
        import json
        report = self.get_full_status_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        return filename


__all__ = [
    "SmartHomeSystem"
]
