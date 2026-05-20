"""
Smart Home System - Notifications, Scheduling, and Automation.

Handles:
- Real-time notifications and alerts
- Time-based scheduling
- Automation rules and triggers
- Scene management
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from enum import Enum
from datetime import datetime, time, timedelta
import json
from dataclasses import dataclass, asdict


class NotificationType(Enum):
    """Types of notifications."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """How notifications are delivered."""
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    SPEAKER = "speaker"


@dataclass
class Notification:
    """Represents a single notification."""
    id: str
    title: str
    message: str
    type: NotificationType
    channels: List[NotificationChannel]
    timestamp: str
    read: bool = False
    priority: int = 1  # 1-5, higher = more urgent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type.value,
            "channels": [c.value for c in self.channels],
            "timestamp": self.timestamp,
            "read": self.read,
            "priority": self.priority
        }


class NotificationManager:
    """Manages all system notifications."""
    
    def __init__(self):
        """Initialize notification manager."""
        self.notifications: List[Notification] = []
        self.subscribers: Dict[str, List[Callable]] = {}
        self.notification_id_counter = 0
        
    def subscribe(self, notification_type: str, callback: Callable) -> None:
        """
        Subscribe to notification type.
        
        Args:
            notification_type: Type to subscribe to
            callback: Function to call when notification is sent
        """
        if notification_type not in self.subscribers:
            self.subscribers[notification_type] = []
        self.subscribers[notification_type].append(callback)
    
    def notify(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        channels: List[NotificationChannel] = None,
        priority: int = 1
    ) -> Notification:
        """
        Send notification.
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            channels: Delivery channels
            priority: Priority level (1-5)
            
        Returns:
            Created notification object
        """
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        
        self.notification_id_counter += 1
        notification = Notification(
            id=f"notif_{self.notification_id_counter}",
            title=title,
            message=message,
            type=notification_type,
            channels=channels,
            timestamp=datetime.now().isoformat(),
            priority=priority
        )
        
        self.notifications.append(notification)
        
        # Call subscribers
        type_key = notification_type.value
        if type_key in self.subscribers:
            for callback in self.subscribers[type_key]:
                try:
                    callback(notification)
                except Exception as e:
                    print(f"Error calling subscriber: {e}")
        
        return notification
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get all notifications."""
        notifs = self.notifications
        if unread_only:
            notifs = [n for n in notifs if not n.read]
        return [n.to_dict() for n in notifs]
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        for notif in self.notifications:
            if notif.id == notification_id:
                notif.read = True
                return True
        return False
    
    def clear_notifications(self) -> int:
        """Clear all old notifications."""
        count = len(self.notifications)
        self.notifications = []
        return count


# ============================================================================
# SCHEDULING SYSTEM
# ============================================================================

