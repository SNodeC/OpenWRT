# Release policy layered on each project's authoritative CPack component model.
set(CPACK_DEB_COMPONENT_INSTALL ON)
set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE arm64)
set(CPACK_DEBIAN_PACKAGE_BREAKS "${CPACK_PACKAGE_NAME} (<< ${CPACK_PACKAGE_VERSION})")
set(CPACK_DEBIAN_PACKAGE_REPLACES "${CPACK_PACKAGE_NAME} (<< ${CPACK_PACKAGE_VERSION})")
set(CPACK_PRE_BUILD_SCRIPTS "${CMAKE_CURRENT_LIST_DIR}/debian-dependencies.cmake")
if(CPACK_PACKAGE_NAME STREQUAL "snodec")
    set(CPACK_DEBIAN_CORE_PACKAGE_DEPENDS adduser)
    set(CPACK_DEBIAN_CORE_PACKAGE_CONTROL_EXTRA "${CMAKE_CURRENT_LIST_DIR}/debian/postinst")
endif()

# Keep the existing full-install names as dependency-only packages. Derive their
# dependencies and the publication inventory from CPack, not a second file list.
set(names "${CPACK_PACKAGE_NAME}\n")
set(depends "")
foreach(component IN LISTS CPACK_COMPONENTS_ALL)
    string(TOLOWER "${CPACK_PACKAGE_NAME}-${component}" name)
    string(APPEND names "${name}\n")
    list(APPEND depends "${name} (= ${CPACK_PACKAGE_VERSION})")
endforeach()
list(JOIN depends ", " depends)
file(MAKE_DIRECTORY "${COMPONENT_OUTPUT}")
file(WRITE "${COMPONENT_OUTPUT}/${CPACK_PACKAGE_NAME}.packages" "${names}")
set(meta "${COMPONENT_OUTPUT}/.meta-${CPACK_PACKAGE_NAME}")
file(MAKE_DIRECTORY "${meta}/DEBIAN")
file(WRITE "${meta}/DEBIAN/control"
    "Package: ${CPACK_PACKAGE_NAME}\nVersion: ${CPACK_PACKAGE_VERSION}\nArchitecture: arm64\nMaintainer: ${CPACK_PACKAGE_CONTACT}\nDepends: ${depends}\nDescription: All ${CPACK_PACKAGE_NAME} components\n")
execute_process(COMMAND dpkg-deb --build --root-owner-group "${meta}"
    "${COMPONENT_OUTPUT}/${CPACK_PACKAGE_NAME}_${CPACK_PACKAGE_VERSION}_arm64.deb"
    COMMAND_ERROR_IS_FATAL ANY)
file(REMOVE_RECURSE "${meta}")
