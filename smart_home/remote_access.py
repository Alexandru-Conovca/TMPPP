"""
Remote Access and Monitoring System for Smart Home.

Handles:
- Remote device control
- Mobile/Web API simulation
- Status monitoring and logging
- System statistics and reports
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from abc import ABC, abstractmethod


class UserRole(Enum):
    """User access roles."""
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User:
    """System user with access control."""
    
    def __init__(self, user_id: str, username: str, email: str, role: UserRole):
        """
        Initialize user.
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: Email address
            role: User role
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = ""  # Would be proper hash in production
        self.created_at = datetime.now()
        self.last_login: Optional[datetime] = None
        self.devices: List[str] = []  # Devices user can control
        self.enabled = True
        
    def has_permission(self, permission: str) -> bool:
        """Check if user has permission."""
        permissions = {
            UserRole.OWNER: ["all"],
            UserRole.ADMIN: ["view_all", "control_all", "manage_users"],
            UserRole.USER: ["view_own", "control_own"],
            UserRole.GUEST: ["view_own"]
        }
        perms = permissions.get(self.role, [])
        return "all" in perms or permission in perms
    
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "devices_count": len(self.devices),
            "enabled": self.enabled
        }


class Session:
    """User session for remote access."""
    
    def __init__(self, session_id: str, user: User):
        """
        Initialize session.
        
        Args:
            session_id: Unique session identifier
            user: User object
        """
        self.session_id = session_id
        self.user = user
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.ip_address = "127.0.0.1"  # Simulated
        self.device_type = "mobile"  # mobile, web, api
        self.active = True
        
    def is_valid(self, timeout_minutes: int = 60) -> bool:
        """Check if session is still valid."""
        if not self.active:
            return False
        
        elapsed = (datetime.now() - self.last_activity).total_seconds() / 60
        return elapsed < timeout_minutes
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def get_info(self) -> Dict[str, Any]:
        """Get session info."""
        return {
            "session_id": self.session_id,
            "user": self.user.username,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "device_type": self.device_type,
            "active": self.active
        }


class RemoteAccessManager:
    """Manages remote access and user sessions."""
    
    def __init__(self):
        """Initialize remote access manager."""
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.user_id_counter = 0
        self.session_id_counter = 0
        self.audit_log: List[Dict[str, Any]] = []
        
        # Create default users
        self._create_default_users()
        
    def _create_default_users(self) -> None:
        """Create default users for demo."""
        owner = User("user_1", "owner", "owner@home.local", UserRole.OWNER)
        admin = User("user_2", "admin", "admin@home.local", UserRole.ADMIN)
        user = User("user_3", "user", "user@home.local", UserRole.USER)
        
        self.users["user_1"] = owner
        self.users["user_2"] = admin
        self.users["user_3"] = user
        self.user_id_counter = 3
        
    def create_user(self, username: str, email: str, role: UserRole) -> User:
        """Create new user."""
        self.user_id_counter += 1
        user_id = f"user_{self.user_id_counter}"
        user = User(user_id, username, email, role)
        self.users[user_id] = user
        
        self._log_action(f"user_created", f"User {username} created with role {role.value}")
        return user
    
    def login(self, username: str, password: str = "password") -> Optional[Session]:
        """
        Login user and create session.
        
        Args:
            username: Username
            password: Password (simplified)
            
        Returns:
            Session object if successful, None otherwise
        """
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not user.enabled:
            self._log_action("login_failed", f"Failed login attempt for {username}")
            return None
        
        # Create session
        self.session_id_counter += 1
        session_id = f"session_{self.session_id_counter}"
        session = Session(session_id, user)
        self.sessions[session_id] = session
        
        user.last_login = datetime.now()
        self._log_action("login_success", f"User {username} logged in")
        
        return session
    
    def logout(self, session_id: str) -> bool:
        """Logout user session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.active = False
            self._log_action("logout", f"User {session.user.username} logged out")
            return True
        return False
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session if valid."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.is_valid():
                session.update_activity()
                return session
        return None
    
    def _log_action(self, action: str, details: str) -> None:
        """Log action to audit log."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        return [u.get_profile() for u in self.users.values()]
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions."""
        active = [s for s in self.sessions.values() if s.is_valid()]
        return [s.get_info() for s in active]
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log."""
        return self.audit_log[-limit:]


# ============================================================================
# MONITORING AND STATISTICS
# ============================================================================

