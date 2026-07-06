"""Tests for Snort IDS status/alert parsing."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.openwrt.api.base import OpenWrtData
from custom_components.openwrt.coordinator import OpenWrtDataCoordinator

LOG = "/var/log/alert_json.txt"
_A1 = (
    '{"timestamp":"26/07/05-11:00:00","proto":"TCP","src_addr":"1.2.3.4",'
    '"src_port":80,"dst_addr":"5.6.7.8","dst_port":1234,"sid":498,'
    '"action":"allow","msg":"FIRST ALERT"}'
)
_A2 = (
    '{"timestamp":"26/07/05-12:00:00","proto":"TCP","src_addr":"2001:db8::1",'
    '"src_port":443,"dst_addr":"2001:db8::2","dst_port":5555,"sid":499,'
    '"action":"drop","msg":"SECOND | ALERT"}'
)


def _make_exec(
    running_code=0, wc="2 " + LOG, tail=_A1 + "\n" + _A2 + "\n", installed=True
):
    async def fake_exec(command, params=None):
        if command == "/etc/init.d/snort":
            return {"code": running_code} if installed else {}
        if command == "/usr/bin/wc":
            return {"code": 0, "stdout": wc}
        if command == "/usr/bin/tail":
            return {"code": 0, "stdout": tail}
        return {}

    return fake_exec


@pytest.mark.asyncio
async def test_snort_parses_alerts():
    coord = SimpleNamespace(
        client=SimpleNamespace(file_exec=AsyncMock(side_effect=_make_exec()))
    )
    data = OpenWrtData()
    await OpenWrtDataCoordinator._async_fetch_snort_data(coord, data)
    s = data.snort_status
    assert s["installed"] is True
    assert s["running"] is True
    assert s["alert_count"] == 2
    assert len(s["recent_alerts"]) == 2
    # newest first
    assert s["recent_alerts"][0]["message"] == "SECOND | ALERT"
    assert s["last_alert"]["message"] == "SECOND | ALERT"
    # IPv6 host is bracketed
    assert s["recent_alerts"][0]["src"] == "[2001:db8::1]:443"
    assert s["recent_alerts"][0]["action"] == "drop"
    # IPv4 host is not bracketed
    assert s["recent_alerts"][1]["src"] == "1.2.3.4:80"


@pytest.mark.asyncio
async def test_snort_not_installed():
    coord = SimpleNamespace(
        client=SimpleNamespace(
            file_exec=AsyncMock(side_effect=_make_exec(installed=False))
        )
    )
    data = OpenWrtData()
    await OpenWrtDataCoordinator._async_fetch_snort_data(coord, data)
    assert data.snort_status["installed"] is False
    assert data.snort_status["alert_count"] == 0


@pytest.mark.asyncio
async def test_snort_installed_not_running_no_alerts():
    coord = SimpleNamespace(
        client=SimpleNamespace(
            file_exec=AsyncMock(
                side_effect=_make_exec(running_code=1, wc="0 " + LOG, tail="")
            )
        )
    )
    data = OpenWrtData()
    await OpenWrtDataCoordinator._async_fetch_snort_data(coord, data)
    s = data.snort_status
    assert s["installed"] is True
    assert s["running"] is False
    assert s["alert_count"] == 0
    assert s["recent_alerts"] == []
