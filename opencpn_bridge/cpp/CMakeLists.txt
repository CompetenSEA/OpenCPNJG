cmake_minimum_required(VERSION 3.14)
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
