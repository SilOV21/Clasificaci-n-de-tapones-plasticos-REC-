# rec_vision — Paquete de visión REC

Clasificación de tapones plásticos por color con K-Means.
Universidad Politécnica de Madrid - MUAR 2025-2026

---

## Estructura del paquete

```
rec_ws/
└── src/
    └── rec_vision/
        ├── rec_vision/
        │   ├── color_calibrator_node.py   ← NODO 1: calibra colores (una vez)
        │   ├── detector_tapones.py        ← NODO 2: detecta y clasifica tapones
        │   └── mcap_publisher.py          ← Reproductor de bag para pruebas
        ├── launch/
        │   ├── color_calibrator.launch.py
        │   └── detector_tapones.launch.py
        ├── package.xml
        ├── setup.py
        └── setup.cfg
```

---

## Instalación (primera vez)

```bash
# 1. Instalar dependencia del bag
pip install mcap-ros2-support

# 2. Añadir workspace al .bashrc (solo una vez)
echo "source ~/rec_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Compilar

```bash
cd ~/rec_ws
colcon build --packages-select rec_vision
```

---

## Lanzar en el LAB (con robot real)

Primero lanza los nodos de tu compañero (en su workspace):
```bash
ros2 launch lra_vision upload_urdf.launch.py
ros2 launch lra_vision camera_manager.launch.py
ros2 launch lra_vision camera_calibration.launch.py
ros2 launch lra_vision aruco_detector.launch.py
```

Luego tus nodos:
```bash
# Terminal 1 — Calibrador de color (lanzar UNA sola vez al inicio)
ros2 launch rec_vision color_calibrator.launch.py num_cajas:=3

# Terminal 2 — Detector de tapones (se lanza con cada tapón)
ros2 launch rec_vision detector_tapones.launch.py
```

---

## Lanzar en LOCAL (con bag de pruebas)

```bash
# Terminal 1 — Bag
python3 ~/rec_ws/src/rec_vision/rec_vision/mcap_publisher.py

# Terminal 2 — TF falso
ros2 run tf2_ros static_transform_publisher \
  --x 0.4 --y 0 --z 0.5 --yaw 0 --pitch 3.1415 --roll 0 \
  --frame-id base_link --child-frame-id camera_optical_frame

# Terminal 3 — Calibrador de color (UNA VEZ)
ros2 launch rec_vision color_calibrator.launch.py num_cajas:=3

# Terminal 4 — Detector de tapones
ros2 launch rec_vision detector_tapones.launch.py
```

---

## Topics publicados

| Topic                      | Tipo             | Descripción                        |
|---------------------------|------------------|------------------------------------|
| `/clasificador/centros_hsv` | Float32MultiArray | Centros HSV de los K grupos (latched) |
| `/clasificador/num_cajas`   | Int32            | Número de cajas definidas (latched)   |
| `/tapones/caja_asignada`    | Int32            | Caja del tapón detectado (1..N)       |
| `/ur3/target_point`         | Point            | Posición del tapón en coords robot    |
| `/tapones/cantidad`         | Int32            | Número de tapones visibles            |
| `/tapones/imagen_debug`     | Image            | Imagen con detecciones dibujadas      |
| `/clasificador/imagen_debug`| Image            | Imagen del calibrador                 |

---

## Parámetros configurables

### color_calibrator_node
- `num_cajas` (default: 3) — Número de cajas de clasificación (1-6)
- `frames_muestreo` (default: 30) — Frames a acumular para K-Means

### detector_tapones
- `frames_muestreo` (default: 30) — Frames para estabilizar posición
- `show_debug` (default: true) — Mostrar ventana OpenCV
