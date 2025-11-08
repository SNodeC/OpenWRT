include $(TOPDIR)/rules.mk

PKG_NAME:=mqttsuite
PKG_VERSION:=1.0.0
PKG_RELEASE:=3

# Source via git (kept your style)
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/SNodeC/mqttsuite
PKG_SOURCE_VERSION:=HEAD

PKG_MAINTAINER:=Volker Christian <me@vchrist.at>

PKG_LICENSE:=GPL-3.0-or-later
PKG_LICENSE_FILES:=LICENSE

PKG_BUILD_DEPENDS:=nlohmannjson easyloggingpp
PKG_BUILD_PARALLEL:=1

CMAKE_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

# EXTRA_CFLAGS+=-Og -g3 -fno-omit-frame-pointer
# EXTRA_CXXFLAGS+=-Og -g3 -fno-omit-frame-pointer
# PKG_BUILD_FLAGS:=no-strip

CMAKE_OPTIONS += \
  -DCONFIG_MQTTSUITE_BROKER_TCP_IPV4=$(if $(CONFIG_MQTTSUITE_BROKER_TCP_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_TLS_IPV4=$(if $(CONFIG_MQTTSUITE_BROKER_TLS_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_TCP_IPV6=$(if $(CONFIG_MQTTSUITE_BROKER_TCP_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_TLS_IPV6=$(if $(CONFIG_MQTTSUITE_BROKER_TLS_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_UNIX=$(if $(CONFIG_MQTTSUITE_BROKER_UNIX),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_UNIX_TLS=$(if $(CONFIG_MQTTSUITE_BROKER_UNIX_TLS),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_WS=$(if $(CONFIG_MQTTSUITE_BROKER_WS),ON,OFF) \
  -DCONFIG_MQTTSUITE_BROKER_WSS=$(if $(CONFIG_MQTTSUITE_BROKER_WSS),ON,OFF) \
  \
  -DCONFIG_MQTTSUITE_INTEGRATOR_TCP_IPV4=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_TCP_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_TLS_IPV4=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_TLS_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_TCP_IPV6=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_TCP_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_TLS_IPV6=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_TLS_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_UNIX=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_UNIX),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_UNIX_TLS=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_UNIX_TLS),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_WS=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_WS),ON,OFF) \
  -DCONFIG_MQTTSUITE_INTEGRATOR_WSS=$(if $(CONFIG_MQTTSUITE_INTEGRATOR_WSS),ON,OFF) \
  \
  -DCONFIG_MQTTSUITE_BRIDGE_TCP_IPV4=$(if $(CONFIG_MQTTSUITE_BRIDGE_TCP_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_TLS_IPV4=$(if $(CONFIG_MQTTSUITE_BRIDGE_TLS_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_TCP_IPV6=$(if $(CONFIG_MQTTSUITE_BRIDGE_TCP_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_TLS_IPV6=$(if $(CONFIG_MQTTSUITE_BRIDGE_TLS_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_UNIX=$(if $(CONFIG_MQTTSUITE_BRIDGE_UNIX),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_UNIX_TLS=$(if $(CONFIG_MQTTSUITE_BRIDGE_UNIX_TLS),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_WS=$(if $(CONFIG_MQTTSUITE_BRIDGE_WS),ON,OFF) \
  -DCONFIG_MQTTSUITE_BRIDGE_WSS=$(if $(CONFIG_MQTTSUITE_BRIDGE_WSS),ON,OFF) \
  \
  -DCONFIG_MQTTSUITE_CLI_TCP_IPV4=$(if $(CONFIG_MQTTSUITE_CLI_TCP_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_TLS_IPV4=$(if $(CONFIG_MQTTSUITE_CLI_TLS_IPV4),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_TCP_IPV6=$(if $(CONFIG_MQTTSUITE_CLI_TCP_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_TLS_IPV6=$(if $(CONFIG_MQTTSUITE_CLI_TLS_IPV6),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_UNIX=$(if $(CONFIG_MQTTSUITE_CLI_UNIX),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_UNIX_TLS=$(if $(CONFIG_MQTTSUITE_CLI_UNIX_TLS),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_WS=$(if $(CONFIG_MQTTSUITE_CLI_WS),ON,OFF) \
  -DCONFIG_MQTTSUITE_CLI_WSS=$(if $(CONFIG_MQTTSUITE_CLI_WSS),ON,OFF)

# ---------- Common helper: strip RPATH staging prefix ----------
define strip_staging_dir_prefix_from_rpath
    echo "Stripping $(STAGING_DIR) prefix from RPATH of executables and libraries below $(1)"; \
    find $(1) -type f -a -exec file {} \; | \
        sed -n -e 's/^\(.*\):.*ELF.*\(executable\|relocatable\|shared object\).*,.*/\1:\2/p' | \
    ( \
        IFS=":"; \
        while read F S; do \
            echo "$$$$F: $$$$S"; \
            b=$$$$(stat -c '%a' $$$$F); \
            cur_rpath="$$$$($(STAGING_DIR_HOST)/bin/patchelf --print-rpath $$$$F 2>/dev/null || true)"; \
            new_rpath=""; \
            [ -n "$$$$cur_rpath" ] || { echo "No RPATH"; continue; }; \
            echo "Current RPATH: $$$$cur_rpath"; \
            OLD_IFS="$$$$IFS"; IFS=":"; \
            for path in $$$$cur_rpath; do \
                case "$$$$path" in \
                    $(STAGING_DIR)/[^/]*) \
                        path_stripped=$$$$(echo $$$$path | sed "s|$(STAGING_DIR)||"); \
                        new_rpath="$$$${new_rpath:+$$$$new_rpath:}$$$$path_stripped"; \
                        ;; \
                    *) \
                        new_rpath="$$$${new_rpath:+$$$$new_rpath:}$$$$path"; \
                        ;; \
                esac; \
            done; \
            IFS="$$$$OLD_IFS"; \
            echo "Final RPATH: $$$$new_rpath"; \
            [ "$$$$new_rpath" = "$$$$cur_rpath" ] || $(STAGING_DIR_HOST)/bin/patchelf --set-rpath "$$$$new_rpath" $$$$F; \
            a=$$$$(stat -c '%a' $$$$F); \
            [ "$$$$a" = "$$$$b" ] || chmod $$$$b $$$$F; \
        done; \
        true; \
    ); \
    echo "Stripping done"
endef

define Package/mqttsuite/Default
  SECTION:=net
  CATEGORY:=Network
  TITLE:=MQTTSuite
  SUBMENU:=MQTTSuite
  URL:=https://github.com/SNodeC/mqttsuite
endef

# ---------- Base (virtual) ----------
define Package/mqttsuite
  $(call Package/mqttsuite/Default)
  TITLE:=A very lightweight MQTT-Integration System (virtual base)
  DEPENDS:=+libfmt
endef

define Package/mqttsuite/description
  Virtual base package for MQTTSuite. Pulls in only libfmt.
All feature packages depend on this. Ships no files.
endef

define Package/mqttsuite/config
  source "$(SOURCE)/Config.in"
endef

define Package/mqttsuite/install
	# virtual: no files
	true
endef

# ---------- mqttsuite-broker ----------
define Package/mqttsuite-broker
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT broker
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-server \
        $(if $(CONFIG_MQTTSUITE_BROKER_TCP_IPV4), \
           +snode.c-net-in-stream-legacy \
           +snode.c-http-server-express-legacy-in \
        ) \
        $(if $(CONFIG_MQTTSUITE_BROKER_TCP_IPV6), \
           +snode.c-net-in6-stream-legacy \
           +snode.c-http-server-express-legacy-in6 \
        ) \
        $(if $(CONFIG_MQTTSUITE_BROKER_TLS_IPV4), \
           +snode.c-net-in-stream-tls \
           +snode.c-http-server-express-tls-in \
        ) \
        $(if $(CONFIG_MQTTSUITE_BROKER_TLS_IPV6), \
           +snode.c-net-in6-stream-tls \
           +snode.c-http-server-express-tls-in6 \
        ) \
        $(if $(CONFIG_MQTTSUITE_BROKER_UNIX), \
           +snode.c-net-un-stream-legacy \
           +snode.c-http-server-express-legacy-un \
        ) \
        $(if $(CONFIG_MQTTSUITE_BROKER_UNIX_TLS), \
           +snode.c-net-un-stream-tls \
           +snode.c-http-server-express-tls-un \
        ) \
        $(if $(filter y, $(CONFIG_MQTTSUITE_BROKER_WS) $(CONFIG_MQTTSUITE_BROKER_WSS)), \
           +snode.c-mqtt-server-websocket \
        )
endef

define Package/mqttsuite-broker/description
  Full-featured MQTT 3.1.1 broker with optional WebSocket endpoints
and a minimal web UI under /var/www/mqttsuite/mqttbroker.
endef

define Package/mqttsuite-broker/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttbroker $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqttbroker
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-broker.so.* $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/snode.c/web/http/upgrade/websocket/mqttbroker/* $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqttbroker/
	find $(1)/usr/lib -name "*.so"  -exec rm {} ";"
	$(INSTALL_DIR) $(1)/usr/var/www/mqttsuite/mqttbroker
	$(CP) $(PKG_BUILD_DIR)/mqttbroker/html/* $(1)/usr/var/www/mqttsuite/mqttbroker/
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttbroker.init $(1)/etc/init.d/mqttbroker
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- mqttsuite-integrator ----------
define Package/mqttsuite-integrator
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT integrator
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-client \
        $(if $(filter y,$(CONFIG_MQTTSUITE_INTEGRATOR_WS) $(CONFIG_MQTTSUITE_INTEGRATOR_WSS)), \
           +snode.c-mqtt-client-websocket \
         ) \
        $(if $(CONFIG_MQTTSUITE_INTEGRATOR_TCP_IPV4), \
           +snode.c-net-in-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_INTEGRATOR_TCP_IPV6), \
           +snode.c-net-in6-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_INTEGRATOR_TLS_IPV4), \
           +snode.c-net-in-stream-tls \
         ) \
        $(if $(CONFIG_MQTTSUITE_INTEGRATOR_TLS_IPV6), \
           +snode.c-net-in6-stream-tls \
         ) \
        $(if $(CONFIG_MQTTSUITE_INTEGRATOR_UNIX), \
           +snode.c-net-un-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_INTEGRATOR_UNIX_TLS), \
           +snode.c-net-un-stream-tls \
         )
endef

define Package/mqttsuite-integrator/description
  JSON-mapping driven MQTT integrator. Includes mapping plugin libraries.
endef

define Package/mqttsuite-integrator/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttintegrator $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqttintegrator
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-integrator.so.* $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-mapping-plugin-storage.so $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-mapping-plugin-double.so $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/snode.c/web/http/upgrade/websocket/mqttintegrator/* $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqttintegrator/
	find $(1)/usr/lib -name "*.so"  -exec rm {} ";"
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttintegrator.init $(1)/etc/init.d/mqttintegrator
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- mqttsuite-bridge ----------
define Package/mqttsuite-bridge
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT bridge
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-client \
        $(if $(filter y,$(CONFIG_MQTTSUITE_BRIDGE_WS) $(CONFIG_MQTTSUITE_BRIDGE_WSS)), \
           +snode.c-mqtt-client-websocket \
         ) \
        $(if $(CONFIG_MQTTSUITE_BRIDGE_TCP_IPV4), \
           +snode.c-net-in-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_BRIDGE_TCP_IPV6), \
           +snode.c-net-in6-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_BRIDGE_TLS_IPV4), \
           +snode.c-net-in-stream-tls \
         ) \
        $(if $(CONFIG_MQTTSUITE_BRIDGE_TLS_IPV6), \
           +snode.c-net-in6-stream-tls \
         ) \
        $(if $(CONFIG_MQTTSUITE_BRIDGE_UNIX), \
           +snode.c-net-un-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_BRIDGE_UNIX_TLS), \
           +snode.c-net-un-stream-tls \
         )
endef

define Package/mqttsuite-bridge/description
  Client-side bridge connecting multiple brokers and relaying topics.
endef

define Package/mqttsuite-bridge/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttbridge $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqttbridge
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-bridge.so.* $(1)/usr/lib/ 2>/dev/null || true
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/snode.c/web/http/upgrade/websocket/mqttbridge/* $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqttbridge/
	find $(1)/usr/lib -name "*.so"  -exec rm {} ";"
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttbridge.init $(1)/etc/init.d/mqttbridge
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- mqttsuite-cli ----------
define Package/mqttsuite-cli
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT command line client
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-client \
        $(if $(filter y,$(CONFIG_MQTTSUITE_CLI_WS) $(CONFIG_MQTTSUITE_CLI_WSS)), \
           +snode.c-mqtt-client-websocket \
         ) \
        $(if $(CONFIG_MQTTSUITE_CLI_TCP_IPV4), \
           +snode.c-net-in-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_CLI_TCP_IPV6), \
           +snode.c-net-in6-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_CLI_TLS_IPV4), \
           +snode.c-net-in-stream-tls \
         ) \
        $(if $(CONFIG_MQTTSUITE_CLI_TLS_IPV6), \
           +snode.c-net-in6-stream-tls \
         ) \
        $(if $(CONFIG_MQTTSUITE_CLI_UNIX), \
           +snode.c-net-un-stream-legacy \
         ) \
        $(if $(CONFIG_MQTTSUITE_CLI_UNIX_TLS), \
           +snode.c-net-un-stream-tls \
         )
endef

define Package/mqttsuite-cli/description
  Simple command-line MQTT client (publish/subscribe) built on SNode.C.
endef

define Package/mqttsuite-cli/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttcli $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqtt
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-cli.so.* $(1)/usr/lib/ 2>/dev/null || true
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/snode.c/web/http/upgrade/websocket/mqtt/* $(1)/usr/lib/snode.c/web/http/upgrade/websocket/mqtt/
	find $(1)/usr/lib -name "*.so"  -exec rm {} ";"
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- Full (virtual) ----------
define Package/mqttsuite-full
  $(call Package/mqttsuite/Default)
  TITLE:=Virtual full package for MQTTSuite. Pulls in all MQTTSuite packages
  DEPENDS:=+mqttsuite-broker \
           +mqttsuite-integrator \
           +mqttsuite-bridge \
           +mqttsuite-cli
endef

define Package/mqttsuite-full/description
  Virtual full package for MQTTSuite. Pulls in all MQTTSuite packages.
endef

define Package/mqttsuite-full/install
	# virtual: no files
	true
endef

# ---------- eval ----------
$(eval $(call BuildPackage,mqttsuite))
$(eval $(call BuildPackage,mqttsuite-broker))
$(eval $(call BuildPackage,mqttsuite-integrator))
$(eval $(call BuildPackage,mqttsuite-bridge))
$(eval $(call BuildPackage,mqttsuite-mqtt))
$(eval $(call BuildPackage,mqttsuite-full))
