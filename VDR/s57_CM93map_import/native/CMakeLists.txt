cmake_minimum_required(VERSION 3.18)
project(ocpn_min LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_definitions(-DOCPN_NO_GUI -DOCPN_NO_GL -DOCPN_NO_SENC)

file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/../vendor/vendor_filelist.cmake" OCPN_SRCS)

add_library(opencpn_subset STATIC ${OCPN_SRCS})

target_include_directories(opencpn_subset PRIVATE
  ${CMAKE_CURRENT_LIST_DIR}/../vendor/shims
  ${CMAKE_CURRENT_LIST_DIR}/../vendor/opencpn_subset/src
)

add_executable(ocpn_min
  ${CMAKE_CURRENT_LIST_DIR}/src/main.cpp
  ${CMAKE_CURRENT_LIST_DIR}/src/emit_stub.cpp)

target_link_libraries(ocpn_min PRIVATE opencpn_subset)
