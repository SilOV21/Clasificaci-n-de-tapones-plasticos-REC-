#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash

cd /root/lra_ws

if [ "${REC_SKIP_BUILD:-0}" != "1" ]; then
    if [ "${REC_INCREMENTAL:-0}" != "1" ]; then
        echo "▶ Limpiando build/ install/ log/ (REC_INCREMENTAL=1 para conservar)"
        rm -rf build install log
    fi
    echo "▶ Compilando workspace…"
    colcon build --symlink-install \
        --event-handlers status- console_cohesion+
fi

if [ -f /root/lra_ws/install/setup.bash ]; then
    source /root/lra_ws/install/setup.bash
else
    echo "✗ install/setup.bash no encontrado tras la compilación." >&2
    exit 1
fi

echo "✓ Workspace listo. Lanzando: $*"
exec "$@"
