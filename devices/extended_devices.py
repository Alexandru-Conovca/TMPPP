"""
Extended device types for a comprehensive Smart Home System.

Implements all device categories for:
- Lighting control
- Climate management (heating, AC, ventilation)
- Appliances control
- Security & Surveillance
- Access control
- Sensors (motion, smoke, water leak, door)
- Multimedia
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import json


class DeviceStatus(Enum):
    """Standard device status values."""
    ON = "on"
    OFF = "off"
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    ALERT = "alert"


class SensorType(Enum):
    """Types of sensors."""
    MOTION = "motion"
    SMOKE = "smoke"
    WATER_LEAK = "water_leak"
    DOOR_OPEN = "door_open"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    AIR_QUALITY = "air_quality"


# ============================================================================
# LIGHTING DEVICES
# ============================================================================

class SmartLight:
    """Smart lighting device with dimming and color control."""
    
    def __init__(self, name: str, brand: str, room: str, brightness: int = 100):
        """
        Initialize smart light.
        
        Args:
            name: Device name
            brand: Manufacturer brand
            room: Room location
            brightness: 0-100 brightness level
        """
        self.name = name
        self.brand = brand
        self.room = room
        self.brightness = max(0, min(100, brightness))
        self.status = DeviceStatus.OFF
        self.color_temp = 4000  # Kelvin
        self.schedule_id: Optional[str] = None
        
    def turn_on(self, brightness: int = 100) -> Dict[str, Any]:
        """Turn on light with optional brightness."""
        self.brightness = max(0, min(100, brightness))
        self.status = DeviceStatus.ON
        return {
            "status": "success",
            "device": self.name,
            "brightness": self.brightness,
            "power": "on"
        }
    
    def turn_off(self) -> Dict[str, Any]:
        """Turn off light."""
        self.status = DeviceStatus.OFF
        self.brightness = 0
        return {
            "status": "success",
            "device": self.name,
            "power": "off"
        }
    
    def set_brightness(self, brightness: int) -> Dict[str, Any]:
        """Set brightness level 0-100."""
        self.brightness = max(0, min(100, brightness))
        if self.brightness > 0:
            self.status = DeviceStatus.ON
        return {
            "status": "success",
            "device": self.name,
            "brightness": self.brightness
        }
    
    def set_color_temp(self, kelvin: int) -> Dict[str, Any]:
        """Set color temperature 2700-6500K."""
        self.color_temp = max(2700, min(6500, kelvin))
        return {
            "status": "success",
            "device": self.name,
            "color_temp": self.color_temp
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current light state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "room": self.room,
            "status": self.status.value,
            "brightness": self.brightness,
            "color_temp": self.color_temp,
            "power": "on" if self.status == DeviceStatus.ON else "off"
        }


# ============================================================================
# CLIMATE CONTROL DEVICES
# ============================================================================

class SmartThermostat:
    """Smart thermostat for temperature control."""
    
    def __init__(self, name: str, brand: str, room: str, target_temp: float = 21):
        """
        Initialize thermostat.
        
        Args:
            name: Device name
            brand: Manufacturer brand
            room: Room location
            target_temp: Target temperature in Celsius
        """
        self.name = name
        self.brand = brand
        self.room = room
        self.target_temp = target_temp
        self.current_temp = 20.0
        self.humidity = 50.0
        self.mode = "auto"  # auto, heating, cooling, off
        self.status = DeviceStatus.IDLE
        self.schedule_id: Optional[str] = None
        
    def set_target_temperature(self, temp: float) -> Dict[str, Any]:
        """Set target temperature."""
        self.target_temp = max(15, min(30, temp))
        self.status = DeviceStatus.ACTIVE
        return {
            "status": "success",
            "device": self.name,
            "target_temp": self.target_temp,
            "current_temp": self.current_temp
        }
    
    def set_mode(self, mode: str) -> Dict[str, Any]:
        """Set thermostat mode: auto, heating, cooling, off."""
        if mode in ["auto", "heating", "cooling", "off"]:
            self.mode = mode
            self.status = DeviceStatus.ACTIVE if mode != "off" else DeviceStatus.OFF
            return {"status": "success", "device": self.name, "mode": self.mode}
        return {"status": "error", "message": f"Invalid mode: {mode}"}
    
    def get_state(self) -> Dict[str, Any]:
        """Get thermostat state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "room": self.room,
            "status": self.status.value,
            "current_temp": self.current_temp,
            "target_temp": self.target_temp,
            "humidity": self.humidity,
            "mode": self.mode
        }