class ScheduleType(Enum):
    """Types of schedules."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    INTERVAL = "interval"


class Schedule:
    """Represents a scheduled task."""
    
    def __init__(
        self,
        schedule_id: str,
        name: str,
        action: Callable,
        schedule_type: ScheduleType,
        start_time: time = None,
        days: List[int] = None,
        interval_minutes: int = 60
    ):
        """
        Initialize schedule.
        
        Args:
            schedule_id: Unique identifier
            name: Schedule name
            action: Function to execute
            schedule_type: Type of schedule
            start_time: Time to execute (for daily, weekly, monthly)
            days: Days to execute (0=Monday for weekly)
            interval_minutes: Minutes between executions (for interval)
        """
        self.schedule_id = schedule_id
        self.name = name
        self.action = action
        self.schedule_type = schedule_type
        self.start_time = start_time or time(12, 0)
        self.days = days or []
        self.interval_minutes = interval_minutes
        self.enabled = True
        self.last_executed: Optional[datetime] = None
        self.next_execution: Optional[datetime] = None
        self.execution_count = 0
        
    def should_execute(self, current_time: datetime = None) -> bool:
        """Check if schedule should execute now."""
        if not self.enabled:
            return False
            
        if current_time is None:
            current_time = datetime.now()
        
        current_clock = current_time.time()
        
        if self.schedule_type == ScheduleType.ONCE:
            if self.last_executed is None and current_clock >= self.start_time:
                return True
        
        elif self.schedule_type == ScheduleType.DAILY:
            if current_clock == self.start_time or (
                self.last_executed and
                self.last_executed.date() != current_time.date() and
                current_clock >= self.start_time
            ):
                return True
        
        elif self.schedule_type == ScheduleType.WEEKLY:
            weekday = current_time.weekday()
            if weekday in self.days and (
                self.last_executed is None or
                (current_time - self.last_executed).days >= 7
            ):
                if current_clock >= self.start_time:
                    return True
        
        elif self.schedule_type == ScheduleType.INTERVAL:
            if self.last_executed is None:
                return True
            if (current_time - self.last_executed).total_seconds() >= (self.interval_minutes * 60):
                return True
        
        return False
    
    def execute(self) -> Dict[str, Any]:
        """Execute the scheduled action."""
        try:
            result = self.action()
            self.last_executed = datetime.now()
            self.execution_count += 1
            return {
                "status": "success",
                "schedule": self.name,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "schedule": self.name,
                "error": str(e)
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Get schedule state."""
        return {
            "id": self.schedule_id,
            "name": self.name,
            "type": self.schedule_type.value,
            "start_time": self.start_time.isoformat(),
            "enabled": self.enabled,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "execution_count": self.execution_count
        }


class ScheduleManager:
    """Manages all scheduled tasks."""
    
    def __init__(self, notification_manager: NotificationManager = None):
        """Initialize schedule manager."""
        self.schedules: Dict[str, Schedule] = {}
        self.notification_manager = notification_manager
        self.schedule_id_counter = 0
        
    def add_schedule(
        self,
        name: str,
        action: Callable,
        schedule_type: ScheduleType,
        start_time: time = None,
        days: List[int] = None,
        interval_minutes: int = 60
    ) -> Schedule:
        """Add new schedule."""
        self.schedule_id_counter += 1
        schedule_id = f"schedule_{self.schedule_id_counter}"
        
        schedule = Schedule(
            schedule_id,
            name,
            action,
            schedule_type,
            start_time,
            days,
            interval_minutes
        )
        
        self.schedules[schedule_id] = schedule
        return schedule
    
    def execute_due_schedules(self) -> List[Dict[str, Any]]:
        """Execute all schedules that are due."""
        results = []
        current_time = datetime.now()
        
        for schedule_id, schedule in self.schedules.items():
            if schedule.should_execute(current_time):
                result = schedule.execute()
                results.append(result)
                
                if self.notification_manager:
                    self.notification_manager.notify(
                        title="Schedule Executed",
                        message=f"Schedule '{schedule.name}' executed successfully",
                        notification_type=NotificationType.INFO
                    )
        
        return results
    
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Get all schedules."""
        return [s.get_state() for s in self.schedules.values()]
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = False
            return True
        return False
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = True
            return True
        return False


# ============================================================================
# AUTOMATION RULES
# ============================================================================

class AutomationRule:
    """Automation rule - trigger conditions and actions."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        trigger: Callable,
        actions: List[Callable],
        enabled: bool = True
    ):
        """
        Initialize automation rule.
        
        Args:
            rule_id: Unique identifier
            name: Rule name
            trigger: Function that returns True when rule should execute
            actions: List of functions to execute when triggered
            enabled: Whether rule is active
        """
        self.rule_id = rule_id
        self.name = name
        self.trigger = trigger
        self.actions = actions
        self.enabled = enabled
        self.execution_count = 0
        self.last_executed: Optional[datetime] = None
        
    def check_and_execute(self) -> Dict[str, Any]:
        """Check trigger and execute actions if needed."""
        if not self.enabled:
            return {"status": "disabled"}
        
        try:
            if self.trigger():
                results = []
                for action in self.actions:
                    results.append(action())
                
                self.last_executed = datetime.now()
                self.execution_count += 1
                
                return {
                    "status": "triggered",
                    "rule": self.name,
                    "results": results
                }
        except Exception as e:
            return {
                "status": "error",
                "rule": self.name,
                "error": str(e)
            }
        
        return {"status": "not_triggered"}
    
    def get_state(self) -> Dict[str, Any]:
        """Get rule state."""
        return {
            "id": self.rule_id,
            "name": self.name,
            "enabled": self.enabled,
            "execution_count": self.execution_count,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None
        }


