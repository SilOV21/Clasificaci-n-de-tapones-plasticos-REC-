"""Load/save HMI settings to ~/.lra_hmi.yaml (with package defaults as fallback)."""
import os
from typing import Optional

import yaml

from .settings import HmiSettings


USER_CONFIG_PATH = os.path.expanduser("~/.lra_hmi.yaml")


def load_settings(default_yaml_path: Optional[str] = None) -> HmiSettings:
    data: dict = {}
    if default_yaml_path and os.path.exists(default_yaml_path):
        data = _read_yaml(default_yaml_path)
    if os.path.exists(USER_CONFIG_PATH):
        user = _read_yaml(USER_CONFIG_PATH)
        data = _deep_merge(data, user)
    return HmiSettings.from_dict(data)


def save_settings(settings: HmiSettings) -> None:
    try:
        with open(USER_CONFIG_PATH, "w") as f:
            yaml.safe_dump(settings.as_dict(), f, sort_keys=False)
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


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Recursively overlay `overlay` onto `base` (dict values merge, scalars replace)."""
    result = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result
