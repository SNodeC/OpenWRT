# MQTTSuite package catalog

These package names apply to **OpenWrt**.

## Installation and build results

- [Install MQTTSuite, including repository setup](install-mqttsuite.md)
- [DEB and RPM component packages](install-mqttsuite.md#components)
- [Published versions and build results](https://github.com/SNodeC/OpenWRT/blob/packages/mqttsuite/README.md)
- [Return to the repository overview](../README.md)

## Packages: 9

| Package | Payload / role |
| --- | --- |
| `mqttsuite` | Empty configuration anchor |
| `mqttsuite-broker` | mqttbroker, libmqtt-broker.so.1, optional server plugin, web assets, procd service |
| `mqttsuite-integrator` | mqttintegrator, libmqtt-integrator.so.1, optional client plugin, procd service |
| `mqttsuite-bridge` | mqttbridge, libmqtt-bridge.so.1, optional client plugin, web assets, procd service |
| `mqttsuite-cli` | mqttcli, libmqtt-cli.so.1, optional client plugin |
| `mqttsuite-store` | mqttstore, libmqtt-store.so.1, optional client plugin; requires MariaDB support |
| `mqttsuite-mapping-double` | /usr/lib/libmqtt-mapping-plugin-double.so |
| `mqttsuite-mapping-storage` | /usr/lib/libmqtt-mapping-plugin-storage.so |
| `mqttsuite-full` | Meta-package: all five applications and both mapping plugins |

Application libraries also include the real `.so.1.0.1` file. Each enabled
MQTT WebSocket plugin contains its `.so.2` ABI symlink and `.so.1.0.1` real file.
