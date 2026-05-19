
```markdown
# Proyecto REC: Clasificación de Tapones Plásticos (Visión + Control UR3)

Este repositorio contiene la integración del sistema de visión artificial y control para el brazo robótico UR3 utilizando **ROS 2 Humble**.

---

## 📋 Requisitos Previos e Instalación

Para compilar y preparar el entorno en tu máquina:

```bash
# 1. Navega a la raíz de tu workspace

# 2. Compila los paquetes de visión y control
colcon build --packages-select rec_vision ur3_vision_control

# 3. Recarga el entorno de tu workspace
source install/setup.bash

```

---

## 🚀 Instrucciones de Ejecución

Sigue el orden de las terminales para arrancar el sistema completo. Recuerda hacer `source` de tu workspace en cada nueva terminal que abras.

### 🔹 Modo 2: Sistema Integrado (Launch Completo)

Para lanzar el pipeline optimizado con la cámara y calibración reales:

#### **Terminal 1: Driver del Robot & Posición de la Cámara**

```bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3 robot_ip:=169.254.12.28 launch_rviz:=false

```

*En otra pestaña de esta terminal, publica la transformación estática de la cámara respecto al robot:*

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 world base_link

```

#### **Terminal 2: Launch unificado de Visión y Control**

Lanza el archivo unificado que arranca los nodos de procesamiento de imagen y el flujo de control:

```bash
cd ~/tu_workspace_ros2
source install/setup.bash
ros2 launch ur3_vision_control launch.py

```

---

## ⚠️ Notas Importantes para el Equipo

* **Calibración de la Cámara:** El archivo `camera_info.yaml` se busca automáticamente dentro del directorio `share` generado tras hacer el `colcon build`. No modifiques a mano la variable `camera_info_yaml` en los scripts de launch.
* **IP del Robot:** Asegúrate de que el UR3 real esté encendido, configurado en modo *Remote Control* y respondiendo en la IP estática `169.254.12.28` antes de lanzar la Terminal 1.

```

```
