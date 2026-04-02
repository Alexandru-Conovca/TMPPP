from devices.device import Device


class ZigbeeDeviceAPI:

    def zigbee_on(self) -> str:
        return "Zigbee device turned ON"

    def zigbee_off(self) -> str:
        return "Zigbee device turned OFF"


class WiFiDeviceAPI:

    def wifi_enable(self) -> str:
        return "WiFi device enabled"

    def wifi_disable(self) -> str:
        return "WiFi device disabled"


class BluetoothDeviceAPI:

    def bt_connect(self) -> str:
        return "Bluetooth device connected"

    def bt_disconnect(self) -> str:
        return "Bluetooth device disconnected"


class ZigbeeAdapter(Device):

    def __init__(self, name: str, brand: str, zigbee_api: ZigbeeDeviceAPI) -> None:
        super().__init__(name=name, brand=brand)
        self._zigbee_api = zigbee_api

    def device_type(self) -> str:
        return "ZigbeeAdapter"

    def operate(self) -> str:
        return self._zigbee_api.zigbee_on()

    def disconnect(self) -> str:
        return self._zigbee_api.zigbee_off()

    def clone(self) -> "ZigbeeAdapter":
        return ZigbeeAdapter(
            name=f"{self.name} (clone)",
            brand=self.brand,
            zigbee_api=ZigbeeDeviceAPI(),
        )

    def visualize(self) -> str:
        return f"[Adapter] {self}"


class WiFiAdapter(Device):

    def __init__(self, name: str, brand: str, wifi_api: WiFiDeviceAPI) -> None:
        super().__init__(name=name, brand=brand)
        self._wifi_api = wifi_api

    def device_type(self) -> str:
        return "WiFiAdapter"

    def operate(self) -> str:
        return self._wifi_api.wifi_enable()

    def disconnect(self) -> str:
        return self._wifi_api.wifi_disable()

    def clone(self) -> "WiFiAdapter":
        return WiFiAdapter(
            name=f"{self.name} (clone)",
            brand=self.brand,
            wifi_api=WiFiDeviceAPI(),
        )

    def visualize(self) -> str:
        return f"[Adapter] {self}"


class BluetoothAdapter(Device):

    def __init__(self, name: str, brand: str, bluetooth_api: BluetoothDeviceAPI) -> None:
        super().__init__(name=name, brand=brand)
        self._bluetooth_api = bluetooth_api

    def device_type(self) -> str:
        return "BluetoothAdapter"

    def operate(self) -> str:
        return self._bluetooth_api.bt_connect()

    def disconnect(self) -> str:
        return self._bluetooth_api.bt_disconnect()

    def clone(self) -> "BluetoothAdapter":
        return BluetoothAdapter(
            name=f"{self.name} (clone)",
            brand=self.brand,
            bluetooth_api=BluetoothDeviceAPI(),
        )

    def visualize(self) -> str:
        return f"[Adapter] {self}"
