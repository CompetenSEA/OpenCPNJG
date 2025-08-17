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

pybind11_add_module(opencpn_bridge MODULE
  bridge.cpp
  pybind.cpp
)

target_include_directories(opencpn_bridge PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}/s52plib/src
  ${CMAKE_CURRENT_SOURCE_DIR}/../opencpn-libs/include
)