class DeviceMetric:
    """Tracks metrics for a device."""
    
    def __init__(self, device_id: str, device_name: str):
        """Initialize device metric tracker."""
        self.device_id = device_id
        self.device_name = device_name
        self.on_count = 0
        self.off_count = 0
        self.power_consumption = 0.0  # kWh
        self.uptime_seconds = 0
        self.error_count = 0
        self.last_state_change: Optional[datetime] = None
        self.state_history: List[Tuple[datetime, str]] = []
        
    def record_state_change(self, new_state: str) -> None:
        """Record state change."""
        timestamp = datetime.now()
        self.state_history.append((timestamp, new_state))
        self.last_state_change = timestamp
        
        if new_state == "on":
            self.on_count += 1
        elif new_state == "off":
            self.off_count += 1
    
    def record_power_consumption(self, kwh: float) -> None:
        """Record power consumption."""
        self.power_consumption += kwh
    
    def record_error(self) -> None:
        """Record error."""
        self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get device statistics."""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "on_count": self.on_count,
            "off_count": self.off_count,
            "power_consumption_kwh": round(self.power_consumption, 2),
            "error_count": self.error_count,
            "last_state_change": self.last_state_change.isoformat() if self.last_state_change else None
        }


class SystemMonitor:
    """Monitors system health and statistics."""
    
    def __init__(self):
        """Initialize system monitor."""
        self.device_metrics: Dict[str, DeviceMetric] = {}
        self.system_start_time = datetime.now()
        self.total_commands = 0
        self.failed_commands = 0
        self.events: List[Dict[str, Any]] = []
        
    def register_device(self, device_id: str, device_name: str) -> None:
        """Register device for monitoring."""
        self.device_metrics[device_id] = DeviceMetric(device_id, device_name)
    
    def record_command(self, device_id: str, command: str, success: bool = True) -> None:
        """Record command execution."""
        self.total_commands += 1
        if not success:
            self.failed_commands += 1
        
        if device_id in self.device_metrics:
            if success:
                self.device_metrics[device_id].record_state_change(command)
            else:
                self.device_metrics[device_id].record_error()
    
    def record_event(self, event_type: str, description: str, severity: str = "info") -> None:
        """Record system event."""
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "severity": severity
        })
    
    def get_device_stats(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for specific device."""
        if device_id in self.device_metrics:
            return self.device_metrics[device_id].get_stats()
        return None
    
    def get_all_device_stats(self) -> List[Dict[str, Any]]:
        """Get all device statistics."""
        return [m.get_stats() for m in self.device_metrics.values()]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        uptime_seconds = (datetime.now() - self.system_start_time).total_seconds()
        uptime_hours = uptime_seconds / 3600
        success_rate = 0
        if self.total_commands > 0:
            success_rate = ((self.total_commands - self.failed_commands) / self.total_commands) * 100
        
        return {
            "system_uptime_hours": round(uptime_hours, 2),
            "total_devices": len(self.device_metrics),
            "total_commands": self.total_commands,
            "failed_commands": self.failed_commands,
            "success_rate_percent": round(success_rate, 2),
            "total_events": len(self.events)
        }
    
    def get_events(self, limit: int = 50, severity: str = None) -> List[Dict[str, Any]]:
        """Get system events."""
        events = self.events
        if severity:
            events = [e for e in events if e["severity"] == severity]
        return events[-limit:]


# ============================================================================
# API GATEWAY
# ============================================================================

class APIGateway:
    """API gateway for remote device control."""
    
    def __init__(self, access_manager: RemoteAccessManager, monitor: SystemMonitor):
        """
        Initialize API gateway.
        
        Args:
            access_manager: Remote access manager
            monitor: System monitor
        """
        self.access_manager = access_manager
        self.monitor = monitor
        self.api_calls: List[Dict[str, Any]] = []
        self.api_call_counter = 0
        
    def execute_command(
        self,
        session_id: str,
        device_id: str,
        command: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute command on device through API.
        
        Args:
            session_id: User session ID
            device_id: Target device ID
            command: Command to execute
            parameters: Command parameters
            
        Returns:
            Result of command execution
        """
        # Verify session
        session = self.access_manager.get_session(session_id)
        if not session:
            return {
                "status": "error",
                "message": "Invalid or expired session"
            }
        
        # Verify permissions
        if not session.user.has_permission("control_own"):
            return {
                "status": "error",
                "message": "Insufficient permissions"
            }
        
        # Log API call
        self.api_call_counter += 1
        self.api_calls.append({
            "api_call_id": f"api_{self.api_call_counter}",
            "timestamp": datetime.now().isoformat(),
            "user": session.user.username,
            "device_id": device_id,
            "command": command,
            "parameters": parameters or {}
        })
        
        # Execute command (simulated)
        success = True
        self.monitor.record_command(device_id, command, success)
        
        return {
            "status": "success",
            "device_id": device_id,
            "command": command,
            "result": "Command executed"
        }
    
    def get_device_status(self, session_id: str, device_id: str) -> Dict[str, Any]:
        """Get device status."""
        session = self.access_manager.get_session(session_id)
        if not session:
            return {"status": "error", "message": "Invalid session"}
        
        return {
            "device_id": device_id,
            "status": "ok",
            "last_update": datetime.now().isoformat()
        }
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API statistics."""
        return {
            "total_calls": len(self.api_calls),
            "unique_users": len(set(c["user"] for c in self.api_calls)),
            "calls_last_hour": self._count_calls_last_hour()
        }
    
    def _count_calls_last_hour(self) -> int:
        """Count API calls in last hour."""
        hour_ago = datetime.now() - timedelta(hours=1)
        return sum(1 for c in self.api_calls 
                  if datetime.fromisoformat(c["timestamp"]) > hour_ago)
    
    def get_api_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get API call logs."""
        return self.api_calls[-limit:]


__all__ = [
    "UserRole",
    "User",
    "Session",
    "RemoteAccessManager",
    "DeviceMetric",
    "SystemMonitor",
    "APIGateway"
]
