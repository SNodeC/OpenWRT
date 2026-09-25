# SNode.C packages and options

Package selection uses `CONFIG_PACKAGE_<name>` for every package below, with
ordinary n/m/y semantics and automatic dependency selection. Build defaults
do not replace package selectors.

## Packages: 67

| Package | Payload / role |
| --- | --- |
| `snode.c` | Configuration directory, account/group registration |
| `snode.c-full` | Meta-package: all 63 runtime modules |
| `snode.c-apps` | Demonstration executables and two echo WebSocket plugins |
| `snode.c-control` | `/usr/bin/snodec-control` (CLI) |
| `snode.c-logger` | `/usr/lib/libsnodec-logger.so.2` + `.so.2.0.0` |
| `snode.c-utils` | `/usr/lib/libsnodec-utils.so.2` + `.so.2.0.0` |
| `snode.c-core-mux-epoll` | `/usr/lib/libsnodec-core-mux-epoll.so.2` + `.so.2.0.0` |
| `snode.c-core-mux-poll` | `/usr/lib/libsnodec-core-mux-poll.so.2` + `.so.2.0.0` |
| `snode.c-core-mux-select` | `/usr/lib/libsnodec-core-mux-select.so.2` + `.so.2.0.0` |
| `snode.c-core` | `/usr/lib/libsnodec-core.so.2` + `.so.2.0.0` |
| `snode.c-core-socket` | `/usr/lib/libsnodec-core-socket.so.2` + `.so.2.0.0` |
| `snode.c-core-socket-stream` | `/usr/lib/libsnodec-core-socket-stream.so.2` + `.so.2.0.0` |
| `snode.c-core-socket-stream-legacy` | `/usr/lib/libsnodec-core-socket-stream-legacy.so.2` + `.so.2.0.0` |
| `snode.c-core-socket-stream-tls` | `/usr/lib/libsnodec-core-socket-stream-tls.so.2` + `.so.2.0.0` |
| `snode.c-db-mariadb` | `/usr/lib/libsnodec-db-mariadb.so.2` + `.so.2.0.0` |
| `snode.c-net` | `/usr/lib/libsnodec-net.so.2` + `.so.2.0.0` |
| `snode.c-net-in` | `/usr/lib/libsnodec-net-in.so.2` + `.so.2.0.0` |
| `snode.c-net-in-phy` | `/usr/lib/libsnodec-net-in-phy.so.2` + `.so.2.0.0` |
| `snode.c-net-in-phy-stream` | `/usr/lib/libsnodec-net-in-phy-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-in-stream` | `/usr/lib/libsnodec-net-in-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-in-stream-legacy` | `/usr/lib/libsnodec-net-in-stream-legacy.so.2` + `.so.2.0.0` |
| `snode.c-net-in-stream-tls` | `/usr/lib/libsnodec-net-in-stream-tls.so.2` + `.so.2.0.0` |
| `snode.c-net-in6` | `/usr/lib/libsnodec-net-in6.so.2` + `.so.2.0.0` |
| `snode.c-net-in6-phy` | `/usr/lib/libsnodec-net-in6-phy.so.2` + `.so.2.0.0` |
| `snode.c-net-in6-phy-stream` | `/usr/lib/libsnodec-net-in6-phy-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-in6-stream` | `/usr/lib/libsnodec-net-in6-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-in6-stream-legacy` | `/usr/lib/libsnodec-net-in6-stream-legacy.so.2` + `.so.2.0.0` |
| `snode.c-net-in6-stream-tls` | `/usr/lib/libsnodec-net-in6-stream-tls.so.2` + `.so.2.0.0` |
| `snode.c-net-l2` | `/usr/lib/libsnodec-net-l2.so.2` + `.so.2.0.0` |
| `snode.c-net-l2-phy` | `/usr/lib/libsnodec-net-l2-phy.so.2` + `.so.2.0.0` |
| `snode.c-net-l2-phy-stream` | `/usr/lib/libsnodec-net-l2-phy-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-l2-stream` | `/usr/lib/libsnodec-net-l2-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-l2-stream-legacy` | `/usr/lib/libsnodec-net-l2-stream-legacy.so.2` + `.so.2.0.0` |
| `snode.c-net-l2-stream-tls` | `/usr/lib/libsnodec-net-l2-stream-tls.so.2` + `.so.2.0.0` |
| `snode.c-net-rc` | `/usr/lib/libsnodec-net-rc.so.2` + `.so.2.0.0` |
| `snode.c-net-rc-phy` | `/usr/lib/libsnodec-net-rc-phy.so.2` + `.so.2.0.0` |
| `snode.c-net-rc-phy-stream` | `/usr/lib/libsnodec-net-rc-phy-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-rc-stream` | `/usr/lib/libsnodec-net-rc-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-rc-stream-legacy` | `/usr/lib/libsnodec-net-rc-stream-legacy.so.2` + `.so.2.0.0` |
| `snode.c-net-rc-stream-tls` | `/usr/lib/libsnodec-net-rc-stream-tls.so.2` + `.so.2.0.0` |
| `snode.c-net-un` | `/usr/lib/libsnodec-net-un.so.2` + `.so.2.0.0` |
| `snode.c-net-un-phy` | `/usr/lib/libsnodec-net-un-phy.so.2` + `.so.2.0.0` |
| `snode.c-net-un-phy-stream` | `/usr/lib/libsnodec-net-un-phy-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-un-stream` | `/usr/lib/libsnodec-net-un-stream.so.2` + `.so.2.0.0` |
| `snode.c-net-un-stream-legacy` | `/usr/lib/libsnodec-net-un-stream-legacy.so.2` + `.so.2.0.0` |
| `snode.c-net-un-stream-tls` | `/usr/lib/libsnodec-net-un-stream-tls.so.2` + `.so.2.0.0` |
| `snode.c-net-un-dgram` | `/usr/lib/libsnodec-net-un-dgram.so.2` + `.so.2.0.0` |
| `snode.c-http` | `/usr/lib/snode.c/web/http/libsnodec-http.so.2` + `.so.2.0.0` |
| `snode.c-http-server` | `/usr/lib/snode.c/web/http/libsnodec-http-server.so.2` + `.so.2.0.0` |
| `snode.c-http-client` | `/usr/lib/snode.c/web/http/libsnodec-http-client.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-legacy-in` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-legacy-in.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-legacy-in6` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-legacy-in6.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-legacy-rc` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-legacy-rc.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-legacy-un` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-legacy-un.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-tls-in` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-tls-in.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-tls-in6` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-tls-in6.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-tls-rc` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-tls-rc.so.2` + `.so.2.0.0` |
| `snode.c-http-server-express-tls-un` | `/usr/lib/snode.c/web/http/libsnodec-http-server-express-tls-un.so.2` + `.so.2.0.0` |
| `snode.c-websocket` | `/usr/lib/snode.c/web/http/upgrade/libsnodec-websocket.so.2` + `.so.2.0.0` |
| `snode.c-websocket-server` | `/usr/lib/snode.c/web/http/upgrade/libsnodec-websocket-server.so.2` + `.so.2.0.0` |
| `snode.c-websocket-client` | `/usr/lib/snode.c/web/http/upgrade/libsnodec-websocket-client.so.2` + `.so.2.0.0` |
| `snode.c-mqtt` | `/usr/lib/snode.c/iot/mqtt/libsnodec-mqtt.so.2` + `.so.2.0.0` |
| `snode.c-mqtt-server` | `/usr/lib/snode.c/iot/mqtt/libsnodec-mqtt-server.so.2` + `.so.2.0.0` |
| `snode.c-mqtt-client` | `/usr/lib/snode.c/iot/mqtt/libsnodec-mqtt-client.so.2` + `.so.2.0.0` |
| `snode.c-mqtt-server-websocket` | `/usr/lib/snode.c/iot/mqtt/libsnodec-mqtt-server-websocket.so.2` + `.so.2.0.0` |
| `snode.c-mqtt-client-websocket` | `/usr/lib/snode.c/iot/mqtt/libsnodec-mqtt-client-websocket.so.2` + `.so.2.0.0` |

The `net-l2-*` rows are L2CAP; the `net-rc-*` rows are RFCOMM. Selecting their
upper layers selects their own lower layers and BlueZ automatically. Express
supports RFCOMM; upstream does not provide an Express/L2CAP module to package.

## SNode.C build defaults

Every symbol below has the `CONFIG_` prefix in `.config`. Defaults shown are
menu defaults. A choice uses exactly one of its alternative symbols. Values
are passed into the existing upstream CMake settings; they are runtime defaults
that the application's existing configuration system can override.

| Config.in symbol | Meaning | Default |
| --- | --- | --- |
| `SNODEC_GROUP_NAME` | Group name of unix group used for config/log/pid file management | `snodec` |
| `SNODEC_EPOLL` | epoll | `selected` |
| `SNODEC_POLL` | poll | `not selected` |
| `SNODEC_SELECT` | select | `not selected` |
| `SNODEC_READ_BLOCKSIZE` | Read block size in bytes | `16384` |
| `SNODEC_WRITE_BLOCKSIZE` | Write block size in bytes | `16384` |
| `SNODEC_READ_TIMEOUT` | Read inactivity timeout in seconds | `60` |
| `SNODEC_WRITE_TIMEOUT` | Write inactivity timeout in seconds | `60` |
| `SNODEC_MAXIMUM_WRITE_QUEUE_BYTES` | Maximum queued write bytes (0 = unlimited) | `0` |
| `SNODEC_WRITE_QUEUE_HIGH_WATERMARK` | Pipe write queue high watermark (0 = automatic) | `0` |
| `SNODEC_WRITE_QUEUE_LOW_WATERMARK` | Pipe write queue low watermark | `0` |
| `SNODEC_BACKLOG` | Listen backlog | `5` |
| `SNODEC_ACCEPTS_PER_TICK` | Accepts per tick | `1` |
| `SNODEC_ACCEPT_TIMEOUT` | Accept inactivity timeout in seconds | `0` |
| `SNODEC_CONNECT_TIMEOUT` | Connect timeout in seconds | `10` |
| `SNODEC_TERMINATE_TIMEOUT` | Shutdown timeout in seconds | `1` |
| `SNODEC_RECONNECT` | Reconnect after disconnect | `n` |
| `SNODEC_RECONNECT_TIME` | Reconnect time in seconds | `1` |
| `SNODEC_RETRY` | Retry listen and connect | `n` |
| `SNODEC_RETRY_ON_FATAL` | Retry also on fatal error | `n` |
| `SNODEC_RETRY_TIMEOUT` | Retry interval in seconds | `1` |
| `SNODEC_RETRY_TRIES` | Upper limit of retry tries | `0` |
| `SNODEC_RETRY_BASE` | Base of exponential increase | `"1.8"` |
| `SNODEC_RETRY_JITTER` | Jitter of retry timeout in percent | `0` |
| `SNODEC_RETRY_LIMIT` | Upper limit of retry timeout in seconds | `0` |
| `SNODEC_INV4_REUSE_ADDRESS` | Reuse address | `n` |
| `SNODEC_INV4_REUSE_PORT` | Reuse port | `n` |
| `SNODEC_INV4_DISABLE_NAGLE_ALGORITHM_TRUE` | true | `not selected` |
| `SNODEC_INV4_DISABLE_NAGLE_ALGORITHM_FALSE` | false | `not selected` |
| `SNODEC_INV4_DISABLE_NAGLE_ALGORITHM_DEFAULT` | default | `selected` |
| `SNODEC_IPV4_NUMERIC` | Accept numeric IPv4 hostnames only | `n` |
| `SNODEC_IPV4_NUMERIC_REVERSE` | Numeric IPv4 reverse lookup | `n` |
| `SNODEC_IN6_REUSE_ADDRESS` | Reuse address | `n` |
| `SNODEC_IN6_REUSE_PORT` | Reuse port | `n` |
| `SNODEC_INV6_DISABLE_NAGLE_ALGORITHM_TRUE` | true | `not selected` |
| `SNODEC_INV6_DISABLE_NAGLE_ALGORITHM_FALSE` | false | `not selected` |
| `SNODEC_INV6_DISABLE_NAGLE_ALGORITHM_DEFAULT` | default | `selected` |
| `SNODEC_IPV6_ONLY` | IPv6 only | `n` |
| `SNODEC_IPV4_MAPPED` | IPv4-mapped IPv6 addresses | `n` |
| `SNODEC_IPV6_NUMERIC` | Accept numeric IPv6 hostnames only | `n` |
| `SNODEC_IPV6_NUMERIC_REVERSE` | Numeric IPv6 reverse lookup | `n` |
| `SNODEC_TLS_INIT_TIMEOUT` | SSL/TLS initial handshake timeout in seconds | `10` |
| `SNODEC_TLS_SHUTDOWN_TIMEOUT` | SSL/TLS teardown timeout in seconds | `2` |
| `SNODEC_HTTP_REQUEST_PIPELINED` | Pipelined requests | `y` |

Read/write sizes, timeouts, retry/reconnect settings and write-queue limits
configure `snode.c-net`. IPv4/IPv6 stream flags configure their stream layers;
name-resolution flags configure their address layers. TLS defaults are shared
by TLS endpoints. HTTP pipelining configures the HTTP client. The I/O choice
controls the core's linked default multiplexer and its package dependency;
selecting extra multiplexer packages does not change that default.

All 44 SNode.C default/choice symbols and the demo selector participate in
recipe reconfiguration. Other module selectors govern package emission and
dependency closure; they do not prune the shared library compilation pass.

## Configuration regression tests

This branch owns `tests/snodec/package_config.json`. Use the shared runner
from a `main` checkout against an SDK whose generated package configuration
includes this branch's recipe and dependencies:

```sh
python3 /path/to/main/tests/test_package_config.py "$SDK" tests/snodec/package_config.json
```

The runner leaves the SDK's active `.config` unchanged. It can test this branch
before it is merged into `main`.
