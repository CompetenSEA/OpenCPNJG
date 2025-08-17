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
option(OPB_STUB_ONLY "Build stub implementation only" ON)

if(OPB_STUB_ONLY)
  pybind11_add_module(opencpn_bridge MODULE cpp/stub/bridge_stub.cpp)
elseif(OPB_WITH_OCPN_MINI)
  message(STATUS "OPB_WITH_OCPN_MINI is not implemented; building stub only")
endif()
