"""
Smart Home Database Module

Provides persistent storage for devices, scenes, rooms, and device history.
Uses SQLite for local storage with automatic backup.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from threading import Lock


class SmartHomeDB:
    """SQLite database for Smart Home persistence."""

    def __init__(self, db_path: str = "data/smarthome.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Devices table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    brand TEXT,
                    room TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
                """
            )

            # Scenes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scenes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    actions TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Rooms table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rooms (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Device states history
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS device_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(device_id) REFERENCES devices(id)
                )
                """
            )

            # System settings
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_device_room ON devices(room)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_device_states_device ON device_states(device_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_device_states_timestamp ON device_states(timestamp)"
            )

            conn.commit()
            conn.close()

    # ==================== DEVICE OPERATIONS ====================

    def save_device(
        self,
        device_id: str,
        name: str,
        device_type: str,
        brand: str = "unknown",
        room: str = "Unassigned",
        location: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save device to database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                metadata_json = json.dumps(metadata or {})

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO devices 
                    (id, name, type, brand, room, location, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                    """,
                    (device_id, name, device_type, brand, room, location, metadata_json),
                )

                conn.commit()
                conn.close()
                return True
        except Exception as e:
            return False

    def load_devices(self) -> List[Dict[str, Any]]:
        """Load all devices from database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM devices")
                rows = cursor.fetchall()
                conn.close()

                devices = []
                for row in rows:
                    devices.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "type": row[2],
                            "brand": row[3],
                            "room": row[4],
                            "location": row[5],
                            "created_at": row[6],
                            "updated_at": row[7],
                            "metadata": json.loads(row[8]) if row[8] else {},
                        }
                    )

                return devices
        except Exception:
            return []

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get single device by ID."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "type": row[2],
                        "brand": row[3],
                        "room": row[4],
                        "location": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                        "metadata": json.loads(row[8]) if row[8] else {},
                    }
        except Exception:
            pass

        return None

    def get_devices_by_room(self, room: str) -> List[Dict[str, Any]]:
        """Get all devices in a specific room."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM devices WHERE room = ?", (room,))
                rows = cursor.fetchall()
                conn.close()

                devices = []
                for row in rows:
                    devices.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "type": row[2],
                            "brand": row[3],
                            "room": row[4],
                            "location": row[5],
                            "metadata": json.loads(row[8]) if row[8] else {},
                        }
                    )

                return devices
        except Exception:
            return []

    def delete_device(self, device_id: str) -> bool:
        """Delete device from database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Delete device states first
                cursor.execute("DELETE FROM device_states WHERE device_id = ?", (device_id,))

                # Delete device
                cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    def update_device_room(self, device_id: str, room: str) -> bool:
        """Update device room assignment."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE devices SET room = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (room, device_id),
                )

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    # ==================== DEVICE STATE HISTORY ====================

    def record_device_state(self, device_id: str, state: Dict[str, Any]) -> bool:
        """Record device state change to history."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                state_json = json.dumps(state)

                cursor.execute(
                    "INSERT INTO device_states (device_id, state) VALUES (?, ?)",
                    (device_id, state_json),
                )

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    def get_device_history(
        self, device_id: str, hours: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get device state history for past N hours."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

                cursor.execute(
                    """
                    SELECT id, device_id, state, timestamp FROM device_states
                    WHERE device_id = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (device_id, cutoff_time, limit),
                )

                rows = cursor.fetchall()
                conn.close()

                history = []
                for row in rows:
                    history.append(
                        {
                            "id": row[0],
                            "device_id": row[1],
                            "state": json.loads(row[2]),
                            "timestamp": row[3],
                        }
                    )

                return history
        except Exception:
            return []

    def clear_old_states(self, days: int = 30) -> int:
        """Delete device states older than N days."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

                cursor.execute(
                    "DELETE FROM device_states WHERE timestamp < ?",
                    (cutoff_time,),
                )

                deleted = cursor.rowcount
                conn.commit()
                conn.close()

                return deleted
        except Exception:
            return 0

    # ==================== SCENE OPERATIONS ====================

    def save_scene(
        self,
        scene_id: str,
        name: str,
        description: str = "",
        actions: List[Dict[str, Any]] = None,
    ) -> bool:
        """Save scene to database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                actions_json = json.dumps(actions or [])

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO scenes
                    (id, name, description, actions, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (scene_id, name, description, actions_json),
                )

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    def load_scenes(self) -> List[Dict[str, Any]]:
        """Load all scenes from database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM scenes")
                rows = cursor.fetchall()
                conn.close()

                scenes = []
                for row in rows:
                    scenes.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2],
                            "actions": json.loads(row[3]),
                            "created_at": row[4],
                            "updated_at": row[5],
                        }
                    )

                return scenes
        except Exception:
            return []

    def delete_scene(self, scene_id: str) -> bool:
        """Delete scene from database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM scenes WHERE id = ?", (scene_id,))

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    # ==================== ROOM OPERATIONS ====================

    def save_room(self, room_id: str, name: str, description: str = "") -> bool:
        """Save room to database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO rooms (id, name, description)
                    VALUES (?, ?, ?)
                    """,
                    (room_id, name, description),
                )

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    def load_rooms(self) -> List[Dict[str, Any]]:
        """Load all rooms from database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM rooms")
                rows = cursor.fetchall()
                conn.close()

                rooms = []
                for row in rows:
                    rooms.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "description": row[2],
                            "created_at": row[3],
                        }
                    )

                return rooms
        except Exception:
            return []

    def delete_room(self, room_id: str) -> bool:
        """Delete room from database."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    # ==================== SETTINGS ====================

    def set_setting(self, key: str, value: str) -> bool:
        """Save system setting."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (key, value),
                )

                conn.commit()
                conn.close()
                return True
        except Exception:
            return False

    def get_setting(self, key: str, default: str = "") -> str:
        """Get system setting."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                conn.close()

                return row[0] if row else default
        except Exception:
            return default

    # ==================== BACKUP & MAINTENANCE ====================

    def backup(self, backup_path: str = None) -> bool:
        """Create database backup."""
        try:
            if backup_path is None:
                backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            with self._lock:
                conn = sqlite3.connect(self.db_path)
                backup_conn = sqlite3.connect(backup_path)

                with backup_conn:
                    conn.backup(backup_conn)

                conn.close()
                backup_conn.close()

            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM devices")
                device_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM scenes")
                scene_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM rooms")
                room_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM device_states")
                state_count = cursor.fetchone()[0]

                conn.close()

                return {
                    "devices": device_count,
                    "scenes": scene_count,
                    "rooms": room_count,
                    "state_records": state_count,
                }
        except Exception:
            return {"devices": 0, "scenes": 0, "rooms": 0, "state_records": 0}

    def export_to_json(self, export_path: str) -> bool:
        """Export all data to JSON file."""
        try:
            export_data = {
                "devices": self.load_devices(),
                "scenes": self.load_scenes(),
                "rooms": self.load_rooms(),
                "exported_at": datetime.now().isoformat(),
            }

            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            return True
        except Exception:
            return False
