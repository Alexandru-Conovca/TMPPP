"""
Smart Home System - Main Entry Point

Modern PyQt5 GUI for comprehensive smart home management with:
- Real-time device control (lights, climate, appliances)
- Security and surveillance management
- Energy monitoring and analytics
- Automation and scheduling
- Scene activation
- Remote access and monitoring
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def launch_smart_home_gui():
    """Launch the new Smart Home Management GUI."""
    try:
        from PyQt5.QtWidgets import QApplication
        from GUI.smart_home_gui import SmartHomeGUI
        
        app = QApplication(sys.argv)
        window = SmartHomeGUI()
        window.show()
        sys.exit(app.exec_())
    except ImportError:
        print("❌ PyQt5 not installed. Install with: pip install PyQt5")
        print("\nInstalling now...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
        # Try again after installation
        launch_smart_home_gui()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def launch_legacy_gui():
    """Launch legacy patterns demo GUI."""
    try:
        from PyQt5.QtWidgets import QApplication
        from GUI.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ Error launching legacy GUI: {e}")
        sys.exit(1)


def launch_console():
    """Launch console interface."""
    try:
        from main_console import run_console
        run_console()
    except Exception as e:
        print(f"❌ Error launching console: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def show_help():
    """Show help message."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║           Smart Home System - Control Interface                ║
╚════════════════════════════════════════════════════════════════╝

Usage:
    python main.py              Launch Smart Home GUI (default)
    python main.py gui          Launch Smart Home GUI
    python main.py legacy       Launch Legacy Patterns Demo
    python main.py console      Launch Console Mode
    python main.py help         Show this help message

Smart Home GUI Features:
  • 📊 Dashboard with system overview
  • 💡 Lighting control and scheduling
  • 🌡️ Climate and HVAC management
  • 🔒 Security and surveillance
  • 🔌 Smart appliances control
  • 📡 Sensors and monitoring
  • 🎬 Scenes and automation
  • ⚙️ Scheduling and rules
  • 📈 Energy monitoring
  • 📱 Remote access simulation

Requirements:
    PyQt5 5.15+  (pip install PyQt5)

Getting Started:
    1. Run: python main.py
    2. Create and control devices
    3. Set up automation rules
    4. Monitor energy consumption
    5. Activate scenes for convenience
    """)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "gui":
            launch_smart_home_gui()
        elif mode == "legacy":
            launch_legacy_gui()
        elif mode == "console":
            launch_console()
        elif mode in ["help", "-h", "--help"]:
            show_help()
        else:
            print(f"❌ Unknown mode: {mode}\n")
            show_help()
            sys.exit(1)
    else:
        # Default to GUI
        launch_smart_home_gui()


if __name__ == "__main__":
    main()

