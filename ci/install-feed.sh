#!/bin/sh
# Run explicitly on an OpenWrt router; CI never invokes this on owned devices.
set -eu
. /etc/openwrt_release
series=${DISTRIB_RELEASE%.*}
case "$series" in 24.10|25.12) ;; *) echo "Unsupported OpenWrt release: $DISTRIB_RELEASE" >&2; exit 1 ;; esac
case "$DISTRIB_ARCH" in ''|*[!a-zA-Z0-9_-]*) echo 'Invalid package architecture' >&2; exit 1 ;; esac
base=https://raw.githubusercontent.com/SNodeC/OpenWRT/packages
url=$base/releases/$series/$DISTRIB_ARCH
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT HUP INT TERM
# Fail before changing router configuration if this platform has no published feed.
wget -q -O "$temporary/build.json" "$url/build.json"
if [ "$series" = 24.10 ]; then
    wget -q -O "$temporary/key.pub" "$base/keys/snodec-usign.pub"
    opkg-key add "$temporary/key.pub"
    touch /etc/opkg/customfeeds.conf
    sed -i '/^src\/gz snodec /d' /etc/opkg/customfeeds.conf
    printf 'src/gz snodec %s\n' "$url" >> /etc/opkg/customfeeds.conf
    opkg update
    opkg install mqttsuite-full snode.c-full snode.c-apps snode.c-control
else
    wget -q -O "$temporary/key.pem" "$base/keys/snodec-apk.pem"
    cp "$temporary/key.pem" /etc/apk/keys/snodec-apk.pem
    printf '%s/packages.adb\n' "$url" > /etc/apk/repositories.d/snodec.list
    apk update
    apk add mqttsuite-full snode.c-full snode.c-apps snode.c-control
fi
