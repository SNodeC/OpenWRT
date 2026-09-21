# MQTTSuite packages and options

Package selection uses `CONFIG_PACKAGE_<name>` for every package below, with
ordinary n/m/y semantics and automatic dependency selection. Build defaults
do not replace package selectors.

## Packages: 9

| Package | Payload / role | Additional feature switches |
| --- | --- | --- |
| `mqttsuite` | Empty configuration anchor | None |
| `mqttsuite-broker` | mqttbroker, libmqtt-broker.so.1, optional server plugin, web assets, procd service | BROKER_* |
| `mqttsuite-integrator` | mqttintegrator, libmqtt-integrator.so.1, optional client plugin, procd service | INTEGRATOR_* |
| `mqttsuite-bridge` | mqttbridge, libmqtt-bridge.so.1, optional client plugin, web assets, procd service | BRIDGE_* |
| `mqttsuite-cli` | mqttcli, libmqtt-cli.so.1, optional client plugin | CLI_* |
| `mqttsuite-store` | mqttstore, libmqtt-store.so.1, optional client plugin; requires SNode.C MariaDB | STORE_* |
| `mqttsuite-mapping-double` | /usr/lib/libmqtt-mapping-plugin-double.so | None |
| `mqttsuite-mapping-storage` | /usr/lib/libmqtt-mapping-plugin-storage.so | None |
| `mqttsuite-full` | Meta-package: all five applications and both mapping plugins | Uses each application's settings |

Application libraries also include the real `.so.1.0.1` file. Each enabled
MQTT WebSocket plugin contains its `.so.2` ABI symlink and `.so.1.0.1` real file.

## MQTTSuite transport defaults

All rows have the `CONFIG_` prefix in `.config`. Enabling a row compiles that
application's endpoint support and selects the matching SNode.C packages.
WS/WSS select the appropriate client/server WebSocket MQTT modules. Both share
one application plugin; it is absent when WS is disabled.

