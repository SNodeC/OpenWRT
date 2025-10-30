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

EXTRA_CFLAGS+=-Og -g3 -fno-omit-frame-pointer
EXTRA_CXXFLAGS+=-Og -g3 -fno-omit-frame-pointer
PKG_BUILD_FLAGS:=no-strip

define Package/mqttsuite/Default
  SECTION:=net
  CATEGORY:=Network
  TITLE:=MQTTSuite
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

define Package/mqttsuite/install
	# virtual: no files
	true
endef

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
	)
	echo "Stripping done"
endef

# ---------- mqttsuite-mqttbroker ----------
define Package/mqttsuite-mqttbroker
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT broker
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-server-websocket \
           +snode.c-http-server-express-legacy-in \
           +snode.c-http-server-express-legacy-in6 \
           +snode.c-http-server-express-legacy-un \
           +snode.c-http-server-express-tls-in \
           +snode.c-http-server-express-tls-in6 \
           +snode.c-http-server-express-tls-un \
           +snode.c-net-in-stream-legacy \
           +snode.c-net-in6-stream-legacy \
           +snode.c-net-in-stream-tls \
           +snode.c-net-in6-stream-tls \
           +snode.c-net-un-stream-legacy \
           +snode.c-net-un-stream-tls
endef

define Package/mqttsuite-mqttbroker/description
  Full-featured MQTT 3.1.1 broker with optional WebSocket endpoints
  and a minimal web UI under /var/www/mqttsuite/mqttbroker.
endef

define Package/mqttsuite-mqttbroker/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttbroker $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-broker.so.* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/var/www/mqttsuite/mqttbroker
	$(CP) $(PKG_BUILD_DIR)/mqttbroker/html/* $(1)/usr/var/www/mqttsuite/mqttbroker/
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttbroker.init $(1)/etc/init.d/mqttbroker
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- mqttsuite-mqttintegrator ----------
define Package/mqttsuite-mqttintegrator
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT integrator
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-client-websocket \
           +snode.c-net-in-stream-legacy \
           +snode.c-net-in6-stream-legacy \
           +snode.c-net-in-stream-tls \
           +snode.c-net-in6-stream-tls \
           +snode.c-net-un-stream-legacy \
           +snode.c-net-un-stream-tls
endef

define Package/mqttsuite-mqttintegrator/description
  JSON-mapping driven MQTT integrator. Includes mapping plugin libraries.
endef

define Package/mqttsuite-mqttintegrator/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttintegrator $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-integrator.so.* $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-mapping-plugin-storage.so $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-mapping-plugin-double.so  $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttintegrator.init $(1)/etc/init.d/mqttintegrator
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- mqttsuite-mqttbridge ----------
define Package/mqttsuite-mqttbridge
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT bridge
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-client-websocket \
           +snode.c-net-in-stream-legacy \
           +snode.c-net-in6-stream-legacy \
           +snode.c-net-in-stream-tls \
           +snode.c-net-in6-stream-tls \
           +snode.c-net-un-stream-legacy \
           +snode.c-net-un-stream-tls \
           +snode.c-net-l2-stream-legacy \
           +snode.c-net-l2-stream-tls \
           +snode.c-net-rc-stream-legacy \
           +snode.c-net-rc-stream-tls
endef

define Package/mqttsuite-mqttbridge/description
  Client-side bridge connecting multiple brokers and relaying topics.
endef

define Package/mqttsuite-mqttbridge/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqttbridge $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-bridge.so.* $(1)/usr/lib/ 2>/dev/null || true
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttbridge.init $(1)/etc/init.d/mqttbridge
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- mqttsuite-mqtt (CLI) ----------
define Package/mqttsuite-mqtt
  $(call Package/mqttsuite/Default)
  TITLE:=MQTT command line client
  DEPENDS:=+mqttsuite \
           +snode.c-mqtt-client-websocket \
           +snode.c-net-in-stream-legacy \
           +snode.c-net-in6-stream-legacy \
           +snode.c-net-in-stream-tls \
           +snode.c-net-in6-stream-tls \
           +snode.c-net-un-stream-legacy \
           +snode.c-net-un-stream-tls
endef

define Package/mqttsuite-mqtt/description
  Simple command-line MQTT client (publish/subscribe) built on SNode.C.
endef

define Package/mqttsuite-mqtt/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/mqtt $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-cli.so.* $(1)/usr/lib/ 2>/dev/null || true
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

# ---------- eval ----------
$(eval $(call BuildPackage,mqttsuite))
$(eval $(call BuildPackage,mqttsuite-mqttbroker))
$(eval $(call BuildPackage,mqttsuite-mqttintegrator))
$(eval $(call BuildPackage,mqttsuite-mqttbridge))
$(eval $(call BuildPackage,mqttsuite-mqtt))
