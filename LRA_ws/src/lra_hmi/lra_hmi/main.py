"""LRA HMI entry point: starts QApplication + rclpy + main window."""
from __future__ import annotations

import os
import signal
import sys

import rclpy
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from .config_io import load_settings, save_settings
from .connection_monitor import ConnectionMonitor
from .process_manager import ProcessManager
from .ros_bridge import RosBridge
from .ui.main_window import MainWindow
from .ui.theme import apply_theme


def _default_config_path() -> str | None:
    try:
        share = get_package_share_directory("lra_hmi")
    except PackageNotFoundError:
        return None
    candidate = os.path.join(share, "config", "default_config.yaml")
    return candidate if os.path.exists(candidate) else None


def main() -> int:
    if not rclpy.ok():
        rclpy.init(args=sys.argv)

    app = QApplication(sys.argv)
    app.setApplicationName("REC HMI")
    apply_theme(app)

    settings = load_settings(_default_config_path())

    sim_mode = ProcessManager.is_sim_mode()
    if sim_mode:
        print("=" * 60)
        print("  REC HMI — modo SIMULACIÓN (LRA_HMI_SIM está activo)")
        print("  Se lanzarán nodos simulados de lra_hmi_sim.")
        print("  El LED de conexión apunta a 127.0.0.1.")
        print("=" * 60, flush=True)
        settings.robot_ip = "127.0.0.1"

    ros_bridge = RosBridge()
    process_manager = ProcessManager(settings=settings)
    connection_monitor = ConnectionMonitor(settings.robot_ip)

    window = MainWindow(
        ros_bridge=ros_bridge,
        process_manager=process_manager,
        connection_monitor=connection_monitor,
        settings=settings,
    )

    spin_timer = QTimer()
    spin_timer.setInterval(50)
    spin_timer.timeout.connect(lambda: ros_bridge.spin_once(0.0))
    spin_timer.start()

    connection_monitor.start()

    signal.signal(signal.SIGINT, lambda *_: app.quit())

    sigint_timer = QTimer()
    sigint_timer.setInterval(200)
    sigint_timer.timeout.connect(lambda: None)
    sigint_timer.start()

    window.show()

    exit_code = app.exec_()

    spin_timer.stop()
    connection_monitor.request_stop()
    connection_monitor.wait(2000)
    process_manager.shutdown()
    save_settings(settings)
    ros_bridge.shutdown()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
