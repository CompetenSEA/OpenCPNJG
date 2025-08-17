cmake_minimum_required(VERSION 3.15)
project(opencpn_bridge LANGUAGES CXX)

include(FetchContent)
FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.11.1.tar.gz
)
FetchContent_MakeAvailable(pybind11)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist)

option(OPB_WITH_OCPN_MINI "Build with ocpn-mini vendor sources" OFF)
option(OPB_STUB_ONLY "Build stub implementation only" OFF)

set(BRIDGE_SOURCES
  bridge.cpp
  pybind.cpp
)

if(OPB_WITH_OCPN_MINI AND NOT OPB_STUB_ONLY)
  file(GLOB_RECURSE OCPN_MINI_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/vendor/ocpn-mini/gui/src/*.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/vendor/ocpn-mini/libs/s52plib/src/*.cpp)
  list(APPEND BRIDGE_SOURCES ${OCPN_MINI_SOURCES})
endif()

pybind11_add_module(opencpn_bridge MODULE ${BRIDGE_SOURCES})

target_include_directories(opencpn_bridge PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}/../opencpn-libs/include
)

if(OPB_WITH_OCPN_MINI AND NOT OPB_STUB_ONLY)
  target_include_directories(opencpn_bridge PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/vendor/ocpn-mini
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/vendor/ocpn-mini/libs/s52plib/src
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/vendor/ocpn-mini/gui/src
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/ocpn_shim)
  target_compile_options(opencpn_bridge PRIVATE
    -include ${CMAKE_CURRENT_SOURCE_DIR}/cpp/ocpn_shim/wx_shim.h)
endif()
