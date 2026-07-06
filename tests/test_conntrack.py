"""Tests for connection-tracking (conntrack) metric collection."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.openwrt.api.base import SystemResources
from custom_components.openwrt.api.ubus import UbusClient


@pytest.fixture
def ubus_client() -> UbusClient:
    return UbusClient(
        MagicMock(),
        MagicMock(),
        host="192.168.1.1",
        username="root",
        password="password",
    )


@pytest.mark.asyncio
async def test_fetch_conntrack_populates(ubus_client: UbusClient):
    """count/max are parsed from the two /proc entries via read_file."""
    res = SystemResources()

    async def fake_read(path: str):
        if path.endswith("nf_conntrack_count"):
            return "256\n"
        if path.endswith("nf_conntrack_max"):
            return "262144\n"
        return None

    with patch.object(ubus_client, "read_file", side_effect=fake_read):
        await ubus_client._fetch_conntrack(res)

    assert res.conntrack_count == 256
    assert res.conntrack_max == 262144


@pytest.mark.asyncio
async def test_fetch_conntrack_missing_stays_zero(ubus_client: UbusClient):
    """If the reads fail/return nothing, the counters stay at 0."""
    res = SystemResources()
    with patch.object(ubus_client, "read_file", new_callable=AsyncMock) as mock_read:
        mock_read.return_value = None
        await ubus_client._fetch_conntrack(res)

    assert res.conntrack_count == 0
    assert res.conntrack_max == 0
