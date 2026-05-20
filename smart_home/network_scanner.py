"""
Network scanning and device fingerprinting module.

Provides:
- Real network scanning (ARP, ping)
- Device type detection via fingerprints
- MAC address vendor lookup
- IP address and hostname resolution
"""

import re
import subprocess
import socket
import ipaddress
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DeviceInfo:
    """Discovered device information."""
    ip: str
    mac: str = "unknown"
    hostname: str = "unknown"
    device_type: str = "unknown"
    brand: str = "unknown"
    confidence: int = 0  # 0-100


class DeviceFingerprints:
    """Database of device fingerprints for type detection."""

    # MAC vendor prefixes (first 3 bytes) -> Brand
    MAC_VENDORS = {
        "00:1A:2B": "Philips",
        "00:17:88": "Nest/Google",
        "AC:DE:48": "Philips Hue",
        "5C:F3:70": "Amazon/Echo",
        "B0:C5:54": "Asus",
        "00:0C:29": "VMware",
        "08:00:27": "VirtualBox",
        "52:54:00": "QEMU",
        "90:B1:35": "Gledopto",
        "C0:06:C3": "GE",
        "DC:4F:22": "Sonos",
        "00:1F:32": "D-Link",
        "00:23:14": "Google",
        "00:25:9F": "Huawei",
        "00:26:5A": "Cisco",
        "34:CE:00": "Lutron",
        "4C:72:B9": "Netgear",
        "60:8C:A5": "TP-Link",
        "B8:27:EB": "Raspberry Pi",
    }

    # Hostname patterns -> Device type
    HOSTNAME_PATTERNS = {
        r"(?i)(camera|cam|ipcam|cctv)": ("camera", "generic"),
        r"(?i)(light|lamp|bulb|hue|philips)": ("light", "Philips"),
        r"(?i)(thermo|nest|heating|climate|ac)": ("thermostat", "Nest"),
        r"(?i)(speaker|echo|sonos|audio)": ("speaker", "Amazon"),
        r"(?i)(lock|door|yale|kevo)": ("door_lock", "Yale"),
        r"(?i)(plug|outlet|switch|socket)": ("appliance", "generic"),
        r"(?i)(tv|television|samsung|lg)": ("tv", "Samsung"),
        r"(?i)(router|gateway|access)": ("gateway", "Netgear"),
        r"(?i)(sensor|motion|temp)": ("sensor", "generic"),
    }

    # Port scanning patterns -> Device type
    PORT_PATTERNS = {
        80: "web_enabled",
        443: "https",
        22: "ssh_enabled",
        23: "telnet",
        554: "rtsp_camera",
        8080: "web_service",
        9200: "elasticsearch",
        5000: "python_app",
    }

    @staticmethod
    def detect_type_from_hostname(hostname: str) -> Tuple[str, str, int]:
        """
        Detect device type from hostname using regex patterns.
        
        Returns:
            (device_type, brand, confidence)
        """
        if not hostname or hostname == "unknown":
            return "unknown", "unknown", 0

        for pattern, (dev_type, brand) in DeviceFingerprints.HOSTNAME_PATTERNS.items():
            if re.search(pattern, hostname):
                return dev_type, brand, 85

        return "unknown", "unknown", 0

    @staticmethod
    def detect_type_from_mac(mac: str) -> Tuple[str, str, int]:
        """
        Detect brand from MAC address vendor prefix.
        
        Returns:
            (device_type, brand, confidence)
        """
        if not mac or mac == "unknown":
            return "unknown", "unknown", 0

        mac_prefix = ":".join(mac.split(":")[:3]).upper()

        for prefix, brand in DeviceFingerprints.MAC_VENDORS.items():
            if mac_prefix.startswith(prefix.upper()):
                # Simple heuristic: some brands imply device types
                if "Hue" in brand or "Philips" in brand:
                    return "light", brand, 70
                if "Echo" in brand or "Amazon" in brand:
                    return "speaker", brand, 70
                if "Nest" in brand or "Google" in brand:
                    return "thermostat", brand, 65
                return "unknown", brand, 50

        return "unknown", "unknown", 0

    @staticmethod
    def detect_type_from_ports(ports: List[int]) -> Tuple[str, str, int]:
        """
        Detect device type from open ports.
        
        Returns:
            (device_type, brand, confidence)
        """
        # RTSP port typically indicates camera
        if 554 in ports:
            return "camera", "unknown", 80

        # HTTP/HTTPS + specific port patterns
        if 80 in ports or 443 in ports or 8080 in ports:
            return "unknown", "unknown", 0

        return "unknown", "unknown", 0


