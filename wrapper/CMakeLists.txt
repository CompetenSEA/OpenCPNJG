cmake_minimum_required(VERSION 3.18)
project(ocpn_min LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_definitions(-DOCPN_MIN_NO_GUI)

# placeholder vendor file list - users should populate with actual OpenCPN sources
file(STRINGS vendor_filelist.cmake OCPN_SRCS)

add_library(ocpn_core STATIC ${OCPN_SRCS})

target_include_directories(ocpn_core PRIVATE ${CMAKE_SOURCE_DIR}/shim)

add_executable(ocpn_min src/main.cpp src/emit_ndjson.cpp src/attr_codec.cpp src/bbox.cpp)
target_link_libraries(ocpn_min PRIVATE ocpn_core)
