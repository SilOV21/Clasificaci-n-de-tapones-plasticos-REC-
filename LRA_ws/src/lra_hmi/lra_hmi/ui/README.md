# LRA HMI UI Subsystem

This subdirectory contains the PyQt5 graphical user interface implementation for the LRA UR3e cap-sorting system. The HMI provides a premium, responsive, industrial SCADA-style dashboard designed with a dark aesthetic, custom widget animations, and real-time data integration.

---

## File Structure & Component Overview

The UI is modularized into dedicated panels, each responsible for a specific domain of the application:

*   [main_window.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/main_window.py): The main window shell. Houses the top bar (E-Stop, connection status, IP address), manages the [WideTabBar](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/widgets.py#L32), and handles the wiring of Qt signals from the ROS bridge and process manager to their respective panels.
*   [launcher_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/launcher_panel.py): The subprocess management interface. Displays status LEDs for each launch/run group (driver, TF, MoveIt, camera, camera URDF, calibrator, detector, pick-sort) and provides controls for starting, stopping, or restarting individual groups, as well as global actions like "Start All" and "Stop All".
*   [status_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/status_panel.py): Displays connection status, joint angle states, and the color signature of the last sorted cap. Also includes a toggle switch to enable or disable the vision pipeline.
*   [counters_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/counters_panel.py): Implements a dynamically sizing grid of cards representing each sorting bin/box, indicating individual cap counters, a global cap counter, a calculated processing rate (caps/minute), and controls to reset or save session reports.
*   [camera_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/camera_panel.py): Handles video frames from ROS 2 image topics (`/camera/image_raw` or `/tapones/imagen_debug`), converting them from OpenCV formats to QPixmaps for real-time rendering.
*   [log_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/log_panel.py): Provides a tabbed text viewer that displays standard output and error logs from each executed subprocess group, formatted with color coding.
*   [settings_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/settings_panel.py): An interactive scrollable configuration editor mapped to ROS parameters, with options for general parameters, camera features, Hough transforms, color calibration thresholds, and pick-and-sort parameters.
*   [about_panel.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/about_panel.py): Explains the scope of the project, including references to the Laboratorio de Automática y Robótica (LRA) at the Universidad Politécnica de Madrid.
*   [theme.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/theme.py): Holds CSS/QSS styles and design tokens (colors, margins, padding, fonts) used to create the custom SCADA theme.
*   [widgets.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/widgets.py): Includes generic custom components like custom-painted [LedIndicator](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/widgets.py#L9) classes, [ColorSwatch](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/widgets.py#L112) displays, and layout templates.

---

## Design System & Style Guide

The HMI uses a unified dark theme defined inside [theme.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/theme.py) that adheres to industrial SCADA styles:

### Color Tokens

| Token | Hex Value | Application |
|---|---|---|
| `BG_BASE` | `#15171c` | Outer application workspace background |
| `BG_PANEL` | `#1b1d22` | Core component background (QGroupBox, QTabWidget pane) |
| `BG_RAISED` | `#23262d` | Button baseline background |
| `BG_INPUT` | `#11131a` | Text input, spinbox, and editable field backgrounds |
| `BORDER` | `#2c3038` | Default panel and grid borders |
| `BORDER_STRONG` | `#3a3f4a` | Prominent highlights and button borders |
| `TEXT_PRIMARY` | `#e6e6e6` | Standard labels and readouts |
| `TEXT_SECONDARY`| `#8b9098` | Helper descriptions and inactive tab labels |
| `TEXT_MUTED` | `#5a6068` | Disabled text, placeholders, and minor details |
| `ACCENT` | `#00b4ff` | Primary actions, title highlights, and active elements |
| `WARN` | `#ffb000` | Warnings, intermediate states, and highlights |
| `DANGER` | `#e84a3b` | Emergency Stop buttons and failed status LEDs |
| `OK` | `#2ecc71` | Successful states and online connection LEDs |

### Typography

*   **Primary Font:** `Inter`, `Segoe UI`, `Ubuntu`, sans-serif (size: 10pt-11pt) — chosen for clear scannability under industrial conditions.
*   **Monospace Font:** `JetBrains Mono`, `Source Code Pro`, `DejaVu Sans Mono`, monospace — applied to numeric values, joint readouts, and log terminal views.

### Custom Component Implementations

1.  **LED Indicator (`LedIndicator`):** Uses custom QPainter operations rather than raw images, creating a radial gradient glow that animates smoothly between colors (green for OK, red for FAULT, amber for WARNING, grey for OFF).
2.  **Color Swatch (`ColorSwatch`):** A custom display card that reflects the color of the last classified cap. It dynamically maps color IDs ("rojo", "azul", "verde", "amarillo", "blanco", "negro") to real RGB equivalents and displays them on screen.
3.  **Wide Tab Bar (`WideTabBar`):** Extends QTabBar to enforce a minimum width for individual tabs, providing a clean dashboard look and making it easy to interact with touchscreens.