class SmartAC:
    """Smart air conditioning unit."""
    
    def __init__(self, name: str, brand: str, room: str):
        self.name = name
        self.brand = brand
        self.room = room
        self.status = DeviceStatus.OFF
        self.mode = "cool"  # cool, dry, fan, heat
        self.temperature = 24
        self.fan_speed = "auto"  # low, medium, high, auto
        self.power_consumption = 0
        
    def turn_on(self) -> Dict[str, Any]:
        """Turn on AC."""
        self.status = DeviceStatus.ON
        self.power_consumption = 1200  # Watts
        return {"status": "success", "device": self.name, "power": "on"}
    
    def turn_off(self) -> Dict[str, Any]:
        """Turn off AC."""
        self.status = DeviceStatus.OFF
        self.power_consumption = 0
        return {"status": "success", "device": self.name, "power": "off"}
    
    def get_state(self) -> Dict[str, Any]:
        """Get AC state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "room": self.room,
            "status": self.status.value,
            "mode": self.mode,
            "temperature": self.temperature,
            "fan_speed": self.fan_speed,
            "power_consumption": self.power_consumption
        }


class SmartVentilation:
    """Smart ventilation/exhaust system."""
    
    def __init__(self, name: str, brand: str, room: str):
        self.name = name
        self.brand = brand
        self.room = room
        self.status = DeviceStatus.OFF
        self.speed = 0  # 0-100
        self.mode = "auto"  # manual, auto, timer
        
    def set_speed(self, speed: int) -> Dict[str, Any]:
        """Set ventilation speed 0-100."""
        self.speed = max(0, min(100, speed))
        if self.speed > 0:
            self.status = DeviceStatus.ON
        else:
            self.status = DeviceStatus.OFF
        return {"status": "success", "device": self.name, "speed": self.speed}
    
    def get_state(self) -> Dict[str, Any]:
        """Get ventilation state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "room": self.room,
            "status": self.status.value,
            "speed": self.speed,
            "mode": self.mode
        }


# ============================================================================
# APPLIANCE CONTROL
# ============================================================================

class SmartAppliance:
    """Generic smart appliance (washing machine, dishwasher, oven, etc.)."""
    
    def __init__(self, name: str, brand: str, appliance_type: str):
        """
        Initialize smart appliance.
        
        Args:
            name: Device name
            brand: Manufacturer
            appliance_type: Type (washing_machine, dishwasher, oven, coffee_maker, etc.)
        """
        self.name = name
        self.brand = brand
        self.appliance_type = appliance_type
        self.status = DeviceStatus.OFF
        self.cycle = "idle"
        self.progress = 0  # 0-100
        self.power_consumption = 0
        self.schedule_id: Optional[str] = None
        
    def turn_on(self, cycle: str = "standard") -> Dict[str, Any]:
        """Start appliance with specified cycle."""
        self.status = DeviceStatus.ACTIVE
        self.cycle = cycle
        self.progress = 0
        self.power_consumption = 2000  # Average watts
        return {
            "status": "success",
            "device": self.name,
            "cycle": cycle,
            "message": f"Starting {cycle} cycle"
        }
    
    def turn_off(self) -> Dict[str, Any]:
        """Turn off appliance."""
        self.status = DeviceStatus.OFF
        self.cycle = "idle"
        self.progress = 0
        self.power_consumption = 0
        return {"status": "success", "device": self.name, "power": "off"}
    
    def get_state(self) -> Dict[str, Any]:
        """Get appliance state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "type": self.appliance_type,
            "status": self.status.value,
            "cycle": self.cycle,
            "progress": self.progress,
            "power_consumption": self.power_consumption
        }


# ============================================================================
# SECURITY & SURVEILLANCE
# ============================================================================

class SmartCamera:
    """Smart security camera with recording."""
    
    def __init__(self, name: str, brand: str, location: str, resolution: str = "1080p"):
        self.name = name
        self.brand = brand
        self.location = location
        self.resolution = resolution
        self.status = DeviceStatus.ON
        self.recording = True
        self.night_vision = True
        self.motion_detection = True
        self.alert_level = "medium"  # low, medium, high
        
    def start_recording(self) -> Dict[str, Any]:
        """Start recording."""
        self.recording = True
        self.status = DeviceStatus.ACTIVE
        return {"status": "success", "device": self.name, "recording": True}
    
    def stop_recording(self) -> Dict[str, Any]:
        """Stop recording."""
        self.recording = False
        self.status = DeviceStatus.IDLE
        return {"status": "success", "device": self.name, "recording": False}
    
    def get_state(self) -> Dict[str, Any]:
        """Get camera state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "location": self.location,
            "status": self.status.value,
            "recording": self.recording,
            "resolution": self.resolution,
            "night_vision": self.night_vision,
            "motion_detection": self.motion_detection
        }


