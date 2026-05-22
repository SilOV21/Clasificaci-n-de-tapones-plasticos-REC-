# lra_hmi

PyQt5 graphical HMI and launcher for the UR3e bottle-cap sorting system.
It replaces the manual three-terminal launch flow with a single window that
starts, stops, restarts and monitors the entire pipeline.

## Features

- **One-click "Start All"** that launches the UR driver, the static TF
  publisher, and the vision/MoveIt stack in the correct order.
- **Per-subsystem control**: each of the three command groups has its own
  Start / Stop / Restart buttons and a colored status LED.
- **Emergency Stop** button in the top bar that force-kills every subprocess
  and disables vision via `/vision_enable`.
- **Live connection LED** for the UR3e (pings every 2 s).
- **Per-box and total counters** driven by `/tapones/caja_asignada` and
  `/tapones/cantidad`, with caps-per-minute rate and JSON session export.
- **Joint angle readout** from `/joint_states`, with a stale-stream warning
  if the driver stops publishing.
- **Live camera view** for both `/image_raw` and `/tapones/imagen_debug`
  (with a source selector).
- **Last-color badge** that shows the latest `/vision_color`.
- **Vision enable/disable** toggle that publishes to `/vision_enable`.
- **Tabbed log viewer** that captures each subprocess's stdout / stderr.
- **Settings dialog** for robot IP, UR type and number of boxes (persisted
  to `~/.lra_hmi.yaml`).

## Topics

Subscribed (read-only):

| Topic                       | Type                | Purpose                |
|-----------------------------|---------------------|------------------------|
| `/tapones/cantidad`         | `std_msgs/Int32`    | Total caps detected    |
| `/tapones/caja_asignada`    | `std_msgs/Int32`    | Latest box assignment  |
| `/clasificador/num_cajas`   | `std_msgs/Int32`    | Configured box count   |
| `/vision_color`             | `std_msgs/String`   | Last detected color    |
| `/joint_states`             | `sensor_msgs/JointState` | Robot joints      |
| `/image_raw`                | `sensor_msgs/Image` | Raw camera             |
| `/tapones/imagen_debug`     | `sensor_msgs/Image` | Detector overlay       |

Published:

| Topic             | Type             | Purpose                                |
|-------------------|------------------|----------------------------------------|
| `/vision_enable`  | `std_msgs/Bool`  | Vision toggle / E-stop hard disable    |

## Build

Inside the container:

```bash
cd /root/lra_ws
colcon build --packages-select lra_hmi
source install/setup.bash
```

## Run

```bash
ros2 run lra_hmi main
# or
ros2 launch lra_hmi hmi.launch.py
```

## X11 forwarding

The `docker-compose.yml` already mounts `/tmp/.X11-unix` and passes the
host `DISPLAY` variable. From the host, allow the container before
starting:

```bash
xhost +local:docker
docker compose up
```

If the window does not appear, verify `echo $DISPLAY` is set inside the
container.

## How the launcher works

`process_manager.py` spawns each command with `subprocess.Popen(...,
preexec_fn=os.setsid)`, so killing the process group with `os.killpg`
cleanly terminates the launched node and any children. `Stop` sends
`SIGTERM` and escalates to `SIGKILL` after 5 s; the E-stop button sends
`SIGKILL` immediately and publishes `Bool(False)` to `/vision_enable`.

## Configuration

Defaults live in `share/lra_hmi/config/default_config.yaml`. User overrides
are persisted to `~/.lra_hmi.yaml` whenever the Settings dialog is
accepted, and applied to:

- the UR driver subprocess argv (`robot_ip:=`, `ur_type:=`)
- the `ConnectionMonitor` ping target
- the number of cards in the counters grid