class AutomationManager:
    """Manages all automation rules."""
    
    def __init__(self, notification_manager: NotificationManager = None):
        """Initialize automation manager."""
        self.rules: Dict[str, AutomationRule] = {}
        self.notification_manager = notification_manager
        self.rule_id_counter = 0
        
    def add_rule(
        self,
        name: str,
        trigger: Callable,
        actions: List[Callable]
    ) -> AutomationRule:
        """Add new automation rule."""
        self.rule_id_counter += 1
        rule_id = f"rule_{self.rule_id_counter}"
        
        rule = AutomationRule(rule_id, name, trigger, actions)
        self.rules[rule_id] = rule
        return rule
    
    def check_all_rules(self) -> List[Dict[str, Any]]:
        """Check and execute all rules."""
        results = []
        for rule_id, rule in self.rules.items():
            result = rule.check_and_execute()
            if result["status"] in ["triggered", "error"]:
                results.append(result)
        
        return results
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Get all rules."""
        return [r.get_state() for r in self.rules.values()]


# ============================================================================
# SCENES
# ============================================================================

class Scene:
    """Pre-configured scene with multiple device actions."""
    
    def __init__(self, scene_id: str, name: str, description: str = ""):
        """
        Initialize scene.
        
        Args:
            scene_id: Unique identifier
            name: Scene name
            description: Scene description
        """
        self.scene_id = scene_id
        self.name = name
        self.description = description
        self.actions: List[Callable] = []
        self.created_at = datetime.now()
        
    def add_action(self, action: Callable) -> None:
        """Add action to scene."""
        self.actions.append(action)
    
    def activate(self) -> Dict[str, Any]:
        """Activate scene and execute all actions."""
        results = []
        for action in self.actions:
            try:
                results.append(action())
            except Exception as e:
                results.append({"error": str(e)})
        
        return {
            "status": "success",
            "scene": self.name,
            "actions_executed": len(self.actions),
            "results": results
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get scene state."""
        return {
            "id": self.scene_id,
            "name": self.name,
            "description": self.description,
            "actions_count": len(self.actions),
            "created_at": self.created_at.isoformat()
        }


class SceneManager:
    """Manages all scenes."""
    
    def __init__(self):
        """Initialize scene manager."""
        self.scenes: Dict[str, Scene] = {}
        self.scene_id_counter = 0
        
    def create_scene(self, name: str, description: str = "") -> Scene:
        """Create new scene."""
        self.scene_id_counter += 1
        scene_id = f"scene_{self.scene_id_counter}"
        
        scene = Scene(scene_id, name, description)
        self.scenes[scene_id] = scene
        return scene
    
    def activate_scene(self, scene_id: str) -> Dict[str, Any]:
        """Activate a scene by ID."""
        if scene_id in self.scenes:
            return self.scenes[scene_id].activate()
        return {"status": "error", "message": f"Scene not found: {scene_id}"}
    
    def get_all_scenes(self) -> List[Dict[str, Any]]:
        """Get all scenes."""
        return [s.get_state() for s in self.scenes.values()]


__all__ = [
    "NotificationType",
    "NotificationChannel",
    "Notification",
    "NotificationManager",
    "ScheduleType",
    "Schedule",
    "ScheduleManager",
    "AutomationRule",
    "AutomationManager",
    "Scene",
    "SceneManager"
]
