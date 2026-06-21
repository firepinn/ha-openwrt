"""Tests for OPKG/APK package update entities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.update import UpdateEntityFeature
from homeassistant.exceptions import HomeAssistantError

from custom_components.openwrt.update import (
    async_setup_entry,
    OpenWrtPackageUpdateEntity,
)
from custom_components.openwrt.const import DOMAIN, DATA_COORDINATOR, DATA_CLIENT
from custom_components.openwrt.api.base import OpenWrtData


@pytest.mark.asyncio
async def test_package_update_setup_and_install(hass) -> None:
    """Test package update entity creation and installation execution."""
    data = OpenWrtData()
    data.upgradeable_packages = {"luci-mod-rpc": "1.0.1"}
    data.permissions.read_system = True

    mock_coordinator = MagicMock()
    mock_coordinator.data = data
    mock_coordinator.router_id = "router_mac"
    mock_coordinator.async_request_refresh = AsyncMock()

    mock_client = MagicMock()
    mock_client.execute_command = AsyncMock()
    mock_coordinator.client = mock_client

    hass.data = {
        DOMAIN: {
            "test_entry_id": {
                DATA_COORDINATOR: mock_coordinator,
                DATA_CLIENT: mock_client,
            }
        }
    }

    entry = MagicMock()
    entry.entry_id = "test_entry_id"

    # Verify entities are registered dynamically
    added_entities = []

    def async_add_entities(entities) -> None:
        added_entities.extend(entities)

    await async_setup_entry(hass, entry, async_add_entities)

    package_entities = [e for e in added_entities if isinstance(e, OpenWrtPackageUpdateEntity)]
    assert len(package_entities) == 1
    
    pkg_entity = package_entities[0]
    assert pkg_entity.name == "Package luci-mod-rpc"
    assert pkg_entity.entity_registry_enabled_default is False
    assert pkg_entity.supported_features == UpdateEntityFeature.INSTALL
    assert pkg_entity.latest_version == "1.0.1"

    # Verify install triggers opkg/apk install commands
    await pkg_entity.async_install(version=None, backup=False)
    
    mock_client.execute_command.assert_called_once()
    script = mock_client.execute_command.call_args[0][0]
    assert "apk add --upgrade luci-mod-rpc" in script
    assert "opkg install luci-mod-rpc" in script
    mock_coordinator.async_request_refresh.assert_called_once()
