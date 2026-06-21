# Installation

## HACS (Recommended)

This integration is fully compatible with [HACS](https://hacs.xyz/).

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=FaserF/ha-openwrt&category=integration)

> [!NOTE]
> This integration is currently a custom repository. A Pull Request to include it in the HACS default repositories is pending.

1. Open **HACS** in Home Assistant.
2. Click on the three dots in the top right corner and select **Custom repositories**.
3. Add `FaserF/ha-openwrt` with category **Integration**.
4. Search for "OpenWrt".
5. Install and restart Home Assistant.

## Manual Installation

1. Download the latest release from the [Releases page](https://github.com/FaserF/ha-openwrt/releases).
2. Extract the `custom_components/openwrt` folder into your Home Assistant's `custom_components` directory.
3. Restart Home Assistant.
