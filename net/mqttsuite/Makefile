include $(TOPDIR)/rules.mk

PKG_NAME:=mqttsuite
PKG_VERSION:=0.1
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/SNodeC/mqttsuite
PKG_SOURCE_VERSION:=HEAD

PKG_MAINTAINER:=Volker Christian <me@vchrist.at>

PKG_LICENSE:=GPL-3.0-or-later
PKG_LICENSE_FILES:=LICENSE

PKG_BUILD_PARALLEL:=1

CMAKE_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/mqttsuite
  SECTION:=net
  CATEGORY:=Network
  TITLE:=A very lightweight MQTT-Integration System
  URL:=https://github.com/SNodeC/mqttsuite
  DEPENDS:=+libfmt \
           +snode.c \
           +snode.c-net-in-stream-legacy \
           +snode.c-net-in-stream-tls \
           +snode.c-net-in6-stream-legacy \
           +snode.c-net-in6-stream-tls \
           +snode.c-net-l2-stream-legacy \
           +snode.c-net-l2-stream-tls \
           +snode.c-net-rc-stream-legacy \
           +snode.c-net-rc-stream-tls \
           +snode.c-net-un-stream-legacy \
           +snode.c-net-un-stream-tls \
           +snode.c-http-server-express \
           +snode.c-http-client \
           +snode.c-websocket-server \
           +snode.c-websocket-client \
           +snode.c-mqtt-server-websocket \
           +snode.c-mqtt-client-websocket
endef

define Package/mqttsuite/description
  The MQTT-Suite project consist of the applications mqttbroker,
  mqttintegrator, wsmqttintegrator, mqttbridge and wsmqttbridge
  powered by SNode.C, a single threaded, single tasking framework
  for networking applications written entirely in C++. Due to
  it's little resource usage it is especially usable on resource
  limited systems.
endef

define strip_staging_dir_prefix_from_rpath
	echo "Stripping $(STAGING_DIR) prefix from RPATH of executables and libraries below $(1)"; \
	find $(1) -type f -a -exec file {} \; | \
		sed -n -e 's/^\(.*\):.*ELF.*\(executable\|relocatable\|shared object\).*,.*/\1:\2/p' | \
	( \
		IFS=":"; \
		while read F S; do \
			echo "$$$$F: $$$$S"; \
			b=$$$$(stat -c '%a' $$$$F); \
			cur_rpath="$$$$($(STAGING_DIR_HOST)/bin/patchelf --print-rpath $$$$F)"; \
			new_rpath=""; \
			echo "Current RPATH: $$$$cur_rpath"; \
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
			echo "Final RPATH: $$$$new_rpath"; \
			[ "$$$$new_rpath" = "$$$$cur_rpath" ] || $(STAGING_DIR_HOST)/bin/patchelf --set-rpath "$$$$new_rpath" $$$$F; \
			a=$$$$(stat -c '%a' $$$$F); \
			[ "$$$$a" = "$$$$b" ] || chmod $$$$b $$$$F; \
		done; \
		true; \
	)
	echo "Stripping done"
endef

define Package/mqttsuite/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/* $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/* $(1)/usr/lib/
	find $(1)/usr/lib -name "*.so"  -exec rm {} ";"
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-mapping-plugin-storage.so $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libmqtt-mapping-plugin-double.so $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mqttbroker.init $(1)/etc/init.d/mqttbroker
	$(INSTALL_BIN) ./files/mqttintegrator.init $(1)/etc/init.d/mqttintegrator
	$(INSTALL_DIR) $(1)/var/www
	$(INSTALL_DIR) $(1)/var/www/mqttsuite
	$(INSTALL_DIR) $(1)/var/www/mqttsuite/mqttbroker
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/mqttbroker/html $(1)/var/www/smqttsuite/mqttbroker/
	$(call strip_staging_dir_prefix_from_rpath,$(1)/usr)
endef

$(eval $(call BuildPackage,mqttsuite))
