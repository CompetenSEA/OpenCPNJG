cmake_minimum_required(VERSION 3.15)
project(opencpn_bridge)
set(CMAKE_CXX_STANDARD 17)

add_library(opencpn_bridge STATIC bridge.cpp)
target_include_directories(opencpn_bridge PUBLIC 
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}/mvt)

find_package(ZLIB REQUIRED)
target_link_libraries(opencpn_bridge PUBLIC ZLIB::ZLIB)

add_executable(mvt_tests mvt/tests.cpp)
target_link_libraries(mvt_tests PRIVATE opencpn_bridge ZLIB::ZLIB)
target_include_directories(mvt_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

enable_testing()
add_test(NAME mvt_tests COMMAND mvt_tests)
project(opencpn_bridge_stub LANGUAGES CXX)

include(FetchContent)
FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.11.1.tar.gz
)
FetchContent_MakeAvailable(pybind11)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# build the python module into the adjacent py/ directory
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../py)

set(SOURCES
  bridge.cpp
)

if(OPB_STUB_ONLY)
  list(APPEND SOURCES
    stub/stub.cpp
  )
endif()

pybind11_add_module(opencpn_bridge MODULE ${SOURCES})

# placeholder for future vendor code option
if(OPB_WITH_OCPN_MINI)
  message(STATUS "OPB_WITH_OCPN_MINI is not implemented; building stub only")
endif()
