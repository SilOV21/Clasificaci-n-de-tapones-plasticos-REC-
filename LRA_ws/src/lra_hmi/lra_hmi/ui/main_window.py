"""Ventana principal del HMI: barra superior con E-stop, cuerpo con pestañas, cableado de señales."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
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
from ..settings import HmiSettings
from .about_panel import AboutPanel
from .camera_panel import CameraPanel
from .counters_panel import CountersPanel
from .launcher_panel import LauncherPanel
from .log_panel import LogPanel
from .settings_panel import SettingsPanel
from .status_panel import StatusPanel
from .widgets import LedIndicator, WideTabBar


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

        self.setWindowTitle("REC · Clasificación de Tapones Plásticos")
        screen = QApplication.primaryScreen().availableGeometry()
        w = max(960, min(1320, screen.width() - 80))
        h = max(680, min(840, screen.height() - 80))
        self.resize(w, h)
        self.setMinimumSize(900, 640)

        self._build_menu()
        self._build_central()
        self._wire_signals()

        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Sistema listo.")

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        m_file = menubar.addMenu("&Archivo")
        act_quit = QAction("&Salir", self)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_help = menubar.addMenu("A&yuda")
        act_about = QAction("&Acerca de", self)
        act_about.triggered.connect(self._show_about)
        m_help.addAction(act_about)

    def _build_central(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(8, 8, 8, 8)

        outer.addLayout(self._build_top_bar())

        self._tabs = QTabWidget()
        self._tabs.setTabBar(WideTabBar())
        self._tabs.tabBar().setElideMode(Qt.ElideNone)
        outer.addWidget(self._tabs, 1)

        self._launcher_panel = LauncherPanel(self._pm)
        self._status_panel = StatusPanel()
        self._counters_panel = CountersPanel(default_boxes=self._settings.num_boxes)
        self._camera_panel_dashboard = CameraPanel(title="Vista en vivo")

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
        self._tabs.addTab(dashboard, "Panel")

        self._camera_panel_full = CameraPanel(title="Cámara (vista completa)")
        self._tabs.addTab(self._camera_panel_full, "Cámara")

        self._log_panel = LogPanel()
        self._tabs.addTab(self._log_panel, "Registros")

        self._settings_panel = SettingsPanel(self._settings)
        self._tabs.addTab(self._settings_panel, "Ajustes")

        self._about_panel = AboutPanel()
        self._tabs.addTab(self._about_panel, "Acerca de")

    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)

        title = QLabel("REC · CLASIFICACIÓN DE TAPONES")
        title.setObjectName("topBarTitle")
        bar.addWidget(title)

        bar.addStretch(1)

        ur_lbl = QLabel("UR3e:")
        ur_lbl.setObjectName("mutedLabel")
        bar.addWidget(ur_lbl)
        self._top_conn_led = LedIndicator(diameter=18)
        bar.addWidget(self._top_conn_led)
        self._top_ip_label = QLabel(self._settings.robot_ip)
        self._top_ip_label.setObjectName("ipLabel")
        bar.addWidget(self._top_ip_label)

        bar.addSpacing(20)

        self._estop_btn = QPushButton("PARADA DE EMERGENCIA")
        estop_font = QFont()
        estop_font.setBold(True)
        estop_font.setPointSize(11)
        self._estop_btn.setFont(estop_font)
        self._estop_btn.setMinimumHeight(40)
        self._estop_btn.setMinimumWidth(220)
        self._estop_btn.setObjectName("estopBtn")
        self._estop_btn.setToolTip("Detiene todos los subsistemas y desactiva la visión.")
        self._estop_btn.clicked.connect(self._on_estop)
        bar.addWidget(self._estop_btn)

        self._rehab_btn = QPushButton("REHABILITAR")
        rehab_font = QFont()
        rehab_font.setBold(True)
        rehab_font.setPointSize(11)
        self._rehab_btn.setFont(rehab_font)
        self._rehab_btn.setMinimumHeight(40)
        self._rehab_btn.setMinimumWidth(170)
        self._rehab_btn.setObjectName("rehabBtn")
        self._rehab_btn.setToolTip(
            "Reactiva la visión tras una parada de emergencia. "
            "Los subsistemas deben reiniciarse desde el lanzador."
        )
        self._rehab_btn.clicked.connect(self._on_rehab)
        bar.addWidget(self._rehab_btn)

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

        self._settings_panel.applied.connect(self._on_settings_applied)
        self._settings_panel.changed_keys.connect(self._on_settings_changed_keys)

    def _on_start_all(self) -> None:
        self.statusBar().showMessage("Iniciando todos los subsistemas…")
        self._pm.start_all()

    def _on_stop_all(self) -> None:
        self.statusBar().showMessage("Deteniendo todos los subsistemas…")
        self._pm.stop_all()

    def _on_estop(self) -> None:
        self.statusBar().showMessage("PARADA DE EMERGENCIA activada.")
        try:
            self._ros.publish_vision_enable(False)
        except Exception:
            pass
        self._pm.emergency_stop()
        self._status_panel.vision_enable_checkbox.setChecked(False)
        QMessageBox.critical(
            self,
            "Parada de Emergencia",
            "Todos los subsistemas se han detenido forzosamente.\n"
            "La visión se ha desactivado.\n\n"
            "Pulse «REHABILITAR» para reactivar la visión y reinicie los "
            "subsistemas desde el lanzador.",
        )

    def _on_rehab(self) -> None:
        self.statusBar().showMessage(
            "Sistema rehabilitado. La visión se ha reactivado.", 5000
        )
        try:
            self._ros.publish_vision_enable(True)
        except Exception:
            pass
        self._status_panel.vision_enable_checkbox.setChecked(True)

    def _on_connection_changed(self, reachable: bool, rtt_ms: float) -> None:
        self._top_conn_led.set_color("ok" if reachable else "fail")
        self._status_panel.set_connection(reachable, rtt_ms)

    def _on_settings_applied(self, new: HmiSettings) -> None:
        from ..config_io import save_settings
        self._settings = new
        self._top_ip_label.setText(new.robot_ip)
        self._pm.set_settings(new)
        self._conn.set_robot_ip(new.robot_ip)
        self._counters_panel.on_num_boxes(new.num_boxes)
        save_settings(new)

    def _on_settings_changed_keys(self, keys) -> None:
        running = [k for k in keys if self._pm.state(k).value == "running"]
        if running:
            labels = ", ".join(self._pm.label(k) for k in running if k in self._pm.keys())
            self.statusBar().showMessage(
                f"Ajustes guardados. Reinicie para aplicar: {labels}", 10000
            )
        else:
            self.statusBar().showMessage("Ajustes guardados.", 4000)

    def _show_about(self) -> None:
        self._tabs.setCurrentWidget(self._about_panel)

    def closeEvent(self, event) -> None:
        if any(self._pm.state(k).value == "running" for k in self._pm.keys()):
            answer = QMessageBox.question(
                self,
                "Salir",
                "Hay subsistemas en ejecución. ¿Detenerlos y salir?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return
        self._pm.shutdown()
        event.accept()
