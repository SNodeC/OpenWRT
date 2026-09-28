# MQTTSuite package catalog

These package names apply to **OpenWrt**. Use the [OpenWrt guide](openwrt.md)
to prepare the feed and install packages with `opkg` or `apk`.

## Install packages

[Prepare the OpenWrt feed and install individual packages](openwrt.md#selective-installation).

## Related package catalogs

- [Browse the SNode.C package catalog](snodec-package-options.md)
- [Find DEB and RPM component packages](linux.md#component-packages)
- [Return to the package catalog overview](../README.md#package-catalogs)

## Packages: 9

| Package | Payload / role |
| --- | --- |
| `mqttsuite` | Empty configuration anchor |
| `mqttsuite-broker` | mqttbroker, libmqtt-broker.so.1, optional server plugin, web assets, procd service |
| `mqttsuite-integrator` | mqttintegrator, libmqtt-integrator.so.1, optional client plugin, procd service |
| `mqttsuite-bridge` | mqttbridge, libmqtt-bridge.so.1, optional client plugin, web assets, procd service |
| `mqttsuite-cli` | mqttcli, libmqtt-cli.so.1, optional client plugin |
| `mqttsuite-store` | mqttstore, libmqtt-store.so.1, optional client plugin; requires SNode.C MariaDB |
| `mqttsuite-mapping-double` | /usr/lib/libmqtt-mapping-plugin-double.so |
| `mqttsuite-mapping-storage` | /usr/lib/libmqtt-mapping-plugin-storage.so |
| `mqttsuite-full` | Meta-package: all five applications and both mapping plugins |

Application libraries also include the real `.so.1.0.1` file. Each enabled
MQTT WebSocket plugin contains its `.so.2` ABI symlink and `.so.1.0.1` real file.