class SmartDoorLock:
    """Smart door lock with access control."""
    
    def __init__(self, name: str, brand: str, location: str):
        self.name = name
        self.brand = brand
        self.location = location
        self.locked = True
        self.battery_level = 100
        self.last_access: Optional[str] = None
        self.access_log: List[Dict[str, Any]] = []
        
    def unlock(self, user_id: str = "system") -> Dict[str, Any]:
        """Unlock door."""
        self.locked = False
        timestamp = datetime.now().isoformat()
        self.last_access = timestamp
        self.access_log.append({
            "action": "unlock",
            "user": user_id,
            "timestamp": timestamp
        })
        return {"status": "success", "device": self.name, "locked": False}
    
    def lock(self, user_id: str = "system") -> Dict[str, Any]:
        """Lock door."""
        self.locked = True
        timestamp = datetime.now().isoformat()
        self.last_access = timestamp
        self.access_log.append({
            "action": "lock",
            "user": user_id,
            "timestamp": timestamp
        })
        return {"status": "success", "device": self.name, "locked": True}
    
    def get_state(self) -> Dict[str, Any]:
        """Get lock state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "location": self.location,
            "locked": self.locked,
            "battery_level": self.battery_level,
            "last_access": self.last_access
        }


# ============================================================================
# SENSORS
# ============================================================================

class SmartSensor:
    """Generic smart sensor with multiple sensing capabilities."""
    
    def __init__(self, name: str, brand: str, sensor_type: SensorType, location: str):
        """
        Initialize smart sensor.
        
        Args:
            name: Device name
            brand: Manufacturer
            sensor_type: Type of sensor
            location: Room/location
        """
        self.name = name
        self.brand = brand
        self.sensor_type = sensor_type
        self.location = location
        self.status = DeviceStatus.IDLE
        self.value = 0
        self.unit = self._get_unit()
        self.alert_threshold = self._get_default_threshold()
        self.alert_active = False
        self.battery_level = 100
        
    def _get_unit(self) -> str:
        """Get measurement unit based on sensor type."""
        units = {
            SensorType.TEMPERATURE: "°C",
            SensorType.HUMIDITY: "%",
            SensorType.CO2: "ppm",
            SensorType.AIR_QUALITY: "µg/m³",
            SensorType.MOTION: "detected",
            SensorType.SMOKE: "detected",
            SensorType.WATER_LEAK: "detected",
            SensorType.DOOR_OPEN: "open/closed"
        }
        return units.get(self.sensor_type, "")
    
    def _get_default_threshold(self) -> float:
        """Get default alert threshold."""
        thresholds = {
            SensorType.TEMPERATURE: 30,
            SensorType.HUMIDITY: 70,
            SensorType.CO2: 1000,
            SensorType.SMOKE: 1,
            SensorType.WATER_LEAK: 1
        }
        return thresholds.get(self.sensor_type, 100)
    
    def set_value(self, value: float) -> Dict[str, Any]:
        """Update sensor value and check alerts."""
        self.value = value
        self.status = DeviceStatus.ACTIVE
        
        # Check if alert should be triggered
        if value > self.alert_threshold:
            self.alert_active = True
            self.status = DeviceStatus.ALERT
        else:
            self.alert_active = False
        
        return {
            "status": "success",
            "device": self.name,
            "value": self.value,
            "unit": self.unit,
            "alert": self.alert_active
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get sensor state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "type": self.sensor_type.value,
            "location": self.location,
            "value": self.value,
            "unit": self.unit,
            "status": self.status.value,
            "alert": self.alert_active,
            "battery_level": self.battery_level
        }


# ============================================================================
# MULTIMEDIA
# ============================================================================

class SmartSpeaker:
    """Smart speaker with audio playback and voice control."""
    
    def __init__(self, name: str, brand: str, room: str):
        self.name = name
        self.brand = brand
        self.room = room
        self.status = DeviceStatus.OFF
        self.volume = 50  # 0-100
        self.playing = False
        self.current_track = ""
        self.microphone_enabled = True
        
    def play(self, track: str) -> Dict[str, Any]:
        """Play audio track."""
        self.current_track = track
        self.playing = True
        self.status = DeviceStatus.ACTIVE
        return {"status": "success", "device": self.name, "playing": track}
    
    def pause(self) -> Dict[str, Any]:
        """Pause playback."""
        self.playing = False
        self.status = DeviceStatus.IDLE
        return {"status": "success", "device": self.name, "playing": False}
    
    def set_volume(self, volume: int) -> Dict[str, Any]:
        """Set volume level."""
        self.volume = max(0, min(100, volume))
        return {"status": "success", "device": self.name, "volume": self.volume}
    
    def get_state(self) -> Dict[str, Any]:
        """Get speaker state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "room": self.room,
            "status": self.status.value,
            "volume": self.volume,
            "playing": self.playing,
            "current_track": self.current_track,
            "microphone": self.microphone_enabled
        }


