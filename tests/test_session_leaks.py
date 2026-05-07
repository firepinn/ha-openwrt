"""Tests for session management and leak prevention."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.openwrt.api.luci_rpc import LuciRpcClient
from custom_components.openwrt.api.ubus import UbusClient
from custom_components.openwrt.config_flow import OpenWrtConfigFlow


@pytest.mark.asyncio
async def test_luci_concurrent_session_creation():
    """Test that concurrent calls to LuciRpcClient._ensure_session only create one session."""
    client = LuciRpcClient(host="192.168.1.1", username="root", password="password")

    with patch(
        "aiohttp.ClientSession",
        return_value=MagicMock(spec=aiohttp.ClientSession, closed=False),
    ) as mock_session_init:
        # Simulate many concurrent calls to _ensure_session
        tasks = [client._ensure_session() for _ in range(20)]
        sessions = await asyncio.gather(*tasks)

        # Verify only one session was created despite many concurrent requests
        assert mock_session_init.call_count == 1
        assert all(s is sessions[0] for s in sessions)

        # Cleanup
        await client.disconnect()


@pytest.mark.asyncio
async def test_ubus_concurrent_session_creation():
    """Test that concurrent calls to UbusClient._ensure_session only create one session."""
    client = UbusClient(host="192.168.1.1", username="root", password="password")

    with patch(
        "aiohttp.ClientSession",
        return_value=MagicMock(spec=aiohttp.ClientSession, closed=False),
    ) as mock_session_init:
        # Simulate many concurrent calls to _ensure_session
        tasks = [client._ensure_session() for _ in range(20)]
        sessions = await asyncio.gather(*tasks)

        # Verify only one session was created despite many concurrent requests
        assert mock_session_init.call_count == 1
        assert all(s is sessions[0] for s in sessions)

        # Cleanup
        await client.disconnect()


@pytest.mark.asyncio
async def test_config_flow_test_connection_cleanup(hass):
    """Test that OpenWrtConfigFlow._test_connection always disconnects the client."""
    flow = OpenWrtConfigFlow()
    flow.hass = hass

    with patch("custom_components.openwrt.config_flow.create_client") as mock_create:
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        mock_client.connect = AsyncMock(
            side_effect=Exception("Connection test failed intentionally")
        )
        mock_client.perform_diagnostics = AsyncMock(return_value={})
        mock_create.return_value = mock_client

        # This should call perform_diagnostics and then disconnect even if connect fails
        await flow._test_connection(
            {"host": "192.168.1.1", "username": "root", "password": "password"}
        )

        # Verify disconnect was called in the finally block
        mock_client.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_config_flow_provision_cleanup(hass):
    """Test that OpenWrtConfigFlow.async_step_do_provision always disconnects the client."""
    flow = OpenWrtConfigFlow()
    flow.hass = hass
    flow._data = {"host": "192.168.1.1", "username": "root", "password": "password"}

    with patch("custom_components.openwrt.config_flow.create_client") as mock_create:
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.provision_user = AsyncMock(
            side_effect=Exception("Provisioning failed intentionally")
        )
        mock_create.return_value = mock_client

        with pytest.raises(Exception, match="Provisioning failed intentionally"):
            await flow.async_step_do_provision()

        # Verify disconnect was called in the finally block
        mock_client.disconnect.assert_called_once()