class NetworkScanner:
    """Real network scanner using ARP and ping."""

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self._arp_cache: Optional[Dict[str, str]] = None

    def scan_network(self, network: str = "192.168.1.0/24") -> List[DeviceInfo]:
        """
        Scan network and detect devices.
        
        Args:
            network: CIDR notation network (e.g., "192.168.1.0/24")
        
        Returns:
            List of discovered DeviceInfo
        """
        devices = []

        try:
            # Try to parse network CIDR
            try:
                net = ipaddress.ip_network(network, strict=False)
            except ValueError:
                return []

            # Scan using ARP on Windows, arp-scan on Linux
            arp_devices = self._scan_arp(str(net))
            devices.extend(arp_devices)

            # Enhance with hostname and fingerprinting
            for device in devices:
                device.hostname = self._resolve_hostname(device.ip)
                dev_type, brand, conf = self._fingerprint_device(device)
                device.device_type = dev_type
                device.brand = brand
                device.confidence = conf

        except Exception as e:
            pass  # Silently fail if scanning not supported

        return devices

    def scan_subnet(self) -> List[DeviceInfo]:
        """
        Scan local subnet (auto-detect from default gateway).
        
        Returns:
            List of discovered DeviceInfo
        """
        try:
            # Get default gateway to determine subnet
            gateway = self._get_default_gateway()
            if gateway:
                # Assume /24 subnet
                parts = gateway.rsplit(".", 1)
                subnet = f"{parts[0]}.0/24"
                return self.scan_network(subnet)
        except Exception:
            pass

        # Fallback to common subnet
        return self.scan_network("192.168.1.0/24")

    def _get_default_gateway(self) -> Optional[str]:
        """Get default gateway IP address."""
        try:
            if Path("C:\\Windows\\System32").exists():  # Windows
                result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                for line in result.stdout.split("\n"):
                    if "Default Gateway" in line:
                        return line.split(":")[-1].strip()

            else:  # Linux/Mac
                result = subprocess.run(
                    ["ip", "route"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                for line in result.stdout.split("\n"):
                    if "default via" in line:
                        return line.split()[2]
        except Exception:
            pass

        return None

    def _scan_arp(self, network: str) -> List[DeviceInfo]:
        """
        Scan network using ARP.
        
        Returns:
            List of DeviceInfo from ARP responses
        """
        devices = []

        try:
            if Path("C:\\Windows\\System32").exists():  # Windows
                # Use Windows arp command
                result = subprocess.run(
                    ["arp", "-a"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                # Parse output: "192.168.1.100     aa-bb-cc-dd-ee-ff"
                for line in result.stdout.split("\n"):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            ip = parts[0].strip()
                            mac = parts[1].strip()
                            if self._is_valid_ip(ip) and self._is_valid_mac(mac):
                                # Normalize MAC format
                                mac = mac.replace("-", ":").upper()
                                devices.append(DeviceInfo(ip=ip, mac=mac))
                        except (ValueError, IndexError):
                            continue

            else:  # Linux
                # Try arp-scan if available
                try:
                    result = subprocess.run(
                        ["arp-scan", "--localnet"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    for line in result.stdout.split("\n"):
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            ip = parts[0].strip()
                            mac = parts[1].strip()
                            if self._is_valid_ip(ip) and self._is_valid_mac(mac):
                                devices.append(DeviceInfo(ip=ip, mac=mac))
                except FileNotFoundError:
                    # Fallback to ping scan
                    devices = self._ping_scan(network)

        except Exception:
            pass

        return devices

    def _ping_scan(self, network: str) -> List[DeviceInfo]:
        """
        Fallback: Scan network using ping.
        
        Returns:
            List of DeviceInfo from ping responses
        """
        devices = []

        try:
            net = ipaddress.ip_network(network, strict=False)

            for ip in list(net.hosts())[:50]:  # Limit to first 50 for speed
                try:
                    if Path("C:\\Windows\\System32").exists():  # Windows
                        result = subprocess.run(
                            ["ping", "-n", "1", "-w", "500", str(ip)],
                            capture_output=True,
                            timeout=1,
                        )
                    else:  # Linux/Mac
                        result = subprocess.run(
                            ["ping", "-c", "1", "-W", "500", str(ip)],
                            capture_output=True,
                            timeout=1,
                        )

                    if result.returncode == 0:
                        mac = self._get_mac_from_arp(str(ip))
                        devices.append(DeviceInfo(ip=str(ip), mac=mac or "unknown"))
                except (subprocess.TimeoutExpired, Exception):
                    continue

        except Exception:
            pass

        return devices

    def _get_mac_from_arp(self, ip: str) -> Optional[str]:
        """Get MAC address for IP using ARP."""
        try:
            if Path("C:\\Windows\\System32").exists():  # Windows
                result = subprocess.run(
                    ["arp", "-a", ip],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                for line in result.stdout.split("\n"):
                    parts = line.split()
                    if len(parts) >= 2:
                        mac = parts[1].strip()
                        if self._is_valid_mac(mac):
                            return mac.replace("-", ":").upper()
            else:  # Linux
                result = subprocess.run(
                    ["arp", ip],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                for line in result.stdout.split("\n"):
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2].upper()
        except Exception:
            pass

        return None

    def _resolve_hostname(self, ip: str) -> str:
        """Resolve IP to hostname using reverse DNS."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname.split(".")[0] if hostname else "unknown"
        except (socket.herror, socket.gaierror, OSError):
            return "unknown"

    def _fingerprint_device(self, device: DeviceInfo) -> Tuple[str, str, int]:
        """
        Determine device type using multiple fingerprints.
        
        Returns:
            (device_type, brand, confidence)
        """
        # Try hostname first (highest priority)
        dev_type, brand, conf = DeviceFingerprints.detect_type_from_hostname(device.hostname)
        if conf >= 80:
            return dev_type, brand, conf

        # Try MAC vendor lookup
        dev_type2, brand2, conf2 = DeviceFingerprints.detect_type_from_mac(device.mac)
        if conf2 > conf:
            dev_type, brand, conf = dev_type2, brand2, conf2

        return dev_type, brand, conf

    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Check if string is valid IPv4 address."""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    @staticmethod
    def _is_valid_mac(mac: str) -> bool:
        """Check if string is valid MAC address."""
        mac = mac.replace("-", ":").replace(" ", "")
        return bool(re.match(r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$", mac))


# Convenience functions
def scan_local_network() -> List[DeviceInfo]:
    """Scan local network and return discovered devices."""
    scanner = NetworkScanner()
    return scanner.scan_subnet()


def fingerprint_device(hostname: str, mac: str) -> Tuple[str, str, int]:
    """
    Get device type and brand from fingerprints.
    
    Returns:
        (device_type, brand, confidence)
    """
    dev_type, brand, conf = DeviceFingerprints.detect_type_from_hostname(hostname)
    if conf < 80:
        dev_type2, brand2, conf2 = DeviceFingerprints.detect_type_from_mac(mac)
        if conf2 > conf:
            dev_type, brand, conf = dev_type2, brand2, conf2

    return dev_type, brand, conf
