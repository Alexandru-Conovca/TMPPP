# Structural Patterns for Smart Home System

This module contains manual, clean OOP implementations of structural design patterns integrated with the smart home system:

- **Adapter**: Integrates devices with different APIs (Zigbee, Wi-Fi, Bluetooth) into the common `Device` interface.
- **Decorator**: Dynamically extends device functionality (e.g., smart light, energy saving, temperature control).
- **Facade**: Provides a unified interface for managing the smart home (turn all on/off, security mode, scenarios).
- **Composite**: Groups devices for collective management (device groups, floors, security groups).
- **Proxy**: Controls access to devices (logging, security, caching).

All patterns are implemented in pure Python OOP style, compatible with the existing factories, HomeManager, and GUI.