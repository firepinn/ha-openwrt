# Device Tracking

## Settings Explained

You can control how the integration handles network clients (PCs, phones, IoT devices). These settings help you balance detail vs. dashboard clutter.

| Option | Effect when **ON** | Effect when **OFF** |
|:--- |:--- |:--- |
| **Track network clients** | Creates individual `device_tracker` entities, signal sensors, and control switches (WoL, Internet Access) for every device. | **No individual device entities** are created. Recommended for large networks to prevent Home Assistant database bloat. |
| **Include wired devices** | Tracks every device in the ARP/Neighbor table, including wired PCs and servers. | **Only WiFi clients** are tracked. Ideal if you only care about mobile presence detection. |
| **Force Wireless MACs** | Manually flags specific MAC addresses as **wireless**. | Use this if your devices are behind a **third-party Access Point (e.g. UniFi)**. These devices often appear as "wired" to the main router, which causes them to stay "home" indefinitely due to stale ARP entries. Flagging them as wireless ensures they are correctly marked "away" when they roam off the network. |

> [!CAUTION]
> **Random MAC Limitation**: The "Ignore devices with randomized MAC addresses" option only works for the native device tracking platform. If you enable **MQTT Presence Detection**, the third-party scripts on the router will continue to report all clients, including those with randomized MACs.

> [!TIP]
> **Summary Sensors stay active!** Even if you disable "Track network clients", the **Connected Clients** and **Wireless Clients** sensors will always show the correct total count of active devices on your network.

## Other Options

- **Update Interval**: How frequently to poll data (default 30s). Adjust based on your router's performance.
- **Consider Home**: Set the grace period (in seconds) for device presence detection (prevents devices from switching to "Away" during brief sleep cycles). Default is 180s.
- **DHCP Software**:
    - `Auto-detect`: Best for most users.
    - `dnsmasq`: Uses `/tmp/dhcp.leases`.
    - `odhcpd`: Uses `ubus call dhcp ipv4leases`.
    - `none`: Disables dynamic IP/hostname resolution to save resources.
- **Enable NLBWMon Top Hosts Sensor** (default: off): When enabled, creates a sensor that ranks the top 5 bandwidth-consuming hosts using the `nlbw` CLI. Requires `nlbwmon` to be installed on the router and `file.exec` rpcd permission for `/usr/sbin/nlbw`. The integration automatically checks for availability at startup and skips entity creation if the binary is not found.
