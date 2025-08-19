cmake_minimum_required(VERSION 3.18)
project(ocpn_min LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_definitions(-DOCPN_MIN_NO_GUI)

#
# Vendor OpenCPN sources
# The list is generated via the discovery script described in the project
# documentation.  Each entry is relative to the OpenCPN repository root.
#
file(STRINGS vendor_filelist.cmake OCPN_SRCS)

find_package(ZLIB REQUIRED)

add_library(ocpn_core STATIC ${OCPN_SRCS})

target_include_directories(ocpn_core PRIVATE
    ${CMAKE_SOURCE_DIR}/shim
    ${CMAKE_SOURCE_DIR}/..
    ${CMAKE_SOURCE_DIR}/../include
    ${CMAKE_SOURCE_DIR}/../gui/include
    ${CMAKE_SOURCE_DIR}/../libs/iso8211/src
    ${CMAKE_SOURCE_DIR}/../libs/iso8211/include
    ${CMAKE_SOURCE_DIR}/../libs/s57-charts/include
    ${CMAKE_SOURCE_DIR}/../libs/s57-charts/src
    )

add_executable(ocpn_min
    src/main.cpp
    src/emit_ndjson.cpp
    src/attr_codec.cpp
    src/bbox.cpp)

target_include_directories(ocpn_min PRIVATE ${CMAKE_SOURCE_DIR}/shim)
target_link_libraries(ocpn_min PRIVATE ocpn_core ZLIB::ZLIB)

