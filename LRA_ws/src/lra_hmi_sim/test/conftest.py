"""Shared fixtures for the HMI smoke tests."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import rclpy


@pytest.fixture(scope="session")
def rclpy_session():
    if not rclpy.ok():
        rclpy.init()
    yield
    if rclpy.ok():
        rclpy.shutdown()
