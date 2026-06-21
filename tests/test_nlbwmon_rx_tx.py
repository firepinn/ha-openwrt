"""Tests for client bandwidth detailed (Rx/Tx) sensors."""

from unittest.mock import MagicMock

from custom_components.openwrt.sensor import (
    _create_nlbwmon_sensors,
    OpenWrtNlbwmonRxSensor,
    OpenWrtNlbwmonTxSensor,
)
from custom_components.openwrt.api.base import OpenWrtData, NlbwmonTraffic


def test_nlbwmon_rx_tx_creation() -> None:
    """Test that Rx and Tx sensors are created and disabled by default."""
    coordinator = MagicMock()
    coordinator.data = OpenWrtData()
    coordinator.data.packages.nlbwmon = True

    device = MagicMock()
    device.mac = "11:22:33:44:55:66"
    device.hostname = "TestPhone"

    entry = MagicMock()
    entry.entry_id = "test_entry"

    sensors = _create_nlbwmon_sensors(coordinator, entry, device)
    
    assert len(sensors) == 2
    assert isinstance(sensors[0], OpenWrtNlbwmonRxSensor)
    assert isinstance(sensors[1], OpenWrtNlbwmonTxSensor)
    
    # Assert disabled by default
    assert sensors[0].entity_registry_enabled_default is False
    assert sensors[1].entity_registry_enabled_default is False


def test_nlbwmon_rx_tx_values() -> None:
    """Test that Rx and Tx sensors report correct values."""
    coordinator = MagicMock()
    coordinator.data = OpenWrtData()
    coordinator.data.nlbwmon_traffic = {
        "11:22:33:44:55:66": NlbwmonTraffic(
            rx_bytes=10485760,  # 10 MB
            tx_bytes=5242880,   # 5 MB
            rx_packets=1000,
            tx_packets=500,
        )
    }

    entry = MagicMock()
    entry.entry_id = "test_entry"

    rx_sensor = OpenWrtNlbwmonRxSensor(coordinator, entry, "11:22:33:44:55:66", "Test")
    tx_sensor = OpenWrtNlbwmonTxSensor(coordinator, entry, "11:22:33:44:55:66", "Test")

    assert rx_sensor.native_value == 10.0
    assert tx_sensor.native_value == 5.0
