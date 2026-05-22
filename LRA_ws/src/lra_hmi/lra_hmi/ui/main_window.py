"""Main window: top bar with E-stop, tabbed body, wiring of all signals."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..connection_monitor import ConnectionMonitor
from ..process_manager import ProcessManager
from ..ros_bridge import RosBridge
from .camera_panel import CameraPanel
from .counters_panel import CountersPanel
from .launcher_panel import LauncherPanel
from .log_panel import LogPanel
from .settings_dialog import HmiSettings, SettingsDialog
from .status_panel import StatusPanel
from .widgets import LedIndicator


class MainWindow(QMainWindow):

    def __init__(
        self,
        ros_bridge: RosBridge,
        process_manager: ProcessManager,
        connection_monitor: ConnectionMonitor,
        settings: HmiSettings,
    ):
        super().__init__()
        self._ros = ros_bridge
        self._pm = process_manager
        self._conn = connection_monitor
        self._settings = settings

        self.setWindowTitle("LRA HMI — UR3e Bottle Cap Sorter")
        self.resize(1280, 820)

        self._build_menu()
        self._build_central()
        self._wire_signals()

        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready.")

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        m_file = menubar.addMenu("&File")
        act_settings = QAction("&Settings…", self)
        act_settings.triggered.connect(self._open_settings)
        m_file.addAction(act_settings)
        m_file.addSeparator()
        act_quit = QAction("&Quit", self)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_help = menubar.addMenu("&Help")
        act_about = QAction("&About", self)
        act_about.triggered.connect(self._show_about)
        m_help.addAction(act_about)

    def _build_central(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(8, 8, 8, 8)

        outer.addLayout(self._build_top_bar())

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, 1)

        self._launcher_panel = LauncherPanel(self._pm)
        self._status_panel = StatusPanel()
        self._counters_panel = CountersPanel(default_boxes=self._settings.num_boxes)
        self._camera_panel_dashboard = CameraPanel(title="Live view")

        dashboard = QWidget()
        dash_layout = QHBoxLayout(dashboard)
        left = QVBoxLayout()
        left.addWidget(self._launcher_panel)
        left.addWidget(self._counters_panel)
        right = QVBoxLayout()
        right.addWidget(self._status_panel)
        right.addWidget(self._camera_panel_dashboard, 1)
        dash_layout.addLayout(left, 1)
        dash_layout.addLayout(right, 1)
        self._tabs.addTab(dashboard, "Dashboard")

        self._camera_panel_full = CameraPanel(title="Camera (full)")
        self._tabs.addTab(self._camera_panel_full, "Camera")

        self._log_panel = LogPanel()
        self._tabs.addTab(self._log_panel, "Logs")

    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()

        title = QLabel("LRA — UR3e Bottle Cap Sorter")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        bar.addWidget(title)

        bar.addStretch(1)

        bar.addWidget(QLabel("UR3e:"))
        self._top_conn_led = LedIndicator(diameter=18)
        bar.addWidget(self._top_conn_led)
        self._top_ip_label = QLabel(self._settings.robot_ip)
        self._top_ip_label.setStyleSheet("color:#444; font-family:monospace;")
        bar.addWidget(self._top_ip_label)

        bar.addSpacing(20)

        self._estop_btn = QPushButton("EMERGENCY  STOP")
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self._estop_btn.setFont(font)
        self._estop_btn.setMinimumHeight(40)
        self._estop_btn.setMinimumWidth(200)
        self._estop_btn.setStyleSheet(
            "QPushButton { background:#c0392b; color:white; border:2px solid #7d241a; "
            "border-radius:6px; }"
            "QPushButton:hover { background:#e74c3c; }"
            "QPushButton:pressed { background:#922b21; }"
        )
        self._estop_btn.clicked.connect(self._on_estop)
        bar.addWidget(self._estop_btn)

        return bar

    def _wire_signals(self) -> None:
        self._pm.state_changed.connect(self._launcher_panel.on_state_changed)
        self._pm.log_line.connect(self._log_panel.append)
        self._launcher_panel.start_all_clicked.connect(self._on_start_all)
        self._launcher_panel.stop_all_clicked.connect(self._on_stop_all)

        self._conn.status_changed.connect(self._on_connection_changed)

        self._ros.total_caps_changed.connect(self._counters_panel.on_total_caps)
        self._ros.box_assigned.connect(self._counters_panel.on_box_assigned)
        self._ros.num_boxes_changed.connect(self._counters_panel.on_num_boxes)
        self._ros.color_changed.connect(self._status_panel.set_color)
        self._ros.joint_states_changed.connect(self._status_panel.set_joint_angles)
        self._ros.joint_states_stale.connect(self._status_panel.set_joint_stream_stale)
        self._ros.image_raw_received.connect(self._camera_panel_dashboard.on_image_raw)
        self._ros.image_raw_received.connect(self._camera_panel_full.on_image_raw)
        self._ros.image_debug_received.connect(self._camera_panel_dashboard.on_image_debug)
        self._ros.image_debug_received.connect(self._camera_panel_full.on_image_debug)
        self._ros.log_message.connect(self._log_panel.append)

        self._status_panel.vision_enable_checkbox.toggled.connect(
            self._ros.publish_vision_enable
        )

    def _on_start_all(self) -> None:
        self.statusBar().showMessage("Starting all subsystems…")
        self._pm.start_all()

    def _on_stop_all(self) -> None:
        self.statusBar().showMessage("Stopping all subsystems…")
        self._pm.stop_all()

    def _on_estop(self) -> None:
        self.statusBar().showMessage("EMERGENCY STOP triggered.")
        try:
            self._ros.publish_vision_enable(False)
        except Exception:
            pass
        self._pm.emergency_stop()
        QMessageBox.critical(
            self,
            "Emergency Stop",
            "All subsystems were force-killed.\nVision was disabled.",
        )

    def _on_connection_changed(self, reachable: bool, rtt_ms: float) -> None:
        self._top_conn_led.set_color("ok" if reachable else "fail")
        self._status_panel.set_connection(reachable, rtt_ms)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec_() == SettingsDialog.Accepted:
            new = dlg.result_settings()
            if new is None:
                return
            ip_changed = new.robot_ip != self._settings.robot_ip
            ur_changed = new.ur_type != self._settings.ur_type
            boxes_changed = new.num_boxes != self._settings.num_boxes
            self._settings = new
            self._top_ip_label.setText(new.robot_ip)
            self._pm.set_robot_ip(new.robot_ip)
            self._pm.set_ur_type(new.ur_type)
            self._conn.set_robot_ip(new.robot_ip)
            if boxes_changed:
                self._counters_panel.on_num_boxes(new.num_boxes)
            note = []
            if ip_changed or ur_changed:
                note.append("Restart the UR Driver to apply IP/type changes.")
            if note:
                self.statusBar().showMessage(" ".join(note), 6000)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About LRA HMI",
            "<b>LRA HMI</b><br>"
            "Graphical launcher &amp; monitor for the UR3e bottle-cap sorter.<br><br>"
            "ROS 2 Humble · PyQt5",
        )

    def closeEvent(self, event) -> None:
        if any(self._pm.state(k).value == "running" for k in self._pm.keys()):
            answer = QMessageBox.question(
                self,
                "Quit",
                "Subsystems are still running. Stop them and quit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return
        self._pm.shutdown()
        event.accept()
