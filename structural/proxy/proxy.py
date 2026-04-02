from devices.device import Device


class LoggingProxy(Device):

    def __init__(self, real_device: Device) -> None:
        super().__init__(name=real_device.name, brand=real_device.brand)
        self._real_device = real_device

    def device_type(self) -> str:
        return f"LoggingProxy({self._real_device.device_type()})"

    def operate(self) -> str:
        result = self._real_device.operate()
        return f"[LOG] {self.name}: {result}"

    def clone(self) -> "LoggingProxy":
        return LoggingProxy(real_device=self._real_device.clone())

    def visualize(self) -> str:
        wrapped_visual = self._real_device.visualize() if hasattr(self._real_device, "visualize") else str(self._real_device)
        return f"{wrapped_visual} [LoggingProxy]"


class SecurityProxy(Device):

    def __init__(self, real_device: Device, user_role: str = "user") -> None:
        super().__init__(name=real_device.name, brand=real_device.brand)
        self._real_device = real_device
        self.user_role = user_role

    def device_type(self) -> str:
        return f"SecurityProxy({self._real_device.device_type()})"

    def operate(self) -> str:
        if self.user_role != "admin":
            return f"Access denied for {self.user_role} on '{self.name}'"
        return self._real_device.operate()

    def clone(self) -> "SecurityProxy":
        return SecurityProxy(real_device=self._real_device.clone(), user_role=self.user_role)

    def visualize(self) -> str:
        wrapped_visual = self._real_device.visualize() if hasattr(self._real_device, "visualize") else str(self._real_device)
        return f"{wrapped_visual} [SecurityProxy role={self.user_role}]"


class CacheProxy(Device):

    def __init__(self, real_device: Device) -> None:
        super().__init__(name=real_device.name, brand=real_device.brand)
        self._real_device = real_device
        self._cached_value = None

    def device_type(self) -> str:
        return f"CacheProxy({self._real_device.device_type()})"

    def operate(self) -> str:
        if self._cached_value is None:
            self._cached_value = self._real_device.operate()
            return self._cached_value
        return f"[CACHE] {self._cached_value}"

    def invalidate_cache(self) -> None:
        self._cached_value = None

    def clone(self) -> "CacheProxy":
        cloned = CacheProxy(real_device=self._real_device.clone())
        cloned._cached_value = self._cached_value
        return cloned

    def visualize(self) -> str:
        wrapped_visual = self._real_device.visualize() if hasattr(self._real_device, "visualize") else str(self._real_device)
        return f"{wrapped_visual} [CacheProxy]"
