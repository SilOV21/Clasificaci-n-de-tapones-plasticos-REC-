"""Load/save HMI settings to ~/.lra_hmi.yaml (with package defaults as fallback)."""
from __future__ import annotations

import os
from typing import Optional

import yaml

from .ui.settings_dialog import HmiSettings


USER_CONFIG_PATH = os.path.expanduser("~/.lra_hmi.yaml")


def load_settings(default_yaml_path: Optional[str] = None) -> HmiSettings:
    if default_yaml_path and os.path.exists(default_yaml_path):
        data = _read_yaml(default_yaml_path)
    else:
        data = {}
    if os.path.exists(USER_CONFIG_PATH):
        user = _read_yaml(USER_CONFIG_PATH)
        data.update(user)
    return HmiSettings(
        robot_ip=str(data.get("robot_ip", "169.254.12.28")),
        ur_type=str(data.get("ur_type", "ur3e")),
        num_boxes=int(data.get("num_boxes", 4)),
    )


def save_settings(settings: HmiSettings) -> None:
    try:
        with open(USER_CONFIG_PATH, "w") as f:
            yaml.safe_dump(settings.as_dict(), f)
    except OSError:
        pass


def _read_yaml(path: str) -> dict:
    try:
        with open(path, "r") as f:
            loaded = yaml.safe_load(f) or {}
            if isinstance(loaded, dict):
                return loaded
    except (OSError, yaml.YAMLError):
        pass
    return {}
