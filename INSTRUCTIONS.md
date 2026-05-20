# Smart Home System — Complete Guide

## Quick Start

### 1. Setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run
```powershell
python main.py          # GUI mode (recommended)
# OR
python main.py console  # Console mode
```

---

## System Features

### 🏠 Home Page
- Device cards with toggle buttons
- Room-based organization
- Live state updates

### 📋 Scenarios
- Pre-built scenes (Morning, Evening, Night)
- Custom scenario creation
- Multi-device control

### 🛏️ Rooms
- Room management
- Device assignment
- Room-based operations

### 🔍 Device Discovery
- Real network scanning (ARP/ping)
- Auto device type detection
- Confidence-based suggestions

---

## Supported Devices

💡 Light | 🌡️ Thermostat | 📷 Camera | 🔐 Door Lock | ❄️ AC | 🔌 Appliance | 🔊 Speaker | 📺 TV | 📡 Sensor

---

## Database

Devices and scenes are automatically persisted to SQLite database:
- **Location:** `data/smarthome.db`
- **Auto-created on first run**
- **Tables:** devices, scenes, rooms, device_states
- **Automatic backup** before updates

### Database Operations
```python
from smart_home.database import SmartHomeDB

db = SmartHomeDB()
db.save_device(device_id, name, type, brand, room)
db.load_devices()
db.delete_device(device_id)
db.get_device_history(device_id, hours=24)
```

---

## Design Patterns

All 9 Gang of Four patterns integrated:

- **Command** — Device operations via RemoteControl
- **Observer** — Device state notifications
- **Strategy** — Device behavior modes
- **Composite** — Room-based grouping
- **Decorator** — Device enhancements
- **Proxy** — Logging & security
- **Facade** — Unified system API
- **Template Method** — Standard routines
- **Chain of Responsibility** — Event pipeline

---

## Usage Examples

### Add Device via Network Scan
1. Click "Add Device"
2. Click "Scan Network"
3. Select discovered device
4. Confirm type/brand
5. Click "Add"

### Command Pattern
```python
system.execute_device_command("light_001", "on")
system.execute_device_command("thermostat_001", "set_temp", temp=22)
```

### Observer Pattern
```python
system.subscribe_to_updates(lambda event: print(event))
```

### Strategy Pattern
```python
system.set_device_strategy("light_001", "night")
```

### Composite Pattern (Rooms)
```python
system.add_device_to_room("light_001", "Living Room")
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Home |
| `2` | Scenarios |
| `3` | Rooms |
| `Ctrl+A` | Add Device |

---

## Project Structure

```
smart_home/          # Core system
├── manager.py       # Device/scene management
├── integrated_system.py   # Pattern integration
├── network_scanner.py     # Network discovery
└── database.py      # Database persistence

devices/             # Device implementations
behavioral/          # GoF behavioral patterns
structural/          # GoF structural patterns
GUI/                 # PyQt5 interface
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GUI won't start | Check Python 3.9+, update PyQt5 |
| Network scan fails | Run as Admin (Windows), install arp-scan (Linux) |
| Database error | Delete `data/smarthome.db`, restart app |
| Devices not saving | Check `data/` folder permissions |

---

## Requirements

- Python 3.9+
- PyQt5 >= 5.15
- SQLite3 (included)

---

**Version:** 2.0 | **Status:** Production Ready ✅