| Config.in symbol | Default | Required options |
| --- | --- | --- |
| `MQTTSUITE_BROKER_TCP_IPV4` | `y` | None |
| `MQTTSUITE_BROKER_TLS_IPV4` | `y` | MQTTSUITE_BROKER_TCP_IPV4 |
| `MQTTSUITE_BROKER_TCP_IPV6` | `y` | None |
| `MQTTSUITE_BROKER_TLS_IPV6` | `y` | MQTTSUITE_BROKER_TCP_IPV6 |
| `MQTTSUITE_BROKER_UNIX` | `y` | None |
| `MQTTSUITE_BROKER_UNIX_TLS` | `n` | MQTTSUITE_BROKER_UNIX |
| `MQTTSUITE_BROKER_WS` | `y` | MQTTSUITE_BROKER_TCP_IPV4 or MQTTSUITE_BROKER_TCP_IPV6 or MQTTSUITE_BROKER_UNIX |
| `MQTTSUITE_BROKER_WSS` | `y` | MQTTSUITE_BROKER_WS; MQTTSUITE_BROKER_TLS_IPV4 or MQTTSUITE_BROKER_TLS_IPV6 or MQTTSUITE_BROKER_UNIX_TLS |
| `MQTTSUITE_INTEGRATOR_TCP_IPV4` | `y` | None |
| `MQTTSUITE_INTEGRATOR_TLS_IPV4` | `y` | MQTTSUITE_INTEGRATOR_TCP_IPV4 |
| `MQTTSUITE_INTEGRATOR_TCP_IPV6` | `y` | None |
| `MQTTSUITE_INTEGRATOR_TLS_IPV6` | `y` | MQTTSUITE_INTEGRATOR_TCP_IPV6 |
| `MQTTSUITE_INTEGRATOR_UNIX` | `y` | None |
| `MQTTSUITE_INTEGRATOR_UNIX_TLS` | `n` | MQTTSUITE_INTEGRATOR_UNIX |
| `MQTTSUITE_INTEGRATOR_WS` | `y` | MQTTSUITE_INTEGRATOR_TCP_IPV4 or MQTTSUITE_INTEGRATOR_TCP_IPV6 or MQTTSUITE_INTEGRATOR_UNIX |
| `MQTTSUITE_INTEGRATOR_WSS` | `y` | MQTTSUITE_INTEGRATOR_WS; MQTTSUITE_INTEGRATOR_TLS_IPV4 or MQTTSUITE_INTEGRATOR_TLS_IPV6 or MQTTSUITE_INTEGRATOR_UNIX_TLS |
| `MQTTSUITE_BRIDGE_TCP_IPV4` | `y` | None |
| `MQTTSUITE_BRIDGE_TLS_IPV4` | `y` | MQTTSUITE_BRIDGE_TCP_IPV4 |
| `MQTTSUITE_BRIDGE_TCP_IPV6` | `y` | None |
| `MQTTSUITE_BRIDGE_TLS_IPV6` | `y` | MQTTSUITE_BRIDGE_TCP_IPV6 |
| `MQTTSUITE_BRIDGE_UNIX` | `y` | None |
| `MQTTSUITE_BRIDGE_UNIX_TLS` | `n` | MQTTSUITE_BRIDGE_UNIX |
| `MQTTSUITE_BRIDGE_WS` | `y` | MQTTSUITE_BRIDGE_TCP_IPV4 or MQTTSUITE_BRIDGE_TCP_IPV6 or MQTTSUITE_BRIDGE_UNIX |
| `MQTTSUITE_BRIDGE_WSS` | `y` | MQTTSUITE_BRIDGE_WS; MQTTSUITE_BRIDGE_TLS_IPV4 or MQTTSUITE_BRIDGE_TLS_IPV6 or MQTTSUITE_BRIDGE_UNIX_TLS |
| `MQTTSUITE_CLI_TCP_IPV4` | `y` | None |
| `MQTTSUITE_CLI_TLS_IPV4` | `y` | MQTTSUITE_CLI_TCP_IPV4 |
| `MQTTSUITE_CLI_TCP_IPV6` | `y` | None |
| `MQTTSUITE_CLI_TLS_IPV6` | `y` | MQTTSUITE_CLI_TCP_IPV6 |
| `MQTTSUITE_CLI_UNIX` | `y` | None |
| `MQTTSUITE_CLI_UNIX_TLS` | `n` | MQTTSUITE_CLI_UNIX |
| `MQTTSUITE_CLI_WS` | `y` | MQTTSUITE_CLI_TCP_IPV4 or MQTTSUITE_CLI_TCP_IPV6 or MQTTSUITE_CLI_UNIX |
| `MQTTSUITE_CLI_WSS` | `y` | MQTTSUITE_CLI_WS; MQTTSUITE_CLI_TLS_IPV4 or MQTTSUITE_CLI_TLS_IPV6 or MQTTSUITE_CLI_UNIX_TLS |
| `MQTTSUITE_STORE_TCP_IPV4` | `y` | None |
| `MQTTSUITE_STORE_TLS_IPV4` | `y` | MQTTSUITE_STORE_TCP_IPV4 |
| `MQTTSUITE_STORE_TCP_IPV6` | `y` | None |
| `MQTTSUITE_STORE_TLS_IPV6` | `y` | MQTTSUITE_STORE_TCP_IPV6 |
| `MQTTSUITE_STORE_UNIX` | `y` | None |
| `MQTTSUITE_STORE_UNIX_TLS` | `n` | MQTTSUITE_STORE_UNIX |
| `MQTTSUITE_STORE_WS` | `y` | MQTTSUITE_STORE_TCP_IPV4 or MQTTSUITE_STORE_TCP_IPV6 or MQTTSUITE_STORE_UNIX |
| `MQTTSUITE_STORE_WSS` | `y` | MQTTSUITE_STORE_WS; MQTTSUITE_STORE_TLS_IPV4 or MQTTSUITE_STORE_TLS_IPV6 or MQTTSUITE_STORE_UNIX_TLS |

The IPv4 TCP switch is mandatory when both IPv6 TCP and Unix sockets are off.
Integrator and bridge have upstream unconditional IPv4 HTTP and HTTPS admin
servers, so disabling MQTT TLS does not remove their admin TLS dependency.

All 40 transport symbols and the five application selectors participate in
recipe reconfiguration. Mapping plugin selectors govern separate package
emission. SNode.C is a build/runtime dependency, maintained on its own branch.

## Regression tests

This branch owns `tests/mqttsuite/package_config.json` and `tests/test_rpath.py`.
Use the shared configuration runner from a `main` checkout against an SDK
whose generated package configuration includes this branch's recipe and its
SNode.C dependency:

```sh
python3 /path/to/main/tests/test_package_config.py "$SDK" tests/mqttsuite/package_config.json
python3 tests/test_rpath.py "$SDK/staging_dir/host/bin/patchelf"
```

The configuration runner leaves the SDK's active `.config` unchanged. SNode.C
can be supplied as a separate feed or checkout; its recipe does not need to
be copied onto this branch.