class SmartTV:
    """Smart television with streaming capabilities."""
    
    def __init__(self, name: str, brand: str, room: str, screen_size: int = 55):
        self.name = name
        self.brand = brand
        self.room = room
        self.screen_size = screen_size
        self.status = DeviceStatus.OFF
        self.volume = 50
        self.input_source = "HDMI1"
        self.apps = ["Netflix", "YouTube", "Spotify", "Prime Video"]
        self.current_app = ""
        
    def turn_on(self) -> Dict[str, Any]:
        """Turn on TV."""
        self.status = DeviceStatus.ON
        return {"status": "success", "device": self.name, "power": "on"}
    
    def turn_off(self) -> Dict[str, Any]:
        """Turn off TV."""
        self.status = DeviceStatus.OFF
        self.current_app = ""
        return {"status": "success", "device": self.name, "power": "off"}
    
    def launch_app(self, app: str) -> Dict[str, Any]:
        """Launch streaming app."""
        if app in self.apps:
            self.current_app = app
            self.status = DeviceStatus.ACTIVE
            return {"status": "success", "device": self.name, "app": app}
        return {"status": "error", "message": f"App not available: {app}"}
    
    def get_state(self) -> Dict[str, Any]:
        """Get TV state."""
        return {
            "name": self.name,
            "brand": self.brand,
            "room": self.room,
            "status": self.status.value,
            "volume": self.volume,
            "input_source": self.input_source,
            "current_app": self.current_app,
            "screen_size": self.screen_size
        }


# ============================================================================
# ENERGY MANAGEMENT
# ============================================================================

class EnergyMonitor:
    """Monitors energy consumption of devices or entire home."""
    
    def __init__(self, name: str, location: str = "main"):
        self.name = name
        self.location = location
        self.status = DeviceStatus.ACTIVE
        self.current_power = 0  # Watts
        self.daily_consumption = 0  # kWh
        self.monthly_consumption = 0  # kWh
        self.cost_per_kwh = 0.15  # USD
        self.history: List[Dict[str, Any]] = []
        
    def update_power(self, watts: int) -> Dict[str, Any]:
        """Update current power consumption."""
        self.current_power = watts
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "power": watts
        })
        return {
            "status": "success",
            "device": self.name,
            "current_power": self.current_power,
            "daily_consumption": self.daily_consumption
        }
    
    def get_consumption_stats(self) -> Dict[str, Any]:
        """Get consumption statistics."""
        daily_cost = self.daily_consumption * self.cost_per_kwh
        monthly_cost = self.monthly_consumption * self.cost_per_kwh
        return {
            "daily_consumption": self.daily_consumption,
            "daily_cost": round(daily_cost, 2),
            "monthly_consumption": self.monthly_consumption,
            "monthly_cost": round(monthly_cost, 2),
            "current_power": self.current_power
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get monitor state."""
        return {
            "name": self.name,
            "location": self.location,
            "status": self.status.value,
            "current_power": self.current_power,
            "daily_consumption": self.daily_consumption,
            "monthly_consumption": self.monthly_consumption,
            "cost_per_kwh": self.cost_per_kwh
        }


__all__ = [
    "DeviceStatus",
    "SensorType",
    "SmartLight",
    "SmartThermostat",
    "SmartAC",
    "SmartVentilation",
    "SmartAppliance",
    "SmartCamera",
    "SmartDoorLock",
    "SmartSensor",
    "SmartSpeaker",
    "SmartTV",
    "EnergyMonitor"
]
