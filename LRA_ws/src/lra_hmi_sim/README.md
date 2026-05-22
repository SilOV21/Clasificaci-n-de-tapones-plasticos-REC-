# lra_hmi_sim

Simulation nodes and test harness for the [`lra_hmi`](../lra_hmi/) package.
Lets you verify every HMI feature without plugging in the real UR3e or
running the real vision pipeline.

## What's inside

| Node                   | What it does                                                   |
|------------------------|----------------------------------------------------------------|
| `fake_ur_driver`       | Publishes `/joint_states` with smooth sine motion (50 Hz).     |
| `fake_vision`          | Publishes counters, colors, num boxes, and synthetic images.   |
| `vision_enable_logger` | Subscribes `/vision_enable`, prints every event.               |
| `crashy_node`          | Exits non-zero after N seconds (for the "crashed" LED test).   |

## Build

```bash
cd /root/lra_ws
colcon build --packages-select lra_hmi lra_hmi_sim
source install/setup.bash
```

## Interactive simulation

Just set the env var before launching the HMI:

```bash
LRA_HMI_SIM=1 ros2 run lra_hmi main
```

When the env var is set:

- A `SIMULATION mode` banner is printed.
- The launcher rows are labeled `[SIM] UR Driver`, `[SIM] TF Publisher`,
  `[SIM] Vision & MoveIt`.
- The connection LED targets `127.0.0.1` (so it goes green immediately).
- Clicking **Start All** runs the fake nodes instead of the real hardware
  ones — no UR3e required.

### Manual verification walkthrough

After launching, click **Start All** and verify:

1. **Connection LED (top bar)** — green within ~2 s (pings 127.0.0.1).
2. **Launcher panel** — all three rows show green LEDs labeled `[SIM] …`.
3. **Counters panel** — total ticks up every ~2 s; the box card matching
   the published color (rojo→1, azul→2, amarillo→3, blanco→4) grows.
4. **Status panel**
   - Joint stream LED green; six joint angles update continuously.
   - Color swatch cycles through ROJO / AZUL / AMARILLO / BLANCO with
     matching background colors.
5. **Camera tab** — synthetic frames render at ~10 Hz. Switch the source
   selector between `/image_raw` and `/tapones/imagen_debug` to see the
   green detection overlay appear/disappear.
6. **Logs tab** — separate sub-tabs per subprocess; the `[SIM] Vision &
   MoveIt` tab contains lines from `fake_vision` and `vision_enable_logger`.
7. **Vision-enable toggle** — uncheck the *Vision enabled* checkbox in
   the Status panel → a line like `>>> /vision_enable received: data=False`
   appears in the Logs tab. Re-check → `data=True`.
8. **Restart driver only** — click `Restart` on the `[SIM] UR Driver`
   row. Only that LED cycles; counters and vision keep going. The joint
   stream LED briefly goes red, then green again.
9. **Save session report** — click **Save session report…** in the
   Counters panel; verify a JSON file is written.
10. **Emergency Stop** — click the red top-bar button. All three LEDs go
    gray within a second. A `data=False` line appears in the Logs tab.
11. **Settings persistence** — File → Settings, change *Number of boxes*
    to 6, accept; the Counters panel grid rebuilds with 6 cards.

### Crash test

To verify the "crashed" LED state and the `Restart` recovery flow:

```bash
# 1. stop everything in the GUI
# 2. set the crash timer
ros2 launch lra_hmi_sim simulation.launch.py num_boxes:=4 &
ros2 run lra_hmi_sim fake_ur_driver --ros-args -p crash_after_s:=10.0
# 3. watch the driver LED go red after 10 s; click Restart to recover
```

Or use the dedicated `crashy_node`:

```bash
ros2 run lra_hmi_sim crashy_node --ros-args -p lifetime_s:=5.0
```

## Automated smoke tests

The `test/` folder contains a [`pytest-qt`](https://pytest-qt.readthedocs.io/)
suite that drives the GUI off-screen with `QT_QPA_PLATFORM=offscreen` and
asserts widget state in response to ROS traffic.

```bash
# inside the container, after colcon build:
QT_QPA_PLATFORM=offscreen pytest src/lra_hmi_sim/test/ -v
# or:
colcon test --packages-select lra_hmi_sim --event-handlers console_direct+
colcon test-result --verbose
```

Test cases:

1. `test_window_builds` — all four panels instantiate.
2. `test_counters_react` — publishing `/tapones/caja_asignada` updates
   the total and the matching box card.
3. `test_color_swatch_reacts` — `/vision_color="rojo"` paints the swatch
   red.
4. `test_joint_stream_live_then_stale` — joints publish → LED green,
   then quiet for 2 s → LED red.
5. `test_camera_renders` — publishing an `Image` results in a non-null
   pixmap.
6. `test_state_led_follows_process_state` — driving the ProcessManager's
   internal state correctly recolors the LED.
7. `test_emergency_stop_invokes_pm_and_publishes` — clicking the red
   button calls `emergency_stop` and publishes `Bool(False)` on
   `/vision_enable`.

## Convenience launchers

Bring up every fake node in one command (without the HMI):

```bash
ros2 launch lra_hmi_sim all_sim.launch.py
# with parameters:
ros2 launch lra_hmi_sim all_sim.launch.py num_boxes:=6 driver_crash_after_s:=15.0
```
